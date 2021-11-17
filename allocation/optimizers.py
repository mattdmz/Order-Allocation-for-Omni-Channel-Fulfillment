
###############################################################################################

'''This file contains all the customized Tabu Search Optimizer.'''

###############################################################################################

from copy import deepcopy
from datetime import datetime
from numpy import array, Infinity
from pandas import Series
from timeit import default_timer as timer

from allocation.constants import OPTIMIZER, TABU_ADD, TABU_DROP
from allocation.optimizer import Optimizer
from dstrbntw.region import Region
from dstrbntw.nodes import Node
from protocols.constants import ALLOC_ARR, BEST_OBJ_VALUE, CUR_TIME, ITER, OBJ_VALUE, STRATEGY


class Tabu_Search(Optimizer):

    ''' Allocates the order to the node with based on a certain calculated criterium.'''

    __type__ = OPTIMIZER

    def __init__(self, region:Region, current_time:datetime=None) -> None:

        ''' Inits parent class for optimizers and 
            sets parameters for Tabu Search algorithm.'''

        # set parameters
        self.memory_list = []
        self.memory_length = 5
        self.max_iter = 50
        self.max_iter_since_improvement = 8
        self.change_restart_strategy = 2
        
        # init parent solution
        super().__init__(region, current_time, self.main)

    @property
    def best_allocation(self) -> array:

        '''Returns the current best allocation.'''

        return self.memory_list[0][ALLOC_ARR]

    def memorize(self, new_allocation:dict) -> None:

        ''' Adds allocation to memory list and drops the last element
            if the max. length of the memory_list was reached.'''
        
        index = 0

        # insert new_allocation in sorted order accoring to the objective value in descening mode.
        for index, allocation in enumerate(self.memory_list):
            if allocation[OBJ_VALUE] < new_allocation[OBJ_VALUE]:
                break

        self.memory_list.insert(index, new_allocation)

        # check if the max length of the memory list was reached
        if len(self.memory_list) > self.memory_length:
            
            # drop element
            del self.memory_list[len(self.memory_list) - 1]

    def memorable(self, new_obj_value:float) -> bool:

        ''' Retunrs True or False depending if the new_allocation is memorable or not.
            Memorable = True if new_obj_value > obj_value of the last element of the memory list'''

        return True if self.memory_list[len(self.memory_list) -1][OBJ_VALUE] < new_obj_value else False

    def is_tabu(self, tabu_list:dict, key:int) -> bool:

        '''Returns True or False depending if the order_index/node_index is tabu.'''
        
        try:
            if tabu_list[key]:
                return True
        except KeyError:
                return False

    # def candiates_tabu_check(self, tabu_add:dict, candidates:array) -> array:

    #     ''' Sets tabu active candidates to - infinite in candidates array.
    #         Returns an array of non tabu candidates.'''

    #     non_tabu_candidates = deepcopy(candidates)

    #     for index, node_index in enumerate(candidates):
            
    #         # check if index in tabu active
    #         if self.is_tabu(tabu_add, node_index):
    #             non_tabu_candidates[index] = -Infinity

    #     return non_tabu_candidates

    # def neighbourhood_tabu_check(self, tabu_drop:dict, neighbourhood:array) -> array:

    #     ''' Sets tabu actice neighbours to - infinite in neighbours array.
    #         Returns an array of non tabu candidates.'''

    #     for order_index in range(len(neighbourhood)):
            
    #         # check if index in tabu active
    #         if self.is_tabu(tabu_drop, order_index):
    #             neighbourhood[order_index] = -Infinity

    #     return neighbourhood

    def update_tabu_list(self, tabu_list:dict, index:int, tabu_tenure:int, iter:int) -> None:

        ''' Adds move to tabu list and 
            removes moves from tabu list which are not valid anymore.'''

        tabu_list[index] = iter + tabu_tenure

        for key, tabu_stop_iter in list(tabu_list.items()):
            if iter >= tabu_stop_iter:
                del tabu_list[key]

    def tabu_add_tenure(self, iter:int, orders_to_allocate:int) -> int:

        '''Retunrs the number of iterations a list index is considered tabu for being added to allocation.'''

        return 4 #round(4 + exp(sqrt(self.max_iter) / pow(4.25 * orders_to_allocate, 2) * iter), 0)

    def tabu_drop_tenure(self, iter:int, orders_to_allocate:int) -> int:

        '''Retunrs the number of iterations a list index is considered tabu for being dropped from allocation.'''

        return 4#round(4 + exp(sqrt(self.max_iter) / pow(4.5 * orders_to_allocate, 2) *iter), 0)

    def init_frequency(self, candidates:list, orders_to_allocate:int) -> list:

        ''' Retunrns a list of dicts to collect the number of number times a node_index 
            is added to the allocation at a certain order_index.'''

        dict = {}
        frequencies = []

        for candidate in candidates:
            dict[candidate] = 0

        for order_index in range(orders_to_allocate):
            frequencies.append(dict)

        return frequencies

    def restart_frequency_based(self, frequency:list) -> array:

        '''Returns an allocation based on the frequency of node_indexes visiting some order_indexes.'''

        allocation = []

        for order_index in range(0, len(frequency)):
            allocation.append(max(frequency[order_index], key=frequency[order_index].get))

        return array(allocation), {}, {} # empty tabu lists

    def restart_memory_based(self, restart_index:int):

        '''Returns the allocaiton, tabu_add and tabu_drop list from the memory list at position restart_trial.'''

        return  deepcopy(self.memory_list[restart_index][ALLOC_ARR]), \
                deepcopy(self.memory_list[restart_index][TABU_ADD]), \
                deepcopy(self.memory_list[restart_index][TABU_DROP])

    def main(self, new_allocation:array, obj_value:float) -> array:

        '''Runs the Tabu Search Algorithm on the initial_allocation.'''

        # init memory list with current best solution
        self.memorize({ITER: 0, ALLOC_ARR:new_allocation, OBJ_VALUE:obj_value, TABU_ADD: {}, TABU_DROP: {}})

        # set starting values
        iter = 0
        iter_since_improvement = 0
        restart_trial = 0
        memory_list_restart_index = 0
        orders_to_allocate = len(new_allocation)
        nodes_available = self.nodes.accepting_orders
        best_obj_value = obj_value
        current_strategy = self.restart_memory_based.__name__
        tabu_add = {}                  # format tabu_add[node_index]: iteration the tabu ends(iter + tabu_add_tenure)
        tabu_drop = {}                 # format tabu_drop[order_index]: iteration the tabu ends(iter + tabu_drop_tenure)
        frequency = self.init_frequency(self.nodes.accepting_orders, orders_to_allocate)

        # start timing
        timing_start = timer()

        while iter <= self.max_iter:

            iter += 1

            # generate neighbourhood
            neighbourhood = self.Neighbourhood_Generator.random(nodes_available, len(new_allocation))

            #evaluate fitness of all neighbours
            order_indexes, node_indexes, fitness_values = self.evaluate_neighbourhood(neighbourhood, self.best_allocation)

            # carry out first admissable move
            for order_index, node, fitness in zip(order_indexes, node_indexes, fitness_values):
                order_index:int
                node:Node
                fitness:float

                # approximate obj_value
                approx_obj_value = best_obj_value + fitness

                # check if move is tabu active
                if (not self.is_tabu(tabu_add, node.index) and not self.is_tabu(tabu_drop, order_index)) or (approx_obj_value > best_obj_value):

                    # check restriction
                    if self.restrictions_met(order_index, node.index):
                
                        # update tabu_drop lists
                        self.update_tabu_list(tabu_add, self.tabu_add_tenure(iter, orders_to_allocate), order_index, iter)

                        # deallocate current node, if its alloation was previously valid 
                        if node.index >= 0:
                            self.deallocate(self.orders.list[order_index], new_allocation[order_index])

                        # carry out move
                        new_allocation[order_index] = node.index

                        # allocate neighbour
                        self.allocate(self.orders.list[order_index], node.index)

                        # update allocation ad frequency for order_index
                        frequency[order_index][node.index] += 1
                        
                        # update tabu_drop list
                        self.update_tabu_list(tabu_drop, self.tabu_drop_tenure(iter, orders_to_allocate), order_index, iter)

                        
                        self.prepare_evaluation()
                        print("approx_val: ", approx_obj_value, "obj_val: ", self.evaluation_model.objective_function(new_allocation))

                        # check if allocation is worth memorizing
                        if self.memorable(approx_obj_value):

                            self.prepare_evaluation()
                            self.memorize({ ITER: iter, 
                                            ALLOC_ARR:deepcopy(new_allocation), 
                                            OBJ_VALUE:self.evaluation_model.objective_function(new_allocation), 
                                            TABU_ADD: deepcopy(tabu_add), 
                                            TABU_DROP: deepcopy(tabu_drop)
                            })

                        # update aspiration criteria if new_allocation has best_obj_value
                        if approx_obj_value > best_obj_value:

                            print("iter: ", iter, ", obj_value: ", best_obj_value, ", improvement: ", approx_obj_value - best_obj_value, "tabu_list_len: ", self.tabu_add_tenure(iter, orders_to_allocate), new_allocation)

                            best_obj_value = approx_obj_value
                            iter_since_improvement = 0
                            break

                        else:
                            # no imporvement 
                            iter_since_improvement += 1

                        # protocol iteration
                        self.protocol.append(Series({   OBJ_VALUE: approx_obj_value, 
                                                        BEST_OBJ_VALUE: best_obj_value, 
                                                        STRATEGY: current_strategy,
                                                        CUR_TIME: timer()
                        }, name=iter))

                        # check if searching process is apparently stuck in local maximum
                        if iter_since_improvement > self.max_iter_since_improvement:

                            #check if restarting strategy needs to change
                            if restart_trial < self.change_restart_strategy:

                                # use memory based strategy to restart
                                memory_list_restart_index = (memory_list_restart_index + 1) if memory_list_restart_index < self.memory_length - 1 else 0
                                new_allocation, tabu_add, tabu_drop = self.restart_memory_based(memory_list_restart_index)
                                
                                # add strategy change for protocol
                                current_strategy = self.restart_memory_based.__name__

                            else:

                                # use frequenecy based restart strategy
                                new_allocation, tabu_add, tabu_drop = self.restart_frequency_based(frequency)
                                
                                # add strategy change for protocol
                                current_strategy = self.restart_frequency_based.__name__
                            
                            # update counters
                            iter_since_improvement = 0
                            restart_trial += 1
                        break

        return self.best_allocation
