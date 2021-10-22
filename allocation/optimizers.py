
###############################################################################################

'''This file contains all the customized Tabu Search Optimizer.'''

###############################################################################################

from copy import deepcopy
from datetime import datetime
from numpy import array
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from allocation.constants import ABS_IMPRVMNT, ALLOC_ARR, ITER, OPTIMIZER
from allocation.optimizer import Optimizer
from dstrbntw.region import Region


class Tabu_Search(Optimizer):

    ''' Allocates the order to the node with based on a certain calculated criterium.'''

    __type__ = OPTIMIZER

    def __init__(self, region:Region, current_time:datetime, cut_off_time:datetime, operator:str=None) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, cut_off_time, operator, self.main)

    def update_tabu_list(self) -> None:

        

        for tabu in zip(tabu_list[(order_index, best_allocation[order_index])].values(), tabu_drop[(order_index, best_allocation[order_index])].values()):
                            if 

    def main(self, initial_allocation:array, obj_value:float) -> array:

        # set starting values
        best_allocation = deepcopy(initial_allocation)
        best_obj_value = obj_value
        mid_term_memory = DataFrame()
        tabu_add = {}
        tabu_drop = {}
        tabu_add_tenure = 5
        tabu_drop_tenure = 3
        iter = 0
        max_iter = 1000

        while iter <= max_iter:

            neighbourhood = self.Neighbourhood_Generator.random()

            order_indexes, node_indexes, fitness_values = self.evaluate_neighbourhood(neighbourhood, best_allocation)

            for order_index, node_index, fitness in zip(order_indexes, node_indexes, fitness_values):
                
                # check if the swap is not tabu or meets the aspiration criterium
                if (tabu_add[(order_index, best_allocation[order_index])]) or (tabu_drop[(order_index, best_allocation[order_index])]) or (obj_value + fitness > best_obj_value):
                    
                    if self.restrictions_met(node_index, order_index):

                        # update tabu lists
                        tabu_drop[(order_index, best_allocation[order_index])] = iter + tabu_drop_tenure
                        tabu_add[(order_index, best_allocation[order_index])] = iter + tabu_add_tenure

                        # apply change
                        best_allocation[order_index] = node_index

                        # protocol new best_allocation
                        evaluated_alloaction = mid_term_memory.xs({ITER:iter, ALLOC_ARR:deepcopy(best_allocation), ABS_IMPRVMNT:obj_value + fitness})
                        evaluated_alloaction.name = iter

                        # store best allocation in mid term memory
                        mid_term_memory.append(Series({ALLOC_ARR:deepcopy(best_allocation), ABS_IMPRVMNT:obj_value + fitness}, name=iter))

                        # update aspiration criteria
                        best_obj_value = obj_value + fitness

                        # update tabu lists
                        self.update_tabu_list()

                        break

        return best_allocation



    