
from copy import deepcopy
from datetime import datetime
from numpy import array, flip, random as np_random, sort
from typing import Union

from allocation.constants import DELIVERY, DURATIONS, DEMANDED, RATES, ROUTE_RATES, TOUR_RATES
from allocation.allocator import Allocator
from dstrbntw.constants import CUSTOMER
from allocation.evaluation import improvement, update
from dstrbntw.delivery import Delivery
from dstrbntw.constants import PIECES
from dstrbntw.nodes import Node
from dstrbntw.region import Region
from transactions.orders import Order

class Optimizer(Allocator):

    '''Parent class for all optimizers.'''

    def __init__(self, region: Region, current_time: datetime, cut_off_time: datetime, main) -> None:
        
        ''' Inits Allocator parents class and creates an allocation to be used as seed (starting allocation)
            for the optimizaiton.'''

        super().__init__(region, current_time, cut_off_time)

        # store main method of child class
        self.main = main

        # seed 
        seed_allocation = self.seed()
        
        # determine obj_value of seed
        self.prepare_evaluation()
        seed_obj_value = self.evaluation_model.objective_function(seed_allocation)

        # run algorithm, evaluate and store result
        allocation = self.main(seed_allocation, seed_obj_value)
        self.store_allocation(self.evaluate(allocation))

    def seed(self) -> array:

        '''Returns a seed (allocation) for the optimization.'''

        allocatable = False

        while not allocatable:

            seed = self.Neighbourhood_Generator.random(candidates=self.nodes.accepting_orders, size=len(self.orders) -1)

            for order_index, node_index in enumerate(seed):
                order_index:int
                node_index:int

                allocatable = self.restrictions_met(order_index, node_index)

        return seed

    def calc_fitness(self, order_index:int, neighbour_index:int, current_node_index:int) -> float:

        ''' Evaluates cost-improvement of modifiying currently allocated node with its neighbour.
            Returns improvement as delta between allocation to neighbour and current allocation.
            A positive return value means the allocation costs descreased and viceversa.'''

        # get the neighbour's node object
        neighbour = self.nodes.__get__(index=neighbour_index) #type: Node

        # build a protype_tour to approximate route duration
        prototype_tour = deepcopy(neighbour.delivery) #type: Delivery
        prototype_tour.approximate_routes(prototype_tour.calc_duration_to_other_stops(self.orders.__getattr__(order_index, CUSTOMER)))

        print("supply improvement: ", improvement(self.evaluation_model.supply, RATES, order_index, neighbour.supply_rate))
        print("order proc improvement: ", improvement(self.evaluation_model.order_processing, RATES, order_index, neighbour.order_processing_rate))
        print("stock improvement: ", improvement(self.evaluation_model.stock, RATES, current_node_index, neighbour.stock_holding_rate) * self.evaluation_model.stock.demanded))
        print("tour rates improvement: ", improvement(self.evaluation_model.tours, TOUR_RATES, order_index, neighbour.tour_rate))
        print("route rates improvement: ", improvement(self.evaluation_model.tours, ROUTE_RATES, order_index, neighbour.route_rate))
        print("durations improvement: ", improvement(self.evaluation_model.tours, DURATIONS, order_index, prototype_tour.tot_duration))


        
        return      improvement(self.evaluation_model.supply, RATES, order_index, neighbour.supply_rate) \
                +   improvement(self.evaluation_model.order_processing, RATES, order_index, neighbour.order_processing_rate) \
                +   improvement(self.evaluation_model.stock, RATES, current_node_index, neighbour.stock_holding_rate) * self.evaluation_model.stock.demanded \
                +   improvement(self.evaluation_model.tours, TOUR_RATES, order_index, neighbour.tour_rate) \
                +   improvement(self.evaluation_model.tours, ROUTE_RATES, order_index, neighbour.route_rate) \
                *   improvement(self.evaluation_model.tours, DURATIONS, order_index, prototype_tour.tot_duration)

    def evaluate_neighbourhood(self, neighbourhood:array, best_allocation:array) -> Union[array, array]:

        ''' Determines the fitness of all neighbours by comparing how they would improve the objective value
            in comparison to the current best allocaiton.
            Returns an array of order indexes ranked according to the fitness of the respective neighbours
            and an array of the neighbours ranked according to their fitness.'''

        fitness = []

        # calculate fitness value for each neighbour
        for order_index, neighbour_index in enumerate(neighbourhood):
            order_index:int
            neighbour_index:int
            
            fitness.append(self.calc_fitness(order_index, neighbour_index, best_allocation[order_index]))

        # create arrays
        order_indexes = array(list(range(len(neighbourhood))))
        neighbour_fitness = array(fitness)
        
        # get permutation to apply on other arrays
        permutation = neighbour_fitness.argsort()[::-1]

        return order_indexes[permutation], neighbourhood[permutation], flip(sort(neighbour_fitness))

    def restrictions_met(self, order_index:int, node_index:int) -> bool:

        ''' Returns True or False based depending if the proposed node_index
            is a valid allocation for the order.'''

        # check if node can currently recieve orders
        if self.node_available(node_index):
            
            # get order
            order = self.orders.__get__(order_index) #type: Order
            
            if self.stock_available(order, node_index):

                # check order deliverability (vehicle volume restrictions, scheduling of order proc and delivery restrictions)
                delivery = self.order_deliverable(order, node_index) #

                if delivery is not None:
                    
                    # replace tour
                    setattr(self.nodes.__get__(index=node_index), DELIVERY, delivery)
                
                    return True 
        
        return False

    class Neighbourhood_Generator: 

        def random(self, candidates:list, size:int) -> array:

            '''Generates a random neighbourhood with elements from candidate list.'''

            return np_random.choice(candidates, size=size)



    





