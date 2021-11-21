

###############################################################################################

'''This file contains the class Neighbourhood.'''

###############################################################################################


from numpy import array, flip, float64, full, Infinity, sort
from typing import Union

from transactions.orders import Order


class Neighbourhood:

    def __init__(self, lists:list) -> None:

        ''' Stores info about a neighboourhood.'''

        n = sum([len(list) for list in lists])

        self.lists = lists
        self.order_indexes = full(shape=n, fill_value=-1, dtype=int)
        self.neighbour_indexes = full(shape=n, fill_value=-1, dtype=int)
        self.fitness = full(shape=n, fill_value=-Infinity, dtype=float64)

    def update(self, lists:list) -> None:

        '''Updates the list of neighbours at positin order_index.'''

        self.lists = lists

    def determine(self, order:Order, order_index:int) -> list:

        ''' Returns a list of candiate nodes which excetion of the currently allocated node
            forming the neighbourhood.'''

        return [node for node in self.lists[order_index] if node != order.allocated_node]

    def evaluate(self) -> Union[array, array, array]:

        ''' Returns an array of order indexes ranked according to the fitness of the respective neighbours
            and an array of the neighbours ranked according to their fitness.'''

        # sort according to best fitness
        permutation = self.fitness.argsort()[::-1]

        return self.order_indexes[permutation], self.neighbour_indexes[permutation], flip(sort(self.fitness))
