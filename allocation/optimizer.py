
###############################################################################################

'''This file contains the parent class for all optimizers.'''

###############################################################################################

from copy import deepcopy
from datetime import datetime
from numpy import array, empty, flip, float64, full, Infinity, random as np_random, sort, zeros
from pandas import DataFrame
from typing import Union

from allocation.constants import DELIVERY, DELIVERY_NOT_EXECUTABLE, STOCK_NOT_AVAILABLE
from allocation.allocator import Allocator
from allocation.neighbourhood import Neighbourhood
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

        # set laceholder for best nodes
        self.best_nodes = []

        # init a DataFrame to protocol the optimization run
        self.protocol = self.init_protocol()

        # define list of candidate nodes for all orders
        self.neighbourhood = Neighbourhood(self.candidates_generator())

        # create seed allocation and calc obj value
        seed_allocation = self.seed_generator()
        self.memorize_best_nodes(seed_allocation)
        self.prepare_evaluation()
        seed_obj_value = self.evaluation_model.objective_function(seed_allocation)

        # run algorithm
        allocation = self.main(seed_allocation, seed_obj_value)
        
        # evaluate and store result
        self.prepare_evaluation()
        self.store_allocation(self.evaluate(allocation))

    def init_protocol(self) -> DataFrame:

        '''Inits a DataFrame to protocol the optimization run.'''

        return DataFrame(columns=[OBJ_VALUE, BEST_OBJ_VALUE, STRATEGY, CUR_TIME])

    def candidates_generator(self) -> list:

        ''' Returns a list of lists with all nodes having stock for 
            potentially allocating the order of the respective column.'''

        candidates = []

        for order in self.orders.list:
            order:Order
            
            # generate candidate list and concatenate to candidate_matrix
            candidates.append(self.determine_candidates(order))

        return candidates

    def nearest_nodes_seed_generator(self, order_index:int, order:Order) -> array:

        ''' Returns an numpy array with all node indexes of the candidate nodes
            in ascending order based on the distance to the order's delivery location.'''

        # filter only nodes as candidates which are not yet allocated to an order
        candidate_nodes = self.neighbourhood.lists[order_index]

        nodes = empty(shape=(len(candidate_nodes)), dtype=Node)
        distances = zeros(shape=(len(candidate_nodes)), dtype=float64)

        for i, node in enumerate(candidate_nodes):
            i:int
            node:Node

            nodes[i] = node
            distances[i] = distance(order.customer.location, node.location)
        
        return nodes[distances.argsort()]

    def cheapest_delivery_seed_generator(self, order_index:int, order:Order) -> array:

        ''' Returns an numpy array with all node indexes of the candidates
            in ascending order based on expected delivery costs of allocating 
            the order at the node.'''

        candidate_nodes = self.neighbourhood.lists[order_index]

        if len(candidate_nodes) > 1:

            nodes = empty(shape=(len(candidate_nodes)), dtype=Node)
            expected_costs = zeros(shape=(len(candidate_nodes)), dtype=float64)

            for i, node in enumerate(candidate_nodes):
                i:int
                node:Node
                
                nodes[i] = node
                expected_costs[i] = self.delivery_costs_of_detour(order, node)
            
            return nodes[expected_costs.argsort()]

        else:

            # no allocation possible for this order
            return STOCK_NOT_AVAILABLE

    def seed_generator(self) -> array:

        '''Returns a seed (allocation) for the optimization.'''

        # init a seed
        seed = self.init_allocation_array()

        # try to allocate and meeting restrictions for as much orders as possible
        for order_index, order in enumerate(self.orders.list):
            order:Order

            if order.allocated_node is None:

                # allocate to first allocatable node in candidates
                for node in self.cheapest_delivery_seed_generator(order_index, order):
                    node:Node

                    # check if order would be allocatable
                    feedback = self.allocatable(order, node.index)

                    if feedback > 0:

                        # allocate to candidate (node_index)
                        self.allocate(order, node.index)
                        break
                
                    elif feedback > seed[order_index]:

                        # store current best feedback
                        seed[order_index] = feedback
                
                # set node_index in seed array (may be negative integer, invalid allocation)
                seed[order_index] = feedback
            
            else:
                # use current allocation
                seed[order_index] = order.allocated_node.index
            
        return seed

    def calc_fitness(self, order_index:int, neighbour_index:int) -> float:

        ''' Evaluates cost-improvement of modifiying currently allocated node with its neighbour.
            Returns improvement as delta between allocation to neighbour and current allocation.
            A positive return value means the allocation costs descreased and viceversa.'''

        # get objects
        order = self.orders.list[order_index] # type: Order
        neighbour = self.nodes.__get__(index=neighbour_index) # type: Node
        current_best_node = self.best_nodes[order_index] # type: Node

        #check if order is already allocated at node
        if order in neighbour.delivery.orders_to_deliver:
            # order is already in delivery tour, optimize tour only
            prototype_delivery = neighbour.delivery           # type: Delivery
        else:
            # create copy and create test tour and add order to it
            prototype_delivery = deepcopy(neighbour.delivery) # type: Delivery
            prototype_delivery.add_order(order)

        # optimize routes
        prototype_delivery.build_routes(max_iterations_ls=0)

        #prototype_delivery.build_routes(max_iterations_ls=10)
        #print("10 iters: ", prototype_delivery.tot_duration)
        #prototype_delivery.build_routes(max_iterations_ls=40)
        #print("40 iters: ", prototype_delivery.tot_duration)

        # check if current node is a real node or a failure record to allow comparison
        if isinstance(current_best_node, Node):

            # compare proposed allocation with current allocation to determine improvement
            return      (current_best_node.supply_rate - neighbour.supply_rate) * order.volume / MAX_PAL_VOLUME \
                    +   (current_best_node.order_processing_rate - neighbour.order_processing_rate) * order.number_of_lines \
                    +   (current_best_node.stock_holding_rate - neighbour.stock_holding_rate) * order.pieces \
                    +   (current_best_node.tour_rate if current_best_node.delivery.tot_duration > 0 else 0) - neighbour.tour_rate \
                    +   (current_best_node.route_rate * current_best_node.delivery.tot_duration) - (neighbour.route_rate * prototype_delivery.tot_duration)

        else:
            # calulcate profit of allocation
            return      order.price \
                    +   neighbour.supply_rate * order.volume / MAX_PAL_VOLUME \
                    +   neighbour.order_processing_rate * order.number_of_lines \
                    +   neighbour.stock_holding_rate * order.pieces \
                    +   neighbour.tour_rate \
                    +   neighbour.route_rate * prototype_delivery.tot_duration

    def calculate_neighbourhood_fitness(self) -> None:

        ''' Determines the fitness of all neighbours by comparing how they would improve the objective value
            in comparison to the current best allocaiton.'''

        number_of_neighbours = 0

        # calculate fitness value for each neighbour
        for order_index, neighbours in enumerate(self.neighbourhood.lists):
            order_index:int
            neighbours:list

            # determine fitness for candidate neibours
            for neighbour_index, neighbour in enumerate(neighbours):
                neighbour_index:int
                neighbour:Node
        
                # evaluate fitness
                index = number_of_neighbours + neighbour_index
                self.neighbourhood.order_indexes[index] = order_index
                self.neighbourhood.neighbour_indexes[index] = neighbour.index
                self.neighbourhood.fitness[index] = self.calc_fitness(order_index, neighbour.index)

            number_of_neighbours = len(neighbours)

    def calculate_node_fitness(self, node_index:int) -> None:

        ''' Determines the fitness of all neighbours by comparing how they would improve the objective value
            in comparison to the current best allocaiton.
            Returns an array of order indexes ranked according to the fitness of the respective neighbours
            and an array of the neighbours ranked according to their fitness.'''

        if node_index is not None:

            # calculate fitness for all nodes affected by a change (=node)
            for fitness_index, neighbour_index in enumerate(self.neighbourhood.neighbour_indexes):
                fitness_index:int
                neighbour_index:int

                if neighbour_index == node_index:
                    
                    # detemrine order index
                    order_index = self.neighbourhood.order_indexes[fitness_index]
                    
                    # recalculate fitness
                    #print("fitness index:", fitness_index, "neighbour_fitness:", self.neighbourhood.fitness[fitness_index])
                    #print("calc fitness for:", node_index)
                    self.neighbourhood.fitness[fitness_index] = self.calc_fitness(order_index, node_index)
                    #print("fitness index:", fitness_index, "neighbour_fitness:", self.neighbourhood.fitness[fitness_index])

    def restrictions_met(self, order_index:int, node_index:int) -> bool:

        ''' Returns True or False based depending if the proposed node_index
            is a valid allocation for the order.'''
            
        # get order
        order = self.orders.list[order_index] #type: Order

        # check order deliverability (vehicle volume restrictions, scheduling of order proc and delivery restrictions)
        delivery = self.order_deliverable(order, node_index)

        if delivery is not None:
            
            # replace tour
            setattr(self.nodes.__get__(index=node_index), DELIVERY, delivery)
        
            return True 
        
        return False
    
    def protocol_iter(self, iter:int, approx_obj_value:float, best_obj_value:float, current_strategy:str, cur_time, new_allocation:array) -> None:
    
        '''Protocols an iteration.'''

        print(  "iter", iter, ": obj_value ", approx_obj_value, " best_obj_value", best_obj_value, 
                ", alloc: ", new_allocation) #", tabu_list_len: ", self.tabu_add_tenure(iter, len(new_allocation)), 

        self.protocol.loc[iter] = {     OBJ_VALUE: approx_obj_value, 
                                        BEST_OBJ_VALUE: best_obj_value, 
                                        STRATEGY: current_strategy,
                                        CUR_TIME: cur_time
        }

    def memorable(self, new_obj_value:float) -> bool:
    
        ''' Retunrs True or False depending if the new_allocation is memorable or not.
            Memorable = True if new_obj_value > obj_value of the last element of the memory list'''

        return True if len(self.memory_list) < self.memory_length or self.memory_list[len(self.memory_list) -1][OBJ_VALUE] < new_obj_value else False

    def memorize_best_nodes(self, new_allocation:array) -> None:

        '''Stores a copy of node allocated to or the failure cause for each order.'''

        best_nodes = []

        for order_index, order in enumerate(self.orders.list):
            order:Order

            if order.allocated_node != None:
                best_nodes.append(deepcopy(self.nodes.__get__(index=new_allocation[order_index])))
            else:
                best_nodes.append(deepcopy(new_allocation[order_index]))

        self.best_nodes = best_nodes        