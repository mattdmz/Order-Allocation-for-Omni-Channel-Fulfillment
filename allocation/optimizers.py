
###############################################################################################

'''This file contains all the customized Tabu Search Optimizer.'''

###############################################################################################

from copy import deepcopy
from datetime import datetime
from numpy import array

from allocation.constants import OPTIMIZER, TABU_ADD, TABU_DROP
from allocation.optimizer import Optimizer
from dstrbntw.region import Region
from protocols.constants import ALLOC_ARR, ITER, OBJ_VALUE

class Tabu_Search(Optimizer):

    ''' Allocates the order to the node with based on a certain calculated criterium.'''

    __type__ = OPTIMIZER

    def __init__(self, region:Region, current_time:datetime, cut_off_time:datetime, operator:str=None) -> None:

        ''' Inits parent class for optimizers and 
            sets parameters for Tabu Search algorithm.
            and runs it'''
        
        super().__init__(region, current_time, cut_off_time, operator, self.main)

        # set parameters
        self.memory_list = []
        self.memory_length = 5
        self.tabu_add_tenure = 5
        self.tabu_drop_tenure = 3
        self.max_iter = 1000
        self.max_iter_since_improvement = 10

    @property
    def best_allocation(self) -> array:

        '''Returns the current best allocation.'''

        return self.memory_list[0][ALLOC_ARR]

    def memorize(self, new_allocation:dict) -> None:

        ''' Adds allocation to memory list and drops the last element
            if the max. length of the memory_list was reached.'''

        # insert new_allocation in sorted order accoring to the objective value in descening mode.
        for index, allocation in enumerate(self.memory_list):
            index:int
            allocation:dict
            
            if allocation[OBJ_VALUE] < new_allocation[OBJ_VALUE]:
                break

        self.memory_list.insert(index, new_allocation)

        # check if the max length of the memory list was reached
        if len(self.memory_list) > self.memory_length:
            
            # dropp element
            del self.memory_list[len(self.memory_list)]

    def memorable(self, new_obj_value:float) -> bool:

        ''' Retunrs True or False depending if the new_allocation is memorable or not.
            Memorable = True if new_obj_value > obj_value of the last element of the memory list'''

        return True if self.memory_list[len(self.memory_list)][OBJ_VALUE] < new_obj_value else False

    def is_tabu(self, tabu_list:dict, order_index:int, node_index:int) -> bool:

        '''Returns True or False depending if the node_index is tabu  '''
        
        try:
            if tabu_list[(order_index, node_index)]:
                return True
        except IndexError:
                return False

    def update_tabu_list(self, tabu_list:dict, tabu_tenure:int, order_index:int, node_index:int, iter:int) -> None:

        ''' Adds move to tabu list and 
            removes moves from tabu list which are not valid anymore.'''

        tabu_list[(order_index, node_index)] = iter + tabu_tenure

        for key, tabu_stop_iter in tabu_list.items():
            if iter > tabu_stop_iter:
                del tabu_list[key]

    def main(self, initial_allocation:array, obj_value:float) -> array:

        '''Runs the Tabu Search Algorithm on the initial_allocation.'''

        # set starting values
        iter = 0
        restart_trial = 0
        tabu_add = {}                  # format tabu_add[(order_index, node_index)]: iteration the tabu ends(iter + tabu_add_tenure)
        tabu_drop = {}                 # format tabu_add[(order_index, node_index)]: iteration the tabu ends(iter + tabu_drop_tenure)
        best_allocation = deepcopy(initial_allocation)
        new_allocation = deepcopy(initial_allocation)
        best_obj_value = obj_value

        while iter <= self.max_iter:

            # generate neighbourhood
            neighbourhood = self.Neighbourhood_Generator.random()

            #evaluate fitness of all neighbours
            order_indexes, node_indexes, fitness_values = self.evaluate_neighbourhood(neighbourhood, best_allocation)

            # carry out first admissable move
            for order_index, node_index, fitness in zip(order_indexes, node_indexes, fitness_values):

                # calcualte new objective value
                new_obj_value = obj_value + fitness
                
                # check if move is tabu active
                if (not self.is_tabu(tabu_add, order_index, node_index)) and (not self.is_tabu(tabu_add, order_index, new_allocation[order_index])):
                    move_admissable = True
                
                # check apiration criteria:
                elif new_obj_value > best_obj_value:
                    move_admissable = True
                        
                if move_admissable:

                    # check restriction
                    if self.restrictions_met(order_index, node_index):

                        # update tabu_drop lists
                        self.update_tabu_list(tabu_drop, self.tabu_drop_tenure, order_index, new_allocation[order_index], iter)

                        # carry out move
                        new_allocation[order_index] = node_index
                        
                        # update tabu_add list
                        self.update_tabu_list(tabu_add, self.tabu_drop_tenure, order_index, node_index, iter)

                        # check if allocation is worth memorizing
                        if self.memorable(new_obj_value):

                            self.memorize({ITER: iter, ALLOC_ARR:deepcopy(new_allocation), OBJ_VALUE:new_obj_value, TABU_ADD: tabu_add, TABU_DROP: tabu_drop})

                        # update aspiration criteria if new_allocation has best_obj_value
                        if new_obj_value > best_obj_value:
                            best_obj_value = new_obj_value
                            iter_since_improvement = 0

                            #UPDATE BEST??? from allocation.evaluation import update

                        else:
                            iter_since_improvement += 1

                        # check if searching process is apparently stuck in local maximum
                        if iter_since_improvement > self.max_iter_since_improvement:
                            
                            # restart from best not allocation not alreay used for a restart
                            new_allocation = self.memory_list[restart_trial][ALLOC_ARR]
                            tabu_add = self.memory_list[restart_trial][TABU_ADD]
                            tabu_drop = self.memory_list[restart_trial][TABU_DROP]

                            restart_trial += 1

                        break

        return self.best_allocation



    