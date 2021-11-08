
###############################################################################################

'''This file contains the class Stock.'''

###############################################################################################

from datetime import datetime
from math import ceil, sqrt
from numpy import array, copy, empty, sum, where, zeros_like
from numpy.random import randint
from scipy.stats import norm

from dstrbntw.constants import *
from dstrbntw.demand import Demand
from parameters import FIX_LEVEL, PLANED_STOCK_DURATION, RPL_CYCLE_DURATION, STOCK_BETA_SERVICE_DEGREE, STOCK_SEED, SUBTRACT_EXPECTED_STOCK_DEMAND
from transactions.orders import Order
from utilities.expdata import write_numpy_array

class Stock():

    ''' Stock of a region. Dispo rule used: (T, s, S)-Rule 
        (control inteval = 1 day, s = reorder level, S = target level).'''

    def __init__(self, empty_arr:array, holding_rates:list, demand:Demand):

        ''' Inits stock for all nodes of a region.'''

        #store demand
        self.demand = demand

        #int empty arrays
        self.reorder_level = copy(empty_arr)
        self.target_level = copy(empty_arr)
        self.reserved = copy(empty_arr)
        self.current_level = None
        
        self.holding_rates = array(holding_rates)

    @property
    def holding_costs(self) -> float:

        '''Returns stock holding costs for 1 day for all nodes of the region.'''

        return sum(sum(self.current_level, axis=0) * self.holding_rates)

    def calc_reorder_level(self, avg_daily_demand:float, variance_demand:float, ppf:float) -> int:

        '''Returns the stock level for an article at a node, at which a replenishment is carried out.'''

        return int(ceil(RPL_CYCLE_DURATION * avg_daily_demand + ppf * sqrt(RPL_CYCLE_DURATION * variance_demand)))

    def calc_target_level(self, avg_daily_demand:float, variance_demand:float, ppf:float, abc_category:str) -> int:

        '''Returns the max. stock quantity an article at a node should have after replenishment.'''
        
        duration = RPL_CYCLE_DURATION + PLANED_STOCK_DURATION[abc_category]
        return int(ceil(duration * avg_daily_demand + ppf * sqrt((duration) * variance_demand)))

    def set_fix_stock_level(self) -> array:

        '''Sets stock type for all nodes to FIX_LEVEL.'''

        #set current level defined in fix parameter
        fix_level = empty(shape=(self.reorder_level.shape), dtype=int)
        fix_level.fill(FIX_LEVEL) 
        
        return fix_level 

    def set_start_level(self, node_start_stock_rates:list=None, article_start_stock_rates:list=None) -> array:

        '''Returns an array with start level of stock based for each node based on STOCK_SEED parameter.'''

        if STOCK_SEED == RNDM_BTWN_REORDER_AND_TARGET_LEVEL:
            return randint(self.reorder_level, self.target_level)
        
        elif STOCK_SEED == TARGET_LEVEL:
            return copy(self.target_level)

        elif STOCK_SEED == PREDEFINED_LEVEL: # set between 70% and 100% of the target level for each element
            return self.target_level * (array(node_start_stock_rates) + array(article_start_stock_rates))

        else: # FIX_LEVEL
            return self.set_fix_stock_level()

    def set_calculated_dispo_levels(self, article_index:int, node_index:int, abc_category:str) -> None:

        ''' Calculates and sets reorder and start level stock of each each article to be listed at each node.
            Determines and sets also start level of stock.'''

        avg_daily_demand =  self.demand.avg[article_index, node_index]
        variance_demand = self.demand.var[article_index, node_index]
        ppf = norm.ppf(STOCK_BETA_SERVICE_DEGREE[abc_category], loc=0, scale=1)
        
        self.reorder_level[article_index, node_index] = self.calc_reorder_level(avg_daily_demand, variance_demand, ppf)
        target_level = self.calc_target_level(avg_daily_demand, variance_demand, ppf, abc_category)
        self.target_level[article_index, node_index] = target_level if target_level > self.reorder_level[article_index, node_index] else self.reorder_level[article_index, node_index] + 1

    def availability(self, article_index:int, node_index:int, quantity_demanded:int, current_time:datetime, op_end_time:datetime) -> bool:

        ''' Returns True if current stock - reserved stock level allows to serve the quantity_demanded, else returns False.'''
        
        #print("current: ", self.current_level[article_index, node_index], ", reserved: ", self.reserved[article_index, node_index], ", quantity_demanded: ", quantity_demanded)
        
        return     self.current_level[article_index, node_index] - self.reserved[article_index, node_index] \
                - (self.demand.expected(article_index, node_index, current_time, op_end_time) if SUBTRACT_EXPECTED_STOCK_DEMAND else 0) \
                -  quantity_demanded >= 0
    
    def reserve(self, article_index:int, node_index:int, quantity:int) -> None:

        '''Reserves stock of a certain article at a certain node by the quantity.'''

        self.reserved[article_index, node_index] += quantity   

    def processability(self, article_index:int, node_index:int, quantity_demanded:int) -> bool:

        ''' Returns True if current stock is actually available, else returns False.'''

        return self.current_level[article_index, node_index] - quantity_demanded >= 0

    def cancel_reservation(self, article_index:int, node_index:int, quantity:int) -> None:

        ''' Cancels reservation for a certain article at a certain node by the quantity ordered.'''

        self.reserved[article_index, node_index] -= quantity

    def consume(self, article_index:int, node_index:int, quantity:int) -> None:

        ''' Reduces stock of a certain article at a certain node by the quantity ordered.'''

        self.current_level[article_index, node_index] -= quantity

    def demanded(self, orders:list) -> array:

        ''' Returns a 1D array with the quantity of stock demanded at the allocated nodes.'''

        stock_demanded = zeros_like(self.current_level)

        for order in orders:
            order:Order

            if order.allocated_node != None:

                for line in order.lines:
                    line:Order.Line

                    stock_demanded[line.article.index, order.allocated_node.index] = line.quantity

        return stock_demanded

    def add(self, article_index:int, node_index:int, quantity:int)-> None:

        '''Adds stock of a certain article at a certain node by the quantity.'''

        self.current_level[article_index, node_index] += quantity

    def replenish(self) -> int:

        '''Replenishes stock to target level if it fell below the reorder level and returns the number of replenishments.'''
        
        replenishments = sum(self.current_level - self.reserved < self.reorder_level)
        self.current_level = where(self.current_level - self.reserved < self.reorder_level, self.target_level, self.current_level)

        return replenishments

    def export(self, region_id:int)-> None:

        ''' Exports stock levels.'''

        #exp data
        write_numpy_array(self.reorder_level, REORDER_STOCK_LEVEL + "_" + str(region_id))
        write_numpy_array(self.target_level, TARGET_STOCK_LEVEL + "_" + str(region_id))
        write_numpy_array(self.current_level, CURRENT_STOCK_LEVEL + "_" + str(region_id))
