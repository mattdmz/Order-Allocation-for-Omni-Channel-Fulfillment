
from copy import deepcopy
from datetime import datetime
from numpy import array, random, sort
from typing import Union

from allocation.allocator import Allocator
from database.constants import TOUR
from dstrbntw.constants import CUSTOMER
from dstrbntw.region import Region

class Optimizer(Allocator):

    '''Parent class for all optimizers.'''

    def __init__(self, region: Region, current_time: datetime, cut_off_time: datetime) -> None:
        
        super().__init__(region, current_time, cut_off_time)

    def calc_fitness(self, order_index:int, neighbour_index:int, current_node_index:int) -> float:

        ''' Evaluates cost-improvement of modifiying currently allocated node with its neighbour.
            Returns improvement as delta between allocation to neighbour and current allocation.
            A positive return value means the allocation costs descreased and viceversa.'''

        # get the neighbour's node object
        neighbour = self.nodes.__get__(index=neighbour_index)

        # build a protype_tour to approximate route duration
        prototype_tour = deepcopy(neighbour.tour)
        prototype_tour.approximate_routes(prototype_tour.calc_duration_to_other_stops(self.orders.__getattr__(order_index, CUSTOMER)))
        
        return    self.evaluation_model.supply.rate_improvement(order_index, neighbour.supply_rate) \
                + self.evaluation_model.order_processing.rate_improvement(order_index, neighbour.order_processing_rate) \
                + self.evaluation_model.stock.rate_improvement(current_node_index, neighbour.stock_holding_rate) \
                + self.evaluation_model.tours.tour_rate_improvement(current_node_index, neighbour.tour_rate) \
                + self.evaluation_model.tours.route_rate_improvement(current_node_index, neighbour.route_rate) \
                * self.evaluation_model.tours.duration_improvement(current_node_index, prototype_tour.tot_duration)

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

    def restrictions_met(self, node_index:int, order_index:int) -> bool:

        ''' Returns True or False based depending if the proposed node_index
            is a valid allocation for the order.'''

        # check if node can currently recieve orders
        if self.node_available(node_index):
            
            # get order
            order = self.orders.__get__(order_index)
            
            if self.stock_available(order, node_index):

                # check order deliverability (vehicle volume restrictions, scheduling of order proc and delivery restrictions)
                tour = self.order_deliverable(order, node_index)

                if tour is not None:
                    
                    # replace tour
                    setattr(self.nodes.__get__(index=node_index), TOUR, tour)
                
                    return True 
        
        return False

    class Neighbourhood_Generator: 

        def random(self, candidates:list, size:int) -> array:

            '''Generates a random neighbourhood with elements from candidate list.'''

            return random.choice(candidates, size=size)



    





