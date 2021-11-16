
###############################################################################################

'''This file contains the parent class for all optimizers.'''

###############################################################################################

from copy import deepcopy
from datetime import datetime
from numpy import array, flip, float64, Infinity, random as np_random, sort, zeros
from pandas import DataFrame
from typing import Union

from allocation.constants import DELIVERY
from allocation.allocator import Allocator
from dstrbntw.delivery import Delivery
from dstrbntw.location import distance
from dstrbntw.nodes import Node
from dstrbntw.region import Region
from parameters import MAX_PAL_VOLUME
from protocols.constants import BEST_OBJ_VALUE, CUR_TIME, OBJ_VALUE, STRATEGY
from transactions.orders import Order

class Optimizer(Allocator):

    '''Parent class for all optimizers.'''

    def __init__(self, region: Region, current_time: datetime, main) -> None:
        
        ''' Inits Allocator parents class and creates an allocation to be used as seed (starting allocation)
            for the optimizaiton.'''

        super().__init__(region, current_time)

        # store main method of child class
        self.main = main

        # init a DataFrame to protocol the optimization run
        self.protocol = self.init_protocol()

        # determine candidate nodes for allocation
        candidates = array(self.nodes.indexes_of_accepting_orders)

        # create seed allocation and calc obj value
        seed_allocation = self.seed(candidates)
        self.allocate_seed(seed_allocation)
        self.prepare_evaluation()
        seed_obj_value = self.evaluation_model.objective_function(seed_allocation)

        # run algorithm
        allocation = self.main(seed_allocation, seed_obj_value, candidates)
        
        # evaluate and store result
        self.store_allocation(self.evaluate(allocation))

    def init_protocol(self) -> DataFrame:

        '''Inits a DataFrame to protocol the optimization run.'''

        return DataFrame(columns=[OBJ_VALUE, BEST_OBJ_VALUE, STRATEGY, CUR_TIME])

    def seed(self, candidates:list) -> array:

        '''Returns a seed (allocation) for the optimization.'''

        # init a seed
        random_seed = self.init_allocation_array()
        seed = deepcopy(random_seed)

        # try to allocate and meeting restrictions for as much orders as possible
        for order_index in range(len(random_seed)):
            order_index:int

            # shuffle candidates
            candidates = self.Neighbourhood_Generator.shuffle(candidates)

            # allocate to first allocatable node_index
            for node in candidates:
                node:Node

                feedback = self.allocatable(self.orders.list[order_index], node.index)

                if feedback > 0:

                    # allocate to candidate (node_index)
                    self.allocate(self.orders.list[order_index], node.index)
                    break
            
                elif feedback > seed[order_index]:

                    # store current best feedback
                    seed[order_index] = feedback
            
            # set node_index in seed array (may be negative integer, invalid allocation)
            seed[order_index] = feedback
            
        return seed

    def allocate_seed(self, seed:array) -> None:

        '''Allocated valid node_indexes of seed (> 0).'''

        for order_index, node_index in enumerate(seed):
            order_index:int
            node_index:int

            if node_index >= 0:
                self.allocate(self.orders.list[order_index], node_index) 

    def calc_fitness(self, order_index:int, neighbour_index:int, current_node_index:int) -> float:

        ''' Evaluates cost-improvement of modifiying currently allocated node with its neighbour.
            Returns improvement as delta between allocation to neighbour and current allocation.
            A positive return value means the allocation costs descreased and viceversa.'''

        # get objects
        order = self.orders.__get__(order_index) # type: Order
        neighbour = self.nodes.__get__(index=neighbour_index) # type: Node

        # build a protype_tour to approximate route duration
        prototype_delivery = deepcopy(neighbour.delivery) # type: Delivery
        new_durations = prototype_delivery.add_order(order)
        prototype_delivery.approximate_routes(new_durations)

        if prototype_delivery.on_time(self.current_time): 

            # check if current node is a real node or a failure record to allow comparison
            if current_node_index > 0:

                # get current node
                current_node = self.nodes.__get__(index=current_node_index) # type: Node

                # compare proposed allocation with current allocation to determine improvement
                return      (current_node.supply_rate - neighbour.supply_rate) * order.volume / MAX_PAL_VOLUME \
                        +   (current_node.order_processing_rate - neighbour.order_processing_rate) * order.number_of_lines \
                        +   (current_node.stock_holding_rate - neighbour.stock_holding_rate) * order.pieces \
                        +   (current_node.tour_rate if current_node.delivery.tot_duration > 0 else 0) - neighbour.tour_rate \
                        +   (current_node.route_rate * current_node.delivery.tot_duration) - (neighbour.route_rate * prototype_delivery.tot_duration)

            else:
                # calulcate profit of allocation
                return      order.price \
                        +   neighbour.supply_rate * order.volume / MAX_PAL_VOLUME \
                        +   neighbour.order_processing_rate * order.number_of_lines \
                        +   neighbour.stock_holding_rate * order.pieces \
                        +   neighbour.tour_rate \
                        +   neighbour.route_rate * prototype_delivery.tot_duration

        else:

            # delivery not on time, invalid move, rate with bad fitness
            return - Infinity
                
    def evaluate_neighbourhood(self, neighbourhood:array, best_allocation:array) -> Union[array, array]:

        ''' Determines the fitness of all neighbours by comparing how they would improve the objective value
            in comparison to the current best allocaiton.
            Returns an array of order indexes ranked according to the fitness of the respective neighbours
            and an array of the neighbours ranked according to their fitness.'''

        fitness = []

        # calculate fitness value for each neighbour
        for order_index, neighbour_index in enumerate(neighbourhood):

            # check if node is available with current best allocation
            neighbour = self.nodes.__get__(index=neighbour_index) # type: Node

            # check if stock is available:
            if neighbour.delivery.on_time(self.current_time):

                if self.stock_available(self.orders.list[order_index], neighbour_index):
            
                    # evaluate fitness
                    fitness.append(self.calc_fitness(order_index, neighbour_index, best_allocation[order_index]))

                else:
                    # stock not available
                    fitness.append(-Infinity)
            else:
                # node not available
                fitness.append(-Infinity)

        # create arrays
        order_indexes = array(range(len(neighbourhood)))
        neighbour_fitness = array(fitness)

        # sort according to best fitness
        permutation = neighbour_fitness.argsort()[::-1]

        return order_indexes[permutation], neighbourhood[permutation], flip(sort(neighbour_fitness))

    def restrictions_met(self, order_index:int, node_index:int) -> bool:

        ''' Returns True or False based depending if the proposed node_index
            is a valid allocation for the order.'''
            
        # get order
        order = self.orders.__get__(order_index) #type: Order
        
        if self.stock_available(order, node_index):

            # check order deliverability (vehicle volume restrictions, scheduling of order proc and delivery restrictions)
            delivery = self.order_deliverable(order, node_index)

            if delivery is not None:
                
                # replace tour
                setattr(self.nodes.__get__(index=node_index), DELIVERY, delivery)
            
                return True 
        
        return False

    def nearest_nodes_candidates_generator(self, candidates:array, order:Order) -> array:

        ''' Returns an numpy array with all node indexes 
            in ascending order based on the distance to the order's delivery location.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        distances = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node_index in enumerate(candidates):
            i:int
            node_index:int

            node = self.nodes.__get__(index=node_index) # type: Node

            indexes[i] = node_index
            distances[i] = distance(node.location, order.customer.location)
        
        return indexes[distances.argsort()]

    class Neighbourhood_Generator: 

        def random(candidates:list, size:int) -> list:

            '''Generates a random neighbourhood with elements from candidate list.'''

            return np_random.choice(candidates, size=size)

        def shuffle(candidates:list) -> list:

            '''Shuffles the candidate list.'''

            np_random.shuffle(candidates)
            return candidates




    





