
###############################################################################################

'''This file contains all allocation rules.'''

###############################################################################################


from copy import deepcopy
from datetime import datetime
from numpy import array, concatenate, float64, zeros

from allocation.ruler import Rule
from allocation.constants import RULE_BASED
from dstrbntw.delivery import Delivery
from dstrbntw.location import distance
from dstrbntw.nodes import Node
from dstrbntw.region import Region
from parameters import ALLOC_OPERATOR
from transactions.orders import Order


class Nearest_Nodes(Rule):

    ''' Allocates an order to the closest node that does not violate the allocaiton restrictions.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime=None) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order, candidates:list) -> array:

        ''' Returns an numpy array with all node indexes 
            in ascending order based on the distance to the order's delivery location.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        distances = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(candidates):
            i:int
            node:Node

            indexes[i] = node.index
            distances[i] = distance(node.location, order.customer.location)
        
        return indexes[distances.argsort()]


class Chepest_Direct_Delivery(Rule):

    ''' Allocates an order to the node having the least transportation costs.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime=None) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order, candidates:list) -> array:

        ''' Returns an numpy array with all node indexes 
            in ascending order based on the the order's delivery costs is the delivery vehicle was driving there directly.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        trsp_costs = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(candidates):
            i:int
            node:Node

            indexes[i] = node.index
            trsp_costs[i] = distance(node.location, order.customer.location) * node.route_rate \
                        + node.tour_rate if len(node.delivery.batches) == 0 else 0
        
        return indexes[trsp_costs.argsort()]


class Cheapest_Delivery(Rule):

    ''' Allocates orders based on the expected delivery costs for the order at the node.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order, candidates:list) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on expected delivery costs of allocating 
            the order at the node.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        expected_costs = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(candidates):
            i:int
            node:Node
            
            indexes[i] = node.index
            expected_costs[i] = self.delivery_costs_of_detour(order, node)
        
        return indexes[expected_costs.argsort()]


class Nearest_Already_Allocated_Nodes(Rule):

    ''' Allocates an order to the closest node that has already another order assigned and does not violate the allocaiton restrictions.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order, candidates:list) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on the distance to the other already allocated order's delivery location.'''

        indexes = []
        not_allocated_indexes = []
        distances = []
        not_allocated_distances = []

        for node in candidates:
            node:Node

            if len(node.delivery.batches) > 0:
                indexes.append(node.index)
                distances.append(distance(order.customer.location, node.location))
            else:
                not_allocated_indexes.append(node.index)
                not_allocated_distances.append(self.marginal_costs(order, node)) #distance(order.customer.location, node.location))

        #transfrom to numpy arrays to perfrom argsort
        indexes = array(indexes, dtype=int)
        distances = array(distances)
        not_allocated_indexes = array(not_allocated_indexes, dtype=int)
        not_allocated_distances = array(not_allocated_distances)

        return concatenate((indexes[distances.argsort()], not_allocated_indexes[not_allocated_distances.argsort()]))


class Allocation_Of_Nearest_Order(Rule):

    ''' Allocates an order to the node where the the order's delivery location is the least distant from was allocated to.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order, candidates:list) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on the smallest distance 
            of the order's delivery location other, 
            already allocated prser's delivery locations.'''

        indexes = []
        not_allocated_indexes = []
        distances = []
        not_allocated_distances = []

        for node in candidates:
            node:Node

            if len(node.delivery.batches) > 0:
                
                indexes.append(node.index)
                dists = []

                for batch in node.delivery.batches:
                    for order in batch.orders:
                        order:Order

                        distance_to_orders_delivery_location = distance(order.customer.location, node.location)
                        dists.append(distance_to_orders_delivery_location)

                distances.append(min(dists))

            else:
                not_allocated_indexes.append(node.index)
                not_allocated_distances.append(self.marginal_costs(order, node)) #distance(order.customer.location, node.location))

        # transfrom to numpy arrays to perfrom argsort
        indexes = array(indexes, dtype=int)
        distances = array(distances)
        not_allocated_indexes = array(not_allocated_indexes, dtype=int)
        not_allocated_distances = array(not_allocated_distances)

        return concatenate((indexes[distances.argsort()], not_allocated_indexes[not_allocated_distances.argsort()]))


class Longest_Stock_Duration(Rule):

    ''' Allocates the order to the node with the longest max (min, median, max) stock duration among all articles ordered.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order, candidates:list) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on the operator (min, median, max) of stock duration 
            for each article ordered at eh respective node.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        stock_duration = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(candidates):
            i:int
            node:Node

            indexes[i] = node.index

            stock_duration[i] = ALLOC_OPERATOR(list((self.stock.current_level[line.article.index, node.index] - self.stock.reserved[line.article.index, node.index])
                                    / self.demand.__getattr__("avg", line.article.index, node.index) for line in order.lines))


        return indexes[stock_duration.argsort()[::-1]]


class Dynamic_1(Rule):

    ''' Allocates orders based on amrginal stock holding and supply costs + expected delivery costs for the order at the node.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order, candidates:list) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on marginal holding and backorder costs of allocating 
            the order at the node.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        marginal_costs = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(candidates):
            i:int
            node:Node
            
            indexes[i] = node.index
            marginal_costs[i] = self.marginal_costs(order, node)
        
        return indexes[marginal_costs.argsort()]


class Modified_Dynamic_1(Rule):

    ''' Allocates orders based on the expected fulfillment costs for the order at the node.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order, candidates:list) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on expected costs of allocating 
            the order at the node.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        expected_costs = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(candidates):
            i:int
            node:Node
            
            indexes[i] = node.index
            expected_costs[i] = self.expected_costs(order, node)
        
        return indexes[expected_costs.argsort()]


class Operational_Costs(Rule):

    ''' Allocates orders based on the expected supply and order processing costs for the order at the node.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order, candidates:list) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on expected supply and order processing costs of allocating 
            the order at the node.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        operational_costs = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(candidates):
            i:int
            node:Node
            
            indexes[i] = node.index
            operational_costs[i] = self.supply_costs(order, node) + self.order_processing_costs(order, node)
        
        return indexes[operational_costs.argsort()]

