
from copy import deepcopy
from datetime import datetime
from numpy import array, flip, random as np_random, sort
from os import path
from pandas import DataFrame
from typing import Union

from allocation.constants import DELIVERY
from allocation.allocator import Allocator
from configs import OUTPUT_DIR
from dstrbntw.constants import CUSTOMER
from dstrbntw.delivery import Delivery
from dstrbntw.nodes import Node
from dstrbntw.region import Region
from parameters import MAX_PAL_VOLUME
from protocols.constants import BEST_OBJ_VALUE, ITER, OBJ_VALUE, RUN_ID, STRATEGY
from transactions.orders import Order
from utilities.expdata import write_df

class Optimizer(Allocator):

    '''Parent class for all optimizers.'''

    def __init__(self, region: Region, current_time: datetime, cut_off_time: datetime, main) -> None:
        
        ''' Inits Allocator parents class and creates an allocation to be used as seed (starting allocation)
            for the optimizaiton.'''

        super().__init__(region, current_time, cut_off_time)

        # store main method of child class
        self.main = main

        # init a DataFrame to protocol the optimization run
        self.protocol = self.init_protocol()

        # seed 
        seed_allocation = self.seed()
        
        # determine obj_value of seed
        self.prepare_evaluation()
        seed_obj_value = self.evaluation_model.objective_function(seed_allocation)

        # run algorithm, evaluate and store result
        allocation = self.main(seed_allocation, seed_obj_value)
        self.store_allocation(self.evaluate(allocation))
        self.export_protocol()

    def init_protocol(self) -> DataFrame:

        '''Inits a DataFrame to protocol the optimization run.'''

        return DataFrame(columns=[ITER, OBJ_VALUE, BEST_OBJ_VALUE, STRATEGY])

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

        # get objects
        order = self.orders.__get__(order_index) # type: Order
        neighbour = self.nodes.__get__(index=neighbour_index) # type: Node
        current_node = self.nodes.__get__(index=current_node_index) # type: Node

        # build a protype_tour to approximate route duration
        prototype_delivery = deepcopy(neighbour.delivery) #type: Delivery
        prototype_delivery.approximate_routes(prototype_delivery.calc_duration_to_other_stops(self.orders.__getattr__(order_index, CUSTOMER)))

        print("supply costs improvement: ", (current_node.supply_rate - neighbour.supply_rate) * order.volume / MAX_PAL_VOLUME)
        print("order proc costs improvement: ", (current_node.order_processing_rate - neighbour.order_processing_rate) * order.lines)
        print("diminuished stock value improvement: ", (current_node.stock_holding_rate - neighbour.stock_holding_rate) * order.pieces)
        print("route costs improvement: ", (current_node.route_rate * current_node.delivery.tot_duration) - (neighbour.route_rate * prototype_delivery.tot_duration))
        print("tour costs improvement: ", (current_node.tour_rate * 1 if prototype_delivery.tot_duration > 0 else 0) - neighbour.tour_rate)
        
        return      (current_node.supply_rate - neighbour.supply_rate) * order.volume / MAX_PAL_VOLUME \
                +   (current_node.order_processing_rate - neighbour.order_processing_rate) * order.lines \
                +   (current_node.stock_holding_rate - neighbour.stock_holding_rate) * order.pieces \
                +   (current_node.tour_rate * 1 if prototype_delivery.tot_duration > 0 else 0) - neighbour.tour_rate \
                +   (current_node.route_rate * current_node.delivery.tot_duration / len(current_node.delivery.orders_to_deliver)) - \
                -   (neighbour.route_rate * prototype_delivery.tot_duration / len(prototype_delivery.orders_to_deliver))
                
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

    def export_protocol(self) -> None:

        ''' Exports the protocol of an optimization run directly to the output driectory.
            Delets the protocol.'''

        write_df(   self.protocol, RUN_ID + "_optimization_protocol_" + self.current_time, 
                    path.join(OUTPUT_DIR, RUN_ID), header=True, index=True)

        del self.protocol

    class Neighbourhood_Generator: 

        def random(self, candidates:list, size:int) -> array:

            '''Generates a random neighbourhood with elements from candidate list.'''

            return np_random.choice(candidates, size=size)



    





