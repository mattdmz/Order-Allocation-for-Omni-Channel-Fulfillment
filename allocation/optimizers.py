
###############################################################################################

'''This file contains all the customized Tabu Search Optimizer.'''

###############################################################################################

from copy import deepcopy
from datetime import datetime
from math import sqrt
from numpy import array, full, argmax
from timeit import default_timer as timer
from typing import Union

from allocation.constants import DELIVERY, OPTIMIZER, TABU_ADD, TABU_DROP
from allocation.optimizer import Optimizer
from dstrbntw.region import Region
from protocols.constants import ALLOC_ARR, ITER, OBJ_VALUE


class Tabu_Search(Optimizer):

    ''' Allocates the order to the node with based on a certain calculated criterium.'''

    __type__ = OPTIMIZER

    def __init__(self, region:Region, current_time:datetime=None) -> None:

        ''' Inits parent class for optimizers and 
            sets parameters for Tabu Search algorithm.'''

        # set parameters
        self.number_of_available_nodes = len([region.nodes.accepting_orders])
        self.number_of_orders_to_allocate = len(region.orders.list)
        self.memory_list = []
        self.memory_length = 5
        self.max_iter = self.number_of_available_nodes * self.number_of_orders_to_allocate * 4
        self.change_restart_strategy_factor = 2

        # set lists and icts
        self.tabu_add = {}                  # format tabu_add[node_index]: iteration the tabu ends(iter + tabu_add_tenure)
        self.tabu_drop = {}                 # format tabu_drop[order_index]: iteration the tabu ends(iter + tabu_drop_tenure)
        self.init_frequency(len(region.orders.list), len(region.nodes.dict))
        
        # init parent solution
        super().__init__(region, current_time, self.main)

    @property
    def best_allocation(self) -> array:

        '''Returns the current best allocation.'''

        return self.memory_list[0][ALLOC_ARR]

    def memorable(self, new_obj_value:float) -> bool:
    
        ''' Retunrs True or False depending if the new_allocation is memorable or not.
            Memorable = True if new_obj_value > obj_value of the last element of the memory list'''

        return True if (len(self.memory_list) < self.memory_length or \
                       self.memory_list[len(self.memory_list) -1][OBJ_VALUE] < new_obj_value) and \
                       not new_obj_value in [self.memory_list[rank][OBJ_VALUE] for rank in range(len(self.memory_list))] \
                    else False

    def memorize(self, iter:int, allocation:array, obj_value:float, tabu_add:dict, tabu_drop:dict) -> None:

        ''' Adds allocation to memory list and drops the last element
            if the max. length of the memory_list was reached.'''

        alloc_to_memorize = {ITER: deepcopy(iter), 
                             ALLOC_ARR: deepcopy(allocation),
                             OBJ_VALUE: deepcopy(obj_value),
                             TABU_ADD: deepcopy(tabu_add),
                             TABU_DROP: deepcopy(tabu_drop)
        }

        offsetter = 0

        # insert allocation in sorted order accoring to the objective value in descening mode.
        if len(self.memory_list)== 0 or self.memory_list[len(self.memory_list)-1][OBJ_VALUE] > obj_value:
            self.memory_list.insert(len(self.memory_list), alloc_to_memorize)
        else:

            for index, memorized_allocation in reversed(list(enumerate(self.memory_list))):
                if obj_value < memorized_allocation[OBJ_VALUE]:
                    offsetter = 1
                    break
            self.memory_list.insert(index+offsetter, alloc_to_memorize)

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

    def set_tabu(self, tabu_list:dict, tabu_tenure:int, index:int) -> None:

        ''' Adds move to tabu list.'''

        tabu_list[index] = tabu_tenure

    def update_tabu_list(self, tabu_list:dict, iter:int) -> None:

        '''Removes moves from tabu list which are not valid anymore.'''

        for key, tabu_stop_iter in list(tabu_list.items()):
            if iter > tabu_stop_iter:
                del tabu_list[key]

    def tabu_add_tenure(self, iter:int, order_index:int) -> int:

        '''Returns the number of iterations a list index is considered tabu for being added to allocation.'''

        return iter + (self.moves.move_indexes[:order_index] != None).sum() / 2

    def tabu_drop_tenure(self, iter:int, allocation:array) -> int:

        '''Returns the number of iterations a list index is considered tabu for being dropped from allocation.'''

        return iter + (allocation >= 0).sum()

    def restart_tabu_list(self, restart_index:int, tabu_list:str, iter:int, allocation:array) -> dict:

        '''Returns a tabu list with updated tabu tenures.'''

        new_tabu_list = {}

        tabu_list = self.memory_list[restart_index][tabu_list]

        if tabu_list == TABU_ADD:

            for key in tabu_list.keys():
                new_tabu_list[key] = self.tabu_add_tenure(iter, key[0])

            return new_tabu_list

        else: #tabu_list == TABU_DROP:

            for key in tabu_list.keys():
                new_tabu_list[key] = self.tabu_drop_tenure(iter, allocation)

            return new_tabu_list

    def modify_entire_allocation(self, current_allocation:array, memorized_allocation:array) -> array:

        ''' Deallocates orders from current allocated nodes and allocates to nodes of memorized nodes.'''

        for order_index in range(len(current_allocation)):
            order_index:int

            if memorized_allocation[order_index] != current_allocation[order_index] and \
               memorized_allocation[order_index] >= 0:

                prototype_delivery = self.order_deliverable(self.orders.list[order_index], 
                                                            memorized_allocation[order_index])

                if prototype_delivery != None:

                    # set new delviery
                    prototype_delivery.create_batches(self.current_time)
                    if prototype_delivery.on_time(self.current_time):

                        if current_allocation[order_index] >= 0:
                            self.deallocate(self.orders.list[order_index], current_allocation[order_index])

                            setattr(self.nodes.__get__(index=memorized_allocation[order_index]), DELIVERY, prototype_delivery)  
                            self.allocate(self.orders.list[order_index], memorized_allocation[order_index])
                            current_allocation[order_index] = memorized_allocation[order_index]

        return current_allocation     

    def init_frequency(self, number_of_orders:int, number_of_nodes:int) -> None:

        ''' Sets up arrays for residence_frequency and transition_frequency.'''

        self.residence_frequency = full((number_of_nodes, number_of_orders), 0)
        self.transition_frequency = full((number_of_nodes, number_of_orders), 0)

    def update_residence_frequency(self, allocation:array) -> None:
        
        '''Updates the residence frequency based on the allocation of the current iter.'''

        for order_index in range(len(self.orders.list)):
            order_index:int

            if allocation[order_index] >= 0:
                self.residence_frequency[allocation[order_index], order_index] += 1

    def restart_frequency_based(self, current_allocation:array) -> Union[array, dict, dict]:

        '''Returns an allocation based on the frequency of node_indexes visiting some order_indexes.'''

        max_frequency_allocation = argmax(self.residence_frequency, axis=0)

        new_allocation = self.modify_entire_allocation(current_allocation, max_frequency_allocation)

        return array(new_allocation), {}, {} # empty tabu lists

    def restart_memory_based(self, iter:int, current_allocation:array, restart_index:int)-> Union[array, dict, dict]:

        '''Returns the allocaiton, tabu_add and tabu_drop list from the memory list at position restart_trial.'''

        if restart_index > len(self.memory_list) -1:
            restart_index = len(self.memory_list) -1

        # copy memorzied allocation ofr usage
        memorized_allocation = deepcopy(self.memory_list[restart_index][ALLOC_ARR])
        
        # modify current allocation
        new_allocation = self.modify_entire_allocation(current_allocation, memorized_allocation)

        return  new_allocation, self.restart_tabu_list(restart_index, TABU_ADD, iter, current_allocation), \
                self.restart_tabu_list(restart_index, TABU_DROP, iter, current_allocation)

    def main(self, allocation:array, obj_value:float) -> array:

        '''Runs the Tabu Search Algorithm on the initial_allocation.'''

        # init variables to evaluate solution quality
        best_obj_value = obj_value
        current_obj_value = obj_value
        new_obj_value = 0

        # flow control variables
        node_dropped = None
        move_carried_out = False             

        # set counters
        iter = 0
        iter_since_improvement = 0 
        restart_trial = 0
        memory_list_restart_index = 0

        # init memory list with current best solution
        self.residence_frequency +=1
        self.memorize(iter, allocation, obj_value, self.tabu_add, self.tabu_drop)
        
        # set starting strategy
        current_strategy = self.restart_memory_based.__name__ + "_" + str(memory_list_restart_index)

        print(" ")
        print("start optimization for", self.current_time)
        print("iter:", iter, "best_obj_value:", best_obj_value)

        # start timing
        timing_start = timer()

        while iter <= self.max_iter:

            iter += 1

            # determine possible moves and evaluate fitness of moves
            if iter_since_improvement == 0:
                self.moves.candidate_list_of_nodes = self.candidates_generator()
                self.moves.move_indexes, self.moves.fitness = self.calculate_move_fitness()
                move_carried_out = False

                # define max_iter_since_improvement as half of available moves
                self.max_iter_since_improvement = int(sqrt((self.moves.move_indexes != None).sum()))

            elif move_carried_out:
                # update move fitness
                self.update_fitness(order_index, node_index, node_dropped)
                move_carried_out = False
            else:
                pass
                print("iter", iter-1, "no move carried out.")
                
            # evaluate fitness of all moves
            if iter_since_improvement == self.max_iter_since_improvement - 1 or iter_since_improvement == self.max_iter_since_improvement:
                moves, fitness_values = self.moves.random_permutation()
            else:
                moves, fitness_values = self.moves.evaluate()

            # carry out first admissable move
            for move, fitness in zip(moves, fitness_values):
                move:tuple
                fitness:float

                # unpack move
                node_index = move[0]
                order_index = move[1]

                if node_index >= 0 and allocation[order_index] != node_index:

                    # approximate obj_value
                    new_obj_value = current_obj_value + fitness

                    # check if move is tabu active
                    if (not self.is_tabu(self.tabu_add,  (order_index, node_index))) and (not self.is_tabu(self.tabu_drop, order_index)) or \
                        new_obj_value > best_obj_value:

                        # check restriction
                        if self.restrictions_met(order_index, node_index):
                
                            # deallocate current node only if it had an allocation previously                            
                            if node_index >= 0 and allocation[order_index] >= 0:
                                self.deallocate(self.orders.list[order_index], allocation[order_index])
                                node_dropped = allocation[order_index]

                            # add move to tabu add list
                            self.set_tabu(self.tabu_add, self.tabu_add_tenure(iter, order_index), (order_index, node_dropped))

                            # carry out move
                            allocation[order_index] = node_index

                            print("iter", iter, ": allocating ", node_index, " to index ", order_index)

                            # allocate to neighbour
                            self.allocate(self.orders.list[order_index], node_index)

                            # frequencies
                            self.transition_frequency[node_index][order_index] += 1
                            self.update_residence_frequency(allocation)
                            
                            # add move to tabu drop list
                            self.set_tabu(self.tabu_drop, self.tabu_drop_tenure(iter, allocation), order_index)
                            
                            # calculate objective value
                            self.prepare_evaluation()
                            obj_value = self.evaluation_model.objective_function(allocation)
                            current_obj_value = obj_value
                            
                            print("new_obj_value (approx):", new_obj_value, "obj_val:", obj_value, "best_obj_val:", best_obj_value)

                            # check if allocation is worth memorizing
                            if self.memorable(obj_value):
                                self.memorize(iter, allocation, obj_value, self.tabu_add, self.tabu_drop)

                            move_carried_out = True
                            break
            
            # update aspiration criteria if allocation has best_obj_value
            if obj_value > best_obj_value:
                
                self.memorize_best_nodes(allocation)
                best_obj_value = obj_value
                iter_since_improvement = 0

            else:
                # no imporvement
                iter_since_improvement += 1

            self.protocol_iter(iter, current_obj_value, best_obj_value, current_strategy, timer() - timing_start, allocation)

            # update tabu lists
            self.update_tabu_list(self.tabu_add, iter)
            self.update_tabu_list(self.tabu_drop, iter)

            # check if searching process is apparently stuck in local maximum
            if iter_since_improvement > self.max_iter_since_improvement:

                #check if restarting strategy needs to change
                if restart_trial == 0 or restart_trial % self.change_restart_strategy_factor != 0:

                    # use memory based strategy to restart
                    memory_list_restart_index = (memory_list_restart_index + 1) if memory_list_restart_index < self.memory_length - 1 else 0
                    allocation, self.tabu_add, self.tabu_drop = self.restart_memory_based(iter, allocation, memory_list_restart_index)

                    # add strategy change for protocol
                    current_strategy = self.restart_memory_based.__name__+ "_" + str(memory_list_restart_index)
                    
                    print("---")
                    print("iter_", iter, ": new_strategy", current_strategy, "using memory index: ", memory_list_restart_index)
                    print("---")

                else:
                    # use frequenecy based restart strategy
                    allocation, self.tabu_add, self.tabu_drop = self.restart_frequency_based(allocation)
                    self.change_restart_strategy_factor
                    
                    # add strategy change for protocol
                    current_strategy = self.restart_frequency_based.__name__+ "_" + str(memory_list_restart_index)

                    print("---")
                    print("iter", iter, ": new_strategy", current_strategy)
                    print("---")

                # update obj_function ans current_obj_function
                self.prepare_evaluation()
                obj_value = self.evaluation_model.objective_function(allocation)
                current_obj_value = obj_value
                
                # update counters
                iter_since_improvement = 0
                restart_trial += 1

        # optimization terminated, allocate to best solution found
        return self.modify_entire_allocation(allocation, self.best_allocation)
