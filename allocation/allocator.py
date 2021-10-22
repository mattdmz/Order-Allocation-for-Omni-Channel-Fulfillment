
###############################################################################################

'''This file contains the main logic for order allocations.'''

###############################################################################################


from copy import deepcopy
from datetime import datetime
from numpy import array, full, float32

from allocation.constants import *
from database.constants import NODE_TYPE
from dstrbntw.constants import ACCEPTING_ORDERS, PROC_TIME
from dstrbntw.region import Region
from parameters import MAX_WORKING_TIME
from transactions.orders import Order
from transactions.sales import Sale

class Allocator:

    '''Parent class for all allocators (rules and optimizers).'''

    def __init__(self, region:Region, current_time:datetime, cut_off_time:datetime) -> None:

        '''Stores region-model objects and inits DatFrame to store allocations.'''

        # store model data
        self.region_id = region.id
        self.current_time = current_time
        self.cut_off_time = cut_off_time
        self.articles = region.articles
        self.customers = region.customers
        self.demand = region.demand
        self.nodes = region.nodes
        self.orders = region.orders
        self.sales = region.sales
        self.stock = region.stock
        self.evaluation_model = region.evaluation_model

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
            availability = self.stock.availability(line.article.index, node_index, line.quantity, self.current_time, self.cut_off_time)
            if not availability:
                break
        
        return availability

    def reserve_stock(self, order:Order, node_index:int):

        '''Reserves the amoutn of stock demanded in order.'''

        for line in order.lines:
            self.stock.reserve(line.article.index, node_index, line.quantity)

    def add_stock(self, order:Order, node_index:int):

        '''Adds amount of article demanded in order to stock.'''
        
        for line in order.lines:
            self.stock.add(line.article.index, node_index, line.quantity)

    def sell(self, sale:Sale) -> None:

        '''Returns revenue for each article of sale if stock is available and lines closed.'''

        # check if there is enough stock available
        for line in sale.lines:
            if self.stock.processability(line.article.index, sale.node.index, line.quantity):
                
                #consume demanded stock
                self.stock.consume(line.article.index, sale.node.index, line.quantity)

                # collect revenue from saleline
                line.closed = True

    def node_available(self, node_index:int) -> bool:

        '''Returns True or False depending if the node is currently accepting orders.'''

        # check if node is currently accepting orders
        return self.nodes.__getattr__(ACCEPTING_ORDERS, index=node_index)

    def order_deliverable(self, order:Order, node_index:int) -> object:
        
        ''' Adds an order to the duration matrix of the node's delivery tour. 
            Apporximates tour duration.
            Schedules delivery and order processing. 
            Returns a prototype tour if the order is deliverable. Else returns None.'''

        # check availablity of delivery capacities. Copy current tour and prototype routes after having added the new order.
        tour = self.nodes.__getattr__(TOUR, index=node_index)
        prototype_tour = deepcopy(tour)
        prototype_tour.approximate_routes(prototype_tour.add_order(order))

        # schedule tour and its order processing
        prototype_tour.schedule_batches()

        # check if tour start after current_time to assure allocatability
        order_deliverable = prototype_tour.on_time(self.current_time)

        return prototype_tour if order_deliverable else None

    def prepare_evaluation(self) -> None:

        '''Provides evaluation model with all allocation based infos to evaluate allocation.'''

        self.evaluation_model.supply.replace_rates(array(self.orders.allocation_based_supply_rates))
        self.evaluation_model.order_processing.replace_rates(array(self.orders.allocation_based_processing_rates))
        self.evaluation_model.tours.replace_durations(array(self.nodes.tour_durations))

    def allocate(self, order:Order, node_index:int) -> None:

        '''Allocates order to node.'''

        order.allocation = self.nodes.__get__(index=node_index)

        # reduce available stock
        self.reserve_stock(order, node_index)

        # reduce available delivery tour capacity and reschedule delivery batches
        tour = self.nodes.__getattr__(TOUR, index=node_index)
        
        # builde routes if there is more than 1 order to deliver
        if len(tour.orders_to_deliver) > 1:
            
            #build routes
            tour.build_routes(time_capacity_per_tour=MAX_WORKING_TIME[self.nodes.__getattr__(NODE_TYPE, index=node_index)])
        
            # schedule tour and its order processing
            tour.schedule_batches()

    def punctuality(self) -> float:

        ''' Returns the number of orders that will be deliverd same-day.
            Same-day == the the day the order arrives, if cut_off_time is not yet reached, 
            else same-day == the day the order arrives + 1, if the order arrives after cut_off_time.'''
                           
        return sum(self.orders.delivered_sameday(self.current_time, self.cut_off_time)) / len(self.orders.list)

    def evaluate(self, allocation:array, iter:int=1) -> dict:

        '''Returns a dict containing the evaluation of the allocation.'''

        return {PROC_TIME: self.current_time,
                REGION_ID: self.region_id,
                ITER: iter, 
                OBJ_VALUE: self.evaluation_model.objective_function(allocation),
                PUNCTUALITY: self.punctuality(),
                ALLOC_ARR: allocation
                }

    def store_allocation(self, evaluated_allocation:array) -> None:

        '''Stores an allocation in the best allocation list'''

        self.allocation = evaluated_allocation





