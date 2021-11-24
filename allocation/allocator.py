
###############################################################################################

'''This file contains the main logic for order allocations.'''

###############################################################################################


from copy import deepcopy
from datetime import datetime
from math import  floor, sqrt
from numpy import append, argsort, array, full, float32
from scipy.stats import norm

from allocation.constants import *
from allocation.evaluation import Evaluation_Model
from database.constants import NODE_TYPE
from dstrbntw.constants import ACCEPTING_ORDERS
from dstrbntw.delivery import Delivery
from dstrbntw.region import Node
from dstrbntw.region import Region
from parameters import ALLOC_START_TIME, ALLOC_OPERATOR, END_OF_TOURS, MAX_PAL_VOLUME, OP_CAPACITY, OP_END_TIME, RPL_CYCLE_DURATION
from protocols.constants import ALLOC_ARR, ALLOCATION_DATETIME, BEST_OBJ_VALUE, ITER, NUMBER_OF_ORDERS, REGION_ID, RETRY, SAMEDAY_DELIVERY
from transactions.orders import Order
from transactions.sales import Sale
from utilities.datetime import time_diff


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

        return full(len(self.orders.list), STOCK_NOT_AVAILABLE, dtype=int)

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
   
    def node_available(self, node_index:int) -> bool:

        '''Returns True or False depending if the node is currently accepting orders.'''

        # check if node is currently accepting orders
        return self.nodes.__getattr__(ACCEPTING_ORDERS, index=node_index)

    def order_deliverable(self, order:Order, node_index:int) -> Delivery:
        
        ''' Adds an order to the duration matrix of the node's delivery tour. 
            Apporximates tour duration.
            Schedules delivery and order processing. 
            Returns a prototype tour if the order is deliverable. Else returns None.'''

        if node_index >= 0:

            # check availablity of delivery capacities. Copy current tour and prototype routes after having added the new order.
            delivery = self.nodes.__getattr__(DELIVERY, index=node_index) #type: Delivery

            #check if order is already allocated at node
            if order in delivery.orders_to_deliver:
                # order is already in delivery tour, optimize tour only
                prototype_delivery = delivery
            
            else:

                # create copy and create test tour and add order to it
                prototype_delivery = deepcopy(delivery) # type: Delivery
                prototype_delivery.add_order(order)

            # optimize routes
            prototype_delivery.build_routes()

            # check if prototype tour end before end of tours
            if  prototype_delivery.approx_delivery_end(self.current_time, OP_CAPACITY[self.nodes.__getattr__(NODE_TYPE, index=node_index)]) \
                <=  datetime.combine(self.current_time.date(), END_OF_TOURS):
                
                return prototype_delivery 
            
            else:
                return None
        
        else:
            return None

    def determine_candidates(self, order:Order) -> list:

        ''' Returns a list of candidate nodes for a certain order 
            based on if the node is available and it holds the required stock.'''

        candidates = []
        nodes_accepting_orders = self.nodes.accepting_orders

        for node in nodes_accepting_orders:

            if self.stock_available(order, node.index):
                candidates.append(node)

        return candidates

    def reserve_stock(self, order:Order, node_index:int):

        '''Reserves the amount of stock demanded in order.'''

        for line in order.lines:
            line:Order.Line
            
            self.stock.reserve(line.article.index, node_index, line.quantity)

    def cancel_stock_reservation(self, order:Order, node_index:int):

        '''Cancels the reservation for the quantity demanded in order.'''

        for line in order.lines:
            line:Order.Line
            
            self.stock.cancel_reservation(line.article.index, node_index, line.quantity)

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
                
                    return ALLOCATABLE
                else:
                    # delivery restrictions not met
                    return DELIVERY_NOT_EXECUTABLE

            else:
                # stock not available
                return STOCK_NOT_AVAILABLE

        else:
            # node not available
            return NO_NODES_AVAILABLE
            
    def allocate(self, order:Order, node_index:int) -> None:

        '''Allocates order to node.'''

        # set allocation
        order.allocated_node = self.nodes.__get__(index=node_index)
        order.allocation_time = self.current_time

        # reduce available stock
        self.reserve_stock(order, node_index)
        
        # creae batches if there is more than 1 order to deliver
        if len(order.allocated_node.delivery.orders_to_deliver) >= 1:
        
            # schedule tour and its order processing
            order.allocated_node.delivery.create_batches(self.current_time)

    def deallocate(self, order:Order, node_index:int) -> None:

        '''Dellocates order from node.'''

        order.allocated_node.delivery.remove_order(order)
            
        # rebuild delivery routes if there is orders remaining to deliver
        if len(order.allocated_node.delivery.orders_to_deliver) > 0:
        
            # reschedule delivery to get the correct delivery times of the new route 
            # without the order that could not be processed
            order.allocated_node.delivery.build_routes()
            order.allocated_node.delivery.create_batches(self.current_time)
            
        else:
            # reset delivery if there is no order left to deliver 
            order.allocated_node.reset_delivery()
        
        order.allocated_node = None
        order.allocation_time = None

        # reduce available stock
        self.cancel_stock_reservation(order, node_index)

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

    # _______________ Support Methods __________________________________________________________________

    def days_since_last_replenishment(self, node_type:int) -> float:
        
        ''' Support method for Dynamic1.
            Returns the number in days since the last replenishment as floating point value.'''
        
        shops_open = datetime.combine(self.current_time.date(), ALLOC_START_TIME)
        full_days_since_replenishment = self.current_time.date().isoweekday() % RPL_CYCLE_DURATION
        open_minutes_current_day = time_diff(shops_open, self.current_time) 
        shops_close = datetime.combine(self.current_time.date(), OP_END_TIME[node_type])

        return full_days_since_replenishment + (open_minutes_current_day / time_diff(shops_open, shops_close))

    def days_until_next_replenishment(self, node_type:int) -> float:
        
        ''' Support method for Dynamic1.
            Returns the remaining number in days until the next replenishment as floating point value.'''
        
        shops_open = datetime.combine(self.current_time.date(), ALLOC_START_TIME)
        shops_close = datetime.combine(self.current_time.date(), OP_END_TIME[node_type])
        full_days_until_replenishment = self.current_time.date().isoweekday() % RPL_CYCLE_DURATION
        left_minutes_open_current_day = time_diff(shops_close, self.current_time) 

        return full_days_until_replenishment + (left_minutes_open_current_day / time_diff(shops_open, shops_close))

    def expected_stock_level_at_end_of_rpm_cyle(self, article_index:int, node_index:int, days_since_rplm:float) -> int:

        ''' Support method for Dynamic1.
            Returns the expected stock level for a certain article at the end 
            of the replenishment cycle == before replenishment.'''

        return     (self.stock.current_level[article_index, node_index] \
                -  self.stock.reserved[article_index, node_index]) \
                -  RPL_CYCLE_DURATION * self.demand.__getattr__("avg", article_index, node_index) * (floor(days_since_rplm) - days_since_rplm + 1) \
                / sqrt(self.demand.__getattr__("var", article_index, node_index) * (floor(days_since_rplm) - days_since_rplm + 1))  

    def reduction_in_stock_holding_costs(self, node:Node, current_stock_level:int, stock_level_at_end_of_rpm_cyle, days_until_next_rplm:float) -> int:

        ''' Support method for Dynamic1.
            Returns the reduction of the stock holding costs resulting from the evaluated allocation.'''

        return (current_stock_level - stock_level_at_end_of_rpm_cyle) * days_until_next_rplm * node.stock_holding_rate
    
    def delivery_costs(self, order:Order, node:Node) -> float:

        '''Returns the delivery costs if the order is allocated at the examined node.'''

        prototype_delivery = deepcopy(node.delivery) #type:Delivery
        prototype_delivery.add_order(order)
        prototype_delivery.build_routes()
        
        return  (prototype_delivery.tot_duration * node.route_rate) \
              + (node.tour_rate if len(node.delivery.orders_to_deliver) == 0 else 0)

    def delivery_costs_of_detour(self, order:Order, node:Node) -> float:

        '''Returns the delivery costs of detour if the order is allocated at the examined node.'''

        prototype_delivery = deepcopy(node.delivery) #type:Delivery
        prototype_delivery.add_order(order)
        prototype_delivery.build_routes()
        
        return  (prototype_delivery.tot_duration * node.route_rate) \
              - (node.delivery.tot_duration * node.route_rate) \
              + (node.tour_rate if len(node.delivery.orders_to_deliver) == 0 else 0)

    def order_processing_costs(self, order:Order, node:Node) -> float:

        ''' Support method for Modified_Dynamic_1.
            Retunrs the expected  order_processing_costs of processing order at node.'''

        return order.number_of_lines * node.order_processing_rate

    def supply_costs(self, order:Order, node:Node) -> float:

        ''' Support method for Modified_Dynamic_1.
            Retunrs the expected supply of processing allocating order at node.'''

        return (order.volume / MAX_PAL_VOLUME) * node.supply_rate

    def marginal_fulfillment_costs(self, order:Order, node:Node):
        
        ''' Support method for Dynamic1.
            Returns marginal holding and backorder costs of maintaining 
            one additional unit of article article_index at node node_index.'''

        marg_holding_and_backorder_costs = []
        days_since_rplm = self.days_since_last_replenishment(node.node_type)

        for line in order.lines:
            line:Order.Line

            # calculate cumulative distribution function for the expected stock at the end of the replenishment cycle
            cdf = norm.cdf(self.expected_stock_level_at_end_of_rpm_cyle(line.article.index, node.index, days_since_rplm))

            # calculate and append marginal costs
            marg_holding_and_backorder_costs.append(node.stock_holding_rate * cdf - node.supply_rate * (1 - cdf))

        return ALLOC_OPERATOR(marg_holding_and_backorder_costs) + self.order_processing_costs(order, node) + self.delivery_costs_of_detour(order, node)

    def marginal_allocation_costs(self, order:Order, node:Node):
        
        ''' Support method for Modified_Dynamic_1.
            Returns marginal holding and backorder costs of maintaining 
            one additional unit of article article_index at node node_index.'''

        marg_holding_and_backorder_costs = []
        days_since_rplm = self.days_since_last_replenishment(node.node_type)

        for line in order.lines:
            line:Order.Line

            # calculate cumulative distribution function for the expected stock at the end of the replenishment cycle
            cdf = norm.cdf(self.expected_stock_level_at_end_of_rpm_cyle(line.article.index, node.index, days_since_rplm))

            # calculate and append marginal costs
            marg_holding_and_backorder_costs.append(node.stock_holding_rate * cdf - node.supply_rate * (1 - cdf))

        return    self.delivery_costs(order, node) - ALLOC_OPERATOR(marg_holding_and_backorder_costs)





