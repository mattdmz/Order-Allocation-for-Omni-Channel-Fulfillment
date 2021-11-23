
###############################################################################################

'''This file contains all the customized Tabu Search Optimizer.'''

###############################################################################################

from copy import deepcopy
from datetime import datetime
from math import floor
from numpy import array, Infinity
from timeit import default_timer as timer
from typing import Union

from allocation.constants import DELIVERY, OPTIMIZER, TABU_ADD, TABU_DROP
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

        # set lists and icts
        self.tabu_add = {}                  # format tabu_add[node_index]: iteration the tabu ends(iter + tabu_add_tenure)
        self.tabu_drop = {}                 # format tabu_drop[order_index]: iteration the tabu ends(iter + tabu_drop_tenure)
        self.frequency = self.init_frequency(region.nodes.accepting_orders, len(region.orders.list))
        
        # init parent solution
        super().__init__(region, current_time, self.main)

    @property
    def best_allocation(self) -> array:

        '''Returns the current best allocation.'''

        return self.memory_list[0][ALLOC_ARR]

    def memorize(self, iter:int, allocation:array, obj_value:float, tabu_add:dict, tabu_drop:dict) -> None:

        ''' Adds allocation to memory list and drops the last element
            if the max. length of the memory_list was reached.'''

        alloc_to_memorize = {ITER: deepcopy(iter), 
                             ALLOC_ARR: deepcopy(allocation),
                             OBJ_VALUE: deepcopy(obj_value),
                             TABU_ADD: deepcopy(tabu_add),
                             TABU_DROP: deepcopy(tabu_drop)
        }
        
        index = 0

        # insert allocation in sorted order accoring to the objective value in descening mode.
        for index, memorized_allocation in reversed(list(enumerate(self.memory_list))):
            if memorized_allocation[OBJ_VALUE] >= obj_value:
                break

        self.memory_list.insert(index+1, alloc_to_memorize)

        # check if the max length of the memory list was reached
        if len(self.memory_list) > self.memory_length:
            
            # drop element
            del self.memory_list[len(self.memory_list) - 1]

    def is_tabu(self, tabu_list:dict, key:int) -> bool:

        '''Returns True or False depending if the order_index/node_index is tabu.'''
        
        try:
            if tabu_list[key]:
                return True
        except KeyError:
                return False

    def set_tabu(self, tabu_list:dict, tabu_tenure:int, index:int, iter:int) -> None:

        ''' Adds move to tabu list.'''

        tabu_list[index] = iter + tabu_tenure

    def update_tabu_list(self, tabu_list:dict, iter:int) -> None:

        '''Removes moves from tabu list which are not valid anymore.'''

        for key, tabu_stop_iter in list(tabu_list.items()):
            if iter > tabu_stop_iter:
                del tabu_list[key]

    def tabu_add_tenure(self, iter:int, number_of_orders_to_allocate:int) -> int:

        '''Returns the number of iterations a list index is considered tabu for being added to allocation.'''

        return 5 #round(4 + exp(sqrt(self.max_iter) / pow(4.25 * number_of_orders_to_allocate, 2) * iter), 0)

    def tabu_drop_tenure(self, iter:int, number_of_orders_to_allocate:int) -> int:

        '''Returns the number of iterations a list index is considered tabu for being dropped from allocation.'''

        return floor(number_of_orders_to_allocate / 2) #round(4 + exp(sqrt(self.max_iter) / pow(4.5 * number_of_orders_to_allocate, 2) *iter), 0)

    def init_frequency(self, candidates:list, number_of_orders_to_allocate:int) -> list:

        ''' Retunrns a list of dicts to collect the number of number times a node_index 
            is added to the allocation at a certain order_index.'''

        dict = {}
        frequencies = []

        for candidate in candidates:
            candidate:Node
            dict[candidate.index] = 0

        for order_index in range(number_of_orders_to_allocate):
            frequencies.append(dict)

        return frequencies

    def protocol_seed(self, allocation:array) -> None:

        for order_index, node_index in enumerate(allocation):
        
            # set seed allocation tabus
            self.set_tabu(self.tabu_add, self.tabu_add_tenure(0, len(self.orders.list)), node_index, 0) 

            # update allocation ad frequency for order_index
            self.frequency[order_index][node_index] += self.tabu_drop_tenure(0, len(self.orders.list))

    def modify_allocation_for_new_strategy(self, current_allocation:array, memorized_allocation:array) -> None:

        ''' Deallocates orders from current allocated nodes and allocates to nodes of memorized nodes.'''

        for order_index in range(len(current_allocation)):
            order_index:int

            self.deallocate(self.orders.list[order_index], current_allocation[order_index])
            setattr(self.nodes.__get__(index=memorized_allocation[order_index]), DELIVERY, 
                    self.order_deliverable(self.orders.list[order_index], memorized_allocation[order_index]))
            self.allocate(self.orders.list[order_index], memorized_allocation[order_index])

    def restart_frequency_based(self, current_allocation:array) -> Union[array, dict, dict]:

        '''Returns an allocation based on the frequency of node_indexes visiting some order_indexes.'''

        new_allocation = []

        for order_index in range(0, len(self.frequency)):
            new_allocation.append(max(self.frequency[order_index], key=self.frequency[order_index].get))

        self.modify_allocation_for_new_strategy(current_allocation, new_allocation)

        return array(new_allocation), {}, {} # empty tabu lists

    def restart_memory_based(self, current_allocation:array, restart_index:int)-> Union[array, dict, dict]:

        '''Returns the allocaiton, tabu_add and tabu_drop list from the memory list at position restart_trial.'''

        if restart_index > len(self.memory_list) -1:
            restart_index = len(self.memory_list) -1

        # copy memorzied allocation ofr usage
        memorized_allocation = deepcopy(self.memory_list[restart_index][ALLOC_ARR])
        
        # modify current allocation
        self.modify_allocation_for_new_strategy(current_allocation, memorized_allocation)

        return  memorized_allocation, \
                deepcopy(self.memory_list[restart_index][TABU_ADD]), \
                deepcopy(self.memory_list[restart_index][TABU_DROP])

    def main(self, allocation:array, obj_value:float) -> array:

        '''Runs the Tabu Search Algorithm on the initial_allocation.'''

        # init variables to evaluate solution quality
        best_obj_value = obj_value
        approx_obj_value = 0

        # flow control variables
        node_dropped = None
        node_allocated_to = None              

        # set counters
        iter = 0
        iter_since_improvement = 0 
        restart_trial = 0
        memory_list_restart_index = 0

        # init memory list with current best solution
        self.protocol_seed(allocation)
        self.memorize(iter, allocation, obj_value, self.tabu_add, self.tabu_drop)
        
        # set starting strategy
        current_strategy = self.restart_memory_based.__name__

        # start timing
        timing_start = timer()

        while iter <= self.max_iter:

            iter += 1

            # generate neighbourhood
            if obj_value >= best_obj_value:
                self.neighbourhood.update(self.candidates_generator())
                self.calculate_neighbourhood_fitness()
            else:
                self.calculate_node_fitness(node_dropped)
                self.calculate_node_fitness(node_allocated_to)
                
            # evaluate fitness of all neighbours
            order_indexes, node_indexes, fitness_values = self.neighbourhood.evaluate()

            # carry out first admissable move
            for order_index, node_index, fitness in zip(order_indexes, node_indexes, fitness_values):
                order_index:int
                node_index:int
                fitness:float

                if not node_index == allocation[order_index] and node_index >= 0:

                    # approximate obj_value
                    approx_obj_value = best_obj_value + fitness

                    # check if move is tabu active
                    if (not self.is_tabu(self.tabu_add,  node_index) or (approx_obj_value > best_obj_value)) and \
                        (not self.is_tabu(self.tabu_drop, order_index) or (approx_obj_value > best_obj_value)) :

                        # check restriction
                        if self.restrictions_met(order_index, node_index):
                
                            # deallocate current node only if it had an allocation previously.
                            # (allocation[order_index] == -1 if allocation is invalid
                            print("iter", iter, ": alloc: ", allocation, " deallocating ", allocation[order_index], " from index ", order_index)
                            
                            if node_index >= 0:
                                self.deallocate(self.orders.list[order_index], allocation[order_index])
                                node_dropped = allocation[order_index]

                            # add move to tabu add list
                            self.set_tabu(self.tabu_add, self.tabu_add_tenure(iter, len(allocation)), node_dropped, iter)

                            # carry out move
                            allocation[order_index] = node_index
                            print("iter", iter, ": allocating ", node_index, " to index ", order_index, "-> alloc: ", allocation)

                            # allocate to neighbour
                            self.allocate(self.orders.list[order_index], node_index)
                            node_allocated_to = node_index

                            # update allocation frequency for order_index
                            self.frequency[order_index][node_index] += 1
                            
                            # add move to tabu drop list
                            self.set_tabu(self.tabu_drop, self.tabu_drop_tenure(iter, len(allocation)), order_index, iter)
                            
                            # calculate objective value
                            self.prepare_evaluation()
                            obj_value = self.evaluation_model.objective_function(allocation)
                            
                            #print("approx_val: ", approx_obj_value, "obj_val: ", obj_value)
                            approx_obj_value = obj_value

                            # check if allocation is worth memorizing
                            if self.memorable(obj_value):
                                self.memorize(iter, allocation, obj_value, self.tabu_add, self.tabu_drop)

                            break
            
            # update aspiration criteria if allocation has best_obj_value
            if approx_obj_value > best_obj_value:
                
                self.memorize_best_nodes(allocation)
                best_obj_value = obj_value
                iter_since_improvement = 0

            else:
                # no imporvement
                iter_since_improvement += 1

            self.protocol_iter(iter, approx_obj_value, best_obj_value, current_strategy, timer() - timing_start, allocation)

            # update tabu lists
            self.update_tabu_list(self.tabu_add, iter)
            self.update_tabu_list(self.tabu_drop, iter)

            # check if searching process is apparently stuck in local maximum
            if iter_since_improvement > self.max_iter_since_improvement:

                #check if restarting strategy needs to change
                if restart_trial < self.change_restart_strategy:

                    # use memory based strategy to restart
                    memory_list_restart_index = (memory_list_restart_index + 1) if memory_list_restart_index < self.memory_length - 1 else 0
                    allocation, self.tabu_add, self.tabu_drop = self.restart_memory_based(allocation, memory_list_restart_index)
                    
                    # add strategy change for protocol
                    current_strategy = self.restart_memory_based.__name__

                else:

                    # use frequenecy based restart strategy
                    allocation, self.tabu_add, self.tabu_drop = self.restart_frequency_based(allocation)
                    
                    # add strategy change for protocol
                    current_strategy = self.restart_frequency_based.__name__
                
                # update counters
                iter_since_improvement = 0
                restart_trial += 1

        return self.best_allocation
