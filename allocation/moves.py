

###############################################################################################

'''This file contains the class Moves.'''

###############################################################################################


from numpy import argsort, array, Infinity, random
from typing import Union

from numpy.random.mtrand import permutation

from transactions.orders import Order


class Moves:

    def __init__(self, candidate_list_of_nodes:list) -> None:

        ''' Stores info about possible moves to carry out.'''

        self.candidate_list_of_nodes = candidate_list_of_nodes
        self.move_indexes = None
        self.fitness = None

    def determine_candiate_nodes(self, order:Order, order_index:int) -> list:

        ''' Returns a list of candiate nodes which excetion of the currently allocated node
            forming the neighbourhood.'''

        return [node for node in self.candidate_list_of_nodes[order_index] if node != order.allocated_node]

    def evaluate(self) -> Union[array, array, array]:

        ''' Returns an array of moves sorted descending baed on their fitness.'''

        # flatten 2D array
        flat_fitness = self.fitness[self.fitness != -Infinity].flatten()
        flat_move_indexes = self.move_indexes[self.move_indexes != None].flatten()

        # get permutation of sorting according to fitness [desc]
        permutation = flat_fitness.argsort()[::-1]

        return flat_move_indexes[permutation], flat_fitness[permutation]

    def random_permutation(self) -> Union[array, array, array]:

        ''' Returns an array of moves moves sorted according to a random permutation.'''

        # flatten 2D array
        flat_fitness = self.fitness[self.fitness != -Infinity].flatten()
        flat_move_indexes = self.move_indexes[self.move_indexes != None].flatten()

        # get permutation of sorting according to fitness [desc]
        permutation = random.permutation(len(flat_fitness)) 

        return flat_move_indexes[permutation], flat_fitness[permutation]
    
