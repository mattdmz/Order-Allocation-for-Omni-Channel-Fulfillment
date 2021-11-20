
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

        # determine candidate nodes for allocating the order
        candidates = self.determine_candidates(order)

        # get a ranking of node indexes based on the ALLOC_METHOD and ALLOC_FUNC defined in the parameters.
        ranked_nodes = self.main(order, candidates)

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