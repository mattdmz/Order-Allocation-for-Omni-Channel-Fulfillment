
###############################################################################################

'''This file contains the base class for all allocation rules.'''

###############################################################################################


from copy import deepcopy
from datetime import datetime
from math import  floor, sqrt
from numpy import append, argsort, array
from typing import Tuple
from scipy.stats import norm

from allocation.allocator import Allocator
from database.constants import DATE_TIME
from dstrbntw.region import Region
from dstrbntw.region import Node
from dstrbntw.delivery import Delivery
from parameters import ALLOC_START_TIME, ALLOC_OPERATOR, MAX_PAL_VOLUME, OP_END_TIME, RPL_CYCLE_DURATION
from transactions.sales import Sale
from transactions.orders import Order
from utilities.datetime import time_diff

class Rule(Allocator):

    '''Parent class with allocation logic for all allocation rules.'''

    def __init__(self, region:Region, current_time:datetime, main)-> None:

        ''' Creates a chronological list of orders and sales to process.
            Allocates orders rule based.
            Prepares evaluation.
            Stores allocation. '''

        super().__init__(region, current_time)

        # store main method of child class
        self.main = main

        # get a created a list of order and sale ids based on its date_time
        self.chron_trnsct_list = self.create_chron_trnsct_list()

        allocation, revenue,  diminuished_stock_value = self.allocate_rule_based()
        self.sales.store_results(revenue, diminuished_stock_value)
        self.prepare_evaluation()
        self.store_allocation(self.evaluate(allocation))

    def create_array(self, transactions:list, attr:str=None) -> array:

        '''Returns a np_array with all transactions or a specific attr of them.'''

        return array(list(getattr(trnsct, attr) if attr is not None else trnsct for trnsct in transactions)) 

    def create_chron_trnsct_list(self) -> array:
    
        '''Returns an np array with the a list of sorted transactions (orders, sales) based on date_time.'''

        # carry out function only if there is sales. Else return orders as shops are currently closed
        if len(self.sales.list) > 0:
            
            trnsct_arr = self.create_array(self.orders.list)
            trnsct_arr = append(trnsct_arr, self.create_array(self.sales.list))

            date_time_arr = self.create_array(self.orders.list, DATE_TIME)
            date_time_arr = append(date_time_arr, self.create_array(self.sales.list, DATE_TIME))

            return trnsct_arr[argsort(date_time_arr)]
        
        else:
            return self.orders.list

    def apply(self, order:Order) -> int:

        ''' Applies the rule stored in self.alloc_func.
            Returns the node_index if allocation was successfull, else it returns -1
            Replaces delivery tour if allocation was successfull.'''

        best_feedback = -1000

        # get a ranking of node indexes based on the ALLOC_METHOD and ALLOC_FUNC defined in the parameters.
        ranked_nodes = self.main(order)

        # try to allocate order. Start with node index ranked 1st.
        for node_index in ranked_nodes:
            node_index:int

            feedback = self.allocatable(order, node_index)

            if feedback > 0:

                # order allocatable
                return node_index
            
            elif feedback > best_feedback:
                best_feedback = feedback
            
        # return the best feedback
        return best_feedback

    def allocate_rule_based(self) -> Tuple[array, float, int]:

        ''' Tries to close all sales and collects their revenue and the diminuished stock value.
            Assigns orders based on the rule set in parameters.'''

        # init index to store the node_id for the order allocation
        index = 0
        allocation =  self.init_allocation_array()
        revenue = 0
        diminuished_stock_value = 0

        # transactions (sales, orders) must be handled follwinging the order of their occurrence in time
        for trnsct in self.chron_trnsct_list:

            # handle sales and allocate order sbased on rule
            if isinstance(trnsct, Sale):
                
                #try to close the sale, collect the revenue and the number of pieces sold and protocol lines which could not be closed
                rev, pieces_sold = self.sell(trnsct)

                if rev > 0:
                    revenue += rev
                    diminuished_stock_value += trnsct.node.stock_holding_rate * pieces_sold
            
            else: # order
                
                # allocate order based on method apply of the rule initialized
                allocation[index] = self.apply(trnsct)
                
                # check if a valid node index was returned for allocation
                if allocation[index] >= 0:
                    self.allocate(trnsct, allocation[index])

                index += 1
                rev = 0
                pieces_sold = 0     

        return allocation, revenue, diminuished_stock_value

    # _______________ Support Methods for rules __________________________________________________________________

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
              - (node.delivery.tot_duration * node.route_rate) \
              + (node.tour_rate if len(node.delivery.batches) == 0 else 0)

    def order_processing_costs(self, order:Order, node:Node) -> float:

        ''' Support method for Modified_Dynamic_1.
            Retunrs the expected  order_processing_costs of processing order at node.'''

        return order.number_of_lines * node.order_processing_rate

    def supply_costs(self, order:Order, node:Node) -> float:

        ''' Support method for Modified_Dynamic_1.
            Retunrs the expected supply of processing allocating order at node.'''

        return (order.volume / MAX_PAL_VOLUME) * node.supply_rate

    def marginal_costs(self, order:Order, node:Node):
        
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

        return ALLOC_OPERATOR(marg_holding_and_backorder_costs) + self.order_processing_costs(order, node) + self.delivery_costs(order, node)

    def expected_costs(self, order:Order, node:Node):
        
        ''' Support method for Modified_Dynamic_1.
            Returns marginal holding and backorder costs of maintaining 
            one additional unit of article article_index at node node_index.'''

        reduction_in_stock_holding_costs = []
        days_until_rplm = self.days_until_next_replenishment(node.node_type)

        for line in order.lines:
            line:Order.Line

            expected_stock_level_at_rplm_time = self.expected_stock_level_at_end_of_rpm_cyle(line.article.index, node.index, days_until_rplm)
            current_stock_level = self.stock.current_level[line.article.index, node.index]
            reduction_in_stock_holding_costs.append(self.reduction_in_stock_holding_costs(node, current_stock_level, expected_stock_level_at_rplm_time, days_until_rplm))

        return    self.supply_costs(order, node) + sum(reduction_in_stock_holding_costs) \
                + self.order_processing_costs(order, node) + self.delivery_costs(order, node)
