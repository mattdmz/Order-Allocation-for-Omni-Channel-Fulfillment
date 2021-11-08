
###############################################################################################

'''This file contains the main logic for order allocations.'''

###############################################################################################


from copy import deepcopy
from datetime import datetime
from numpy import array, full, float32

from allocation.constants import *
from allocation.evaluation import Evaluation_Model
from database.constants import NODE_TYPE
from dstrbntw.constants import ACCEPTING_ORDERS
from dstrbntw.region import Region
from dstrbntw.delivery import Delivery
from protocols.constants import ALLOC_ARR, ALLOCATION_DATETIME, BEST_OBJ_VALUE, ITER, NUMBER_OF_ORDERS, REGION_ID, RETRY, SAMEDAY_DELIVERY
from transactions.orders import Order
from transactions.sales import Sale
from parameters import OP_END_TIME

class Allocator:

    '''Parent class for all allocators (rules and optimizers).'''

    def __init__(self, region:Region, current_time:datetime) -> None:

        '''Stores region-model objects and inits DatFrame to store allocations.'''

        # store model data
        self.region_id = region.id
        self.current_time = current_time
        self.articles = region.articles
        self.customers = region.customers
        self.demand = region.demand
        self.nodes = region.nodes
        self.orders = region.orders
        self.sales = region.sales
        self.stock = region.stock
        self.evaluation_model = Evaluation_Model(self.sales, self.orders, self.stock.holding_rates, self.nodes.tour_rates, self.nodes.route_rates)

        # init allocation attribute
        self.allocation = None

    def init_allocation_array(self) -> array:

        ''' Returns an np_array with the length of the number of orders to allocate.'''

        return full(len(self.orders.list), -10, dtype=int)

    def update_allocation_based_rates(self, allocation:array, rate_type:str) -> array:

        '''Returns an array of rates of type "rate_type" based on the node_type of allocated node.'''

        return array(list(rate_type[self.nodes.__getattr__(node_index, NODE_TYPE)] for node_index in allocation), dtype=float32)

    def stock_available(self, order:Order, node_index:int)-> bool:

        '''Returns True if stock is available to serve all orderlines, else returns False.'''
        
        availability = True
        
        for line in order.lines:
            line:Order.Line
            
            availability = self.stock.availability(line.article.index, node_index, line.quantity, self.current_time, 
                            datetime.combine(self.current_time.date(), OP_END_TIME[self.nodes.__getattr__(NODE_TYPE, index=node_index)]))
            if not availability:
                break
        
        return availability

    def reserve_stock(self, order:Order, node_index:int):

        '''Reserves the amoutn of stock demanded in order.'''

        for line in order.lines:
            line:Order.Line
            
            self.stock.reserve(line.article.index, node_index, line.quantity)

    def sell(self, sale:Sale) -> float:

        ''' Sets True or False if each saleline of the saleline can be closed or not 
            depending if stock is available to satisfy the demanded quantity of each saleline.
            If stock is available, the demanded quantity is consumed and returned and the realized revenue 
            is collected for each saleline.'''

        revenue = 0
        pieces_sold = 0

        # check if there is enough stock available
        for line in sale.lines:
            line:Sale.Line
            
            if self.stock.processability(line.article.index, sale.node.index, line.quantity):
                
                # consume demanded stock
                self.stock.consume(line.article.index, sale.node.index, line.quantity)

                # collect revenue from saleline
                line.closed = True
                revenue += line.article.price * line.quantity
                pieces_sold += line.quantity

        return revenue, pieces_sold
            
    def node_available(self, node_index:int) -> bool:

        '''Returns True or False depending if the node is currently accepting orders.'''

        # check if node is currently accepting orders
        return self.nodes.__getattr__(ACCEPTING_ORDERS, index=node_index)

    def order_deliverable(self, order:Order, node_index:int) -> Delivery:
        
        ''' Adds an order to the duration matrix of the node's delivery tour. 
            Apporximates tour duration.
            Schedules delivery and order processing. 
            Returns a prototype tour if the order is deliverable. Else returns None.'''

        # check availablity of delivery capacities. Copy current tour and prototype routes after having added the new order.
        delivery = self.nodes.__getattr__(DELIVERY, index=node_index) #type: Delivery
        prototype_delivery = deepcopy(delivery)
        prototype_delivery.approximate_routes(prototype_delivery.add_order(order))

        # schedule tour and its order processing
        prototype_delivery.create_batches()

        # check if tour start after current_time to assure allocatability
        order_deliverable = prototype_delivery.on_time(self.current_time)

        return prototype_delivery if order_deliverable else None

    def allocatable(self, order:Order, node_index:int) -> int:
            
        ''' Returns 1 if an order is allocatable at the examined node.
            Else returns feedback on why the order was not allocatable at the examined node.
                -100 --> node not available
                -10  --> stock not available
                -1   --> delivery restrictions not met'''

            # check if node can currently recieve orders
        if self.node_available(node_index):
            
            if self.stock_available(order, node_index):

                # check order deliverability (vehicle volume restrictions, scheduling of order proc and delivery restrictions)
                delivery = self.order_deliverable(order, node_index)

                if delivery is not None:
                    
                    # replace delivery
                    setattr(self.nodes.__get__(index=node_index), DELIVERY, delivery)
                
                    return 1 
                else:
                    # delivery restrictions not met
                    return -1

            else:
                # stock not available
                return -10

        else:
            # node not available
            return -100
            
    def allocate(self, order:Order, node_index:int) -> None:

        '''Allocates order to node.'''

        order.allocated_node = self.nodes.__get__(index=node_index)
        order.allocation_time = self.current_time

        # reduce available stock
        self.reserve_stock(order, node_index)

        # reduce available delivery tour capacity and reschedule delivery batches
        delivery = self.nodes.__getattr__(DELIVERY, index=node_index) #type: Delivery
        
        # builde routes if there is more than 1 order to deliver
        if len(delivery.orders_to_deliver) > 1:
            
            # build routes
            delivery.build_routes(node_type=order.allocated_node.node_type)
        
            # schedule tour and its order processing
            delivery.create_batches()

    def prepare_evaluation(self) -> None:

        ''' Provides allocation based informations to the evaluation model´.
            Methode must be called before evaluating an allocation'''

        self.evaluation_model.prepare(self.orders.allocation_based_supply_costs(), self.orders.allocation_based_processing_costs(), \
                                self.stock.demanded(self.orders.list), self.nodes.tour_durations, self.sales.revenue, self.sales.diminuished_stock_value)

    def evaluate(self, allocation:array, iter:int=1) -> dict:

        '''Returns a dict containing the evaluation of the allocation.'''

        on_retry = sum(order.allocation_retried for order in self.evaluation_model.orders_list)

        return {    ALLOCATION_DATETIME: self.current_time,
                    REGION_ID: self.region_id,
                    ITER: iter,
                    BEST_OBJ_VALUE: self.evaluation_model.objective_function(allocation),
                    NUMBER_OF_ORDERS: len(self.evaluation_model.orders_list) - on_retry,
                    RETRY: on_retry,
                    SAMEDAY_DELIVERY: self.evaluation_model.sameday_delivery(self.current_time),
                    ALLOC_ARR: allocation
                }

    def store_allocation(self, evaluated_allocation:array) -> None:

        '''Stores an allocation in the best allocation list'''

        self.allocation = evaluated_allocation





