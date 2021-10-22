from copy import deepcopy
from datetime import datetime
from numpy import array, random, sort
from typing import Union
import random

######################################################################

from copy import deepcopy
from datetime import datetime
from numpy import array

from allocation.constants import ALLOC_ARR, ITER, OBJ_VALUE, OPTIMIZER, TABU_ADD, TABU_DROP

class Optimizer():

    '''Parent class for all optimizers.'''

    def __init__(self) -> None:
        
        pass

    def calc_fitness(self, new_allocation) -> float:

        ''' Evaluates cost-improvement of modifiying currently allocated node with its neighbour.
            Returns improvement as delta between allocation to neighbour and current allocation.
            A positive return value means the allocation costs descreased and viceversa.'''
        
        return  sum(new_allocation)

    def evaluate_neighbourhood(self, neighbourhood:array, best_allocation:array) -> Union[array, array]:

        ''' Determines the fitness of all neighbours by comparing how they would improve the objective value
            in comparison to the current best allocaiton.
            Returns an array of order indexes ranked according to the fitness of the respective neighbours
            and an array of the neighbours ranked according to their fitness.'''

        fitness = []

        # calculate fitness value for each neighbour
        for order_index, neighbour_index in enumerate(neighbourhood):
            fitness.append(self.calc_fitness(order_index, neighbour_index, best_allocation[order_index]))

            # create arrays
            order_indexes = array(list(range(len(neighbourhood))))
            neighbour_fitness = array(fitness)

        return order_indexes[neighbour_fitness.argsort()], neighbourhood[neighbour_fitness.argsort()], sort(neighbour_fitness)

    def restrictions_met(self, order_index:int, node_index:int) -> bool:

        ''' Returns True or False based depending if the proposed node_index
            is a valid allocation for the order.'''
        
        return True if random.getrandbits(1) == 1 else False

    class Neighbourhood_Generator: 

        def random(self, candidates:list, size:int) -> array:

            '''Generates a random neighbourhood with elements from candidate list.'''

            return random.choice(candidates, size=size)


###############################################################################################


class Tabu_Search(Optimizer):

    ''' Allocates the order to the node with based on a certain calculated criterium.'''

    __type__ = OPTIMIZER

    def __init__(self) -> None:

        ''' Inits parent class for optimizers and 
            sets parameters for Tabu Search algorithm.'''
        
        super().__init__()

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

    def update_tabu_list(self, tabu_list:dict, order_index:int, node_index:int, iter:int) -> None:

        ''' Adds move to tabu list and 
            removes moves from tabu list which are not valid anymore.'''

        tabu_list[(order_index, node_index)] = iter + self.tabu_drop_tenure

        for key, tabu_stop_iter in tabu_list.items():
            if tabu_stop_iter > iter:
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
                if (not self.is_tabu(tabu_add, order_index, node_index)) or (not self.is_tabu(tabu_add, order_index, new_allocation[order_index])):
                    move_admissable = True
                
                # check apiration criteria:
                elif new_obj_value > best_obj_value:
                    move_admissable = True
                        
                if move_admissable:

                    # check restriction
                    if self.restrictions_met(order_index, node_index):

                        # update tabu_drop lists
                        self.update_tabu_list(tabu_drop, order_index, new_allocation[order_index], iter)

                        # carry out move
                        new_allocation[order_index] = node_index
                        
                        # update tabu_add list
                        self.update_tabu_list(tabu_add, order_index, node_index, iter)

                        # check if allocation is worth memorizing
                        if self.memorable(new_obj_value):

                            self.memorize({ITER: iter, ALLOC_ARR:deepcopy(new_allocation), OBJ_VALUE:new_obj_value, TABU_ADD: tabu_add, TABU_DROP: tabu_drop})

                        # update aspiration criteria if new_allocation has best_obj_value
                        if new_obj_value > best_obj_value:
                            best_obj_value = new_obj_value
                            iter_since_improvement = 0
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


#############################################################################################################

ts = Tabu_Search()

best_alloaction = list(random.randint(0, 25) for node_index in range(0, 26))

best_obj_value = ts.calc_fitness(best_alloaction)

result = ts.main()
    
    





