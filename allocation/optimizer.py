
###############################################################################################

'''This file contains the parent class for all optimizers.'''

###############################################################################################

from copy import deepcopy
from datetime import datetime
from numpy import array, empty, float64, full, Infinity, zeros
from pandas import DataFrame
from typing import Union

from allocation.constants import DELIVERY, STOCK_NOT_AVAILABLE
from allocation.allocator import Allocator
from allocation.moves import Moves
from dstrbntw.delivery import Delivery, create_prototype
from dstrbntw.location import distance
from dstrbntw.nodes import Node
from dstrbntw.region import Region
from parameters import MAX_PAL_VOLUME
from protocols.constants import ALLOC_ARR, BEST_OBJ_VALUE, CUR_TIME, OBJ_VALUE, STRATEGY
from transactions.orders import Order
from transactions.sales import Sale

class Optimizer(Allocator):

    '''Parent class for all optimizers.'''

    def __init__(self, region: Region, current_time: datetime, main) -> None:
        
        ''' Inits Allocator parents class and creates an allocation to be used as seed (starting allocation)
            for the optimizaiton.'''

        super().__init__(region, current_time)

        # store main method of child class
        self.main = main

        revenue,  diminuished_stock_value = self.handle_sales()
        self.sales.store_results(revenue, diminuished_stock_value)

        # set laceholder for best nodes
        self.best_nodes = []

        # init a DataFrame to protocol the optimization run
        self.protocol = self.init_protocol()

        # define list of candidate nodes for all orders
        self.moves = Moves(self.candidates_generator())

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

    def handle_sales(self) -> Union[float, float]:

        ''' Tries to close the sales, collects the revenues and the number of pieces sold.
            Protocol lines which could not be closed.'''

        revenue = 0
        diminuished_stock_value = 0

        for sale in self.sales.list:
            sale:Sale
            
            rev, pieces_sold = self.sell(sale)

            if rev > 0:
                # collect revenue and pieces sold
                revenue += rev
                diminuished_stock_value += sale.node.stock_holding_rate * pieces_sold
                # reset counters
                rev = 0
                pieces_sold = 0 

        return revenue,  diminuished_stock_value 

    def init_protocol(self) -> DataFrame:

        '''Inits a DataFrame to protocol the optimization run.'''

        return DataFrame(columns=[OBJ_VALUE, BEST_OBJ_VALUE, STRATEGY, CUR_TIME, ALLOC_ARR])

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
        candidate_nodes = self.moves.candidate_list_of_nodes[order_index]

        if len(candidate_nodes) > 1:

            nodes = empty(shape=(len(candidate_nodes)), dtype=Node)
            distances = zeros(shape=(len(candidate_nodes)), dtype=float64)

            for i, node in enumerate(candidate_nodes):
                i:int
                node:Node

                nodes[i] = node
                distances[i] = distance(order.customer.location, node.location)
            
            return nodes[distances.argsort()]

        else:

            # no allocation possible for this order
            return [STOCK_NOT_AVAILABLE]

    def cheapest_delivery_seed_generator(self, order_index:int, order:Order) -> array:

        ''' Returns an numpy array with all node indexes of the candidates
            in ascending order based on expected delivery costs of allocating 
            the order at the node.'''

        candidate_nodes = self.moves.candidate_list_of_nodes[order_index]

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
            return [STOCK_NOT_AVAILABLE]

    def seed_generator(self) -> array:

        '''Returns a seed (allocation) for the optimization.'''

        # init a seed
        seed = self.init_allocation_array()

        # try to allocate and meeting restrictions for as much orders as possible
        for order_index, order in enumerate(self.orders.list):
            order:Order

            if order.allocated_node is None:

                #candidate_nodes = self.cheapest_delivery_seed_generator(order_index, order)
                candidate_nodes = self.nearest_nodes_seed_generator(order_index, order)

                if candidate_nodes[0] != STOCK_NOT_AVAILABLE:

                    # allocate to first allocatable node in candidates
                    for node in candidate_nodes:
                        node:Node

                        # check if order would be allocatable
                        feedback = self.allocatable(order, node.index)

                        if feedback > 0:

                            # allocate to candidate (node_index)
                            self.allocate(order, node.index)
                            seed[order_index] = node.index
                            break
                    
                        elif feedback > seed[order_index]:

                            # store current best feedback
                            seed[order_index] = feedback

                else:
                    # stock not available for this order at any node
                    seed[order_index] = STOCK_NOT_AVAILABLE
            
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
        current_node = self.orders.list[order_index].allocated_node # type: Node

        #check if order is already allocated at node
        if order in neighbour.delivery.orders_to_deliver:
            # order is already in delivery tour, optimize tour only
            prototype_delivery = neighbour.delivery           # type: Delivery
        else:
            # create copy and create test tour and add order to it
            prototype_delivery = create_prototype(neighbour.delivery, order)

        # check if current node is a real node or a failure record to allow comparison
        if isinstance(current_node, Node):

            # compare proposed allocation with current allocation to determine improvement
            return      (current_node.supply_rate - neighbour.supply_rate) * order.volume / MAX_PAL_VOLUME \
                    +   (current_node.order_processing_rate - neighbour.order_processing_rate) * order.number_of_lines \
                    +   (current_node.stock_holding_rate - neighbour.stock_holding_rate) * order.pieces \
                    +   (current_node.route_rate * current_node.delivery.tot_duration) - (neighbour.route_rate * prototype_delivery.tot_duration) \
                    +   (current_node.tour_rate if current_node.delivery.tot_duration > 0 else 0) \
                    -   (neighbour.tour_rate if prototype_delivery.tot_duration > 0 else 0) \
                    

        else:
            # calulcate profit of allocation
            return      order.price \
                    -   neighbour.supply_rate * order.volume / MAX_PAL_VOLUME \
                    -   neighbour.order_processing_rate * order.number_of_lines \
                    -   neighbour.stock_holding_rate * order.pieces \
                    -   neighbour.tour_rate \
                    -   neighbour.route_rate * prototype_delivery.tot_duration

    def calculate_move_fitness(self) -> Union[array, array]:

        ''' Determines the fitness of all neighbours by comparing how they would improve the objective value
            in comparison to the current best allocation.'''

        # init fitness array
        x = len(self.orders.list)
        y = len(self.nodes.dict)
        fitness = full((y, x), -Infinity)
        move_indexes = full((y, x), None, dtype=object)

        # calculate fitness value for each neighbour
        for order_index, neighbours in enumerate(self.moves.candidate_list_of_nodes):
            order_index:int
            neighbours:list

            # determine fitness for candidate neibours
            for neighbour in neighbours:
                neighbour:Node

                # evaluate fitness for moves on order_index 
                move_indexes[neighbour.index, order_index] = (neighbour.index, order_index)
                fitness[neighbour.index, order_index]= self.calc_fitness(order_index, neighbour.index)

        return  move_indexes, fitness
         
    def update_fitness(self, order_index_move_performed_on:int, added_node_index:int, dropped_node_index:int) -> None:

        ''' Updates the fitness of moves with added_node_index and dropped_node_index.'''

        # recaluculate fitness
        for order_index in range(len(self.orders.list)):

            # for order_indexes other than order_index_move_performed_on
            if order_index != order_index_move_performed_on and self.moves.fitness[dropped_node_index, order_index] != -Infinity:
                # node dropped
                self.moves.fitness[dropped_node_index, order_index] = self.calc_fitness(order_index, dropped_node_index)

            if order_index != order_index_move_performed_on and self.moves.fitness[added_node_index, order_index] != -Infinity:
                # node added
                self.moves.fitness[added_node_index, order_index] = self.calc_fitness(order_index, added_node_index)

            # for order_index_move_performed_on
            elif order_index == order_index_move_performed_on:
                # node dropped
                self.moves.fitness[dropped_node_index, order_index] = deepcopy(self.moves.fitness[added_node_index, order_index]) * (-1)
                self.moves.move_indexes[dropped_node_index, order_index] = (dropped_node_index, order_index)
                # node added
                self.moves.fitness[added_node_index, order_index] = 0.0
                self.moves.move_indexes[added_node_index, order_index] = (added_node_index, order_index)

        # recalculate fitness based on move carried out
        for node in self.moves.candidate_list_of_nodes[order_index_move_performed_on]:
            node:Node

            if node.index != added_node_index and node.index != dropped_node_index and \
                self.moves.fitness[node.index, order_index_move_performed_on] != -Infinity:
                self.moves.fitness[node.index, order_index_move_performed_on] = self.calc_fitness(order_index_move_performed_on, node.index)

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
    
    def protocol_iter(self, iter:int, obj_value:float, best_obj_value:float, current_strategy:str, cur_time, allocation:array) -> None:
    
        '''Protocols an iteration.'''

        self.protocol.loc[iter] = {     OBJ_VALUE: obj_value, 
                                        BEST_OBJ_VALUE: best_obj_value, 
                                        STRATEGY: current_strategy,
                                        CUR_TIME: cur_time,
                                        ALLOC_ARR: str(allocation)
        }

    def memorize_best_nodes(self, new_allocation:array) -> None:

        '''Stores a copy of node allocated to or the failure cause for each order.'''

        best_nodes = []

        for order_index in range(len(self.orders.list)):
            order_index:int

            if new_allocation[order_index] >= 0:
                best_nodes.append(deepcopy(self.nodes.__get__(index=new_allocation[order_index])))
            else:
                best_nodes.append(deepcopy(new_allocation[order_index]))

        self.best_nodes = best_nodes        