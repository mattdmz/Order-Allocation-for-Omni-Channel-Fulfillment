
###############################################################################################

'''This file contains all allocation rules.'''

###############################################################################################


from copy import deepcopy
from datetime import datetime
from math import  floor, sqrt
from numpy import array, concatenate, float64, zeros 
from scipy.stats import norm

from allocation.ruler import Rule
from allocation.constants import RULE_BASED
from dstrbntw.delivery import Delivery
from dstrbntw.location import distance
from dstrbntw.nodes import Node
from dstrbntw.region import Region
from parameters import ALLOC_START_TIME, ALLOC_OPERATOR, ALREADY_ALLOCATED_THRESHOLD, ORDER_PROCESSING_START, OP_END_TIME, RPL_CYCLE_DURATION
from transactions.orders import Order
from utilities.datetime import time_diff


class Nearest_Nodes(Rule):

    ''' Allocates an order to the closest node that does not violate the allocaiton restrictions.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime=None) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order) -> array:

        ''' Returns an numpy array with all node indexes 
            in ascending order based on the distance to the order's delivery location.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        distances = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(self.nodes.dict.values()):
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

    def main(self, order:Order) -> array:

        ''' Returns an numpy array with all node indexes 
            in ascending order based on the the order's delivery costs is the delivery vehicle was driving there directly.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        trsp_costs = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(self.nodes.dict.values()):
            i:int
            node:Node

            indexes[i] = node.index
            trsp_costs[i] = distance(node.location, order.customer.location) * node.route_rate \
                        + node.tour_rate if len(node.delivery.batches) == 0 else 0
        
        return indexes[trsp_costs.argsort()]


class Nearest_Already_Allocated_Nodes(Rule):

    ''' Allocates an order to the closest node that has already another order assigned and does not violate the allocaiton restrictions.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def main(self, order:Order) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on the distance to the other already allocated order's delivery location.'''

        # check if there are enough orders for the algorithm to provide variety
        nodes_allocated_to = [node.index for node in self.nodes.dict.values() if len(node.delivery.batches) > 0]

        indexes = []
        not_allocated_indexes = []
        distances = []
        not_allocated_distances = []

        for node in self.nodes.dict.values():
            node:Node

            if len(node.delivery.batches) > 0 and len(nodes_allocated_to) >= len(self.nodes.dict) * ALREADY_ALLOCATED_THRESHOLD:
                indexes.append(node.index)
                distances.append(distance(order.customer.location, node.location))
            else:
                not_allocated_indexes.append(node.index)
                not_allocated_distances.append(distance(order.customer.location, node.location))

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

    def main(self, order:Order) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on the smallest distance 
            of the order's delivery location other, 
            already allocated prser's delivery locations.'''

        # check if there are enough orders for the algorithm to provide variety
        nodes_allocated_to = [node.index for node in self.nodes.dict.values() if len(node.delivery.batches) > 0]

        indexes = []
        not_allocated_indexes = []
        distances = []
        not_allocated_distances = []

        for node in self.nodes.dict.values():
            node:Node

            if len(node.delivery.batches) > 0 and len(nodes_allocated_to) >= len(self.nodes.dict) * ALREADY_ALLOCATED_THRESHOLD:
                
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
                not_allocated_distances.append(distance(order.customer.location, node.location))

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

    def main(self, order:Order) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on the operator (min, median, max) of stock duration 
            for each article ordered at eh respective node.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        stock_duration = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(self.nodes.dict.values()):
            i:int
            node:Node

            indexes[i] = node.index

            stock_duration[i] = ALLOC_OPERATOR(list((self.stock.current_level[line.article.index, node.index] - self.stock.reserved[line.article.index, node.index])
                                    / self.demand.__getattr__("avg", line.article.index, node.index) for line in order.lines))


        return indexes[stock_duration.argsort()[::-1]]


class Dynamic_1(Rule):

    ''' Allocates the order to the node with based on a certain calculated criterium.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, self.main)

    def days_since_last_replenishment(self, node_type:int) -> float:
        
        ''' Support method for Dynamic1.
            Returns the remaining number in days until the next replenishment as floating point value.'''
        
        shops_open = datetime.combine(self.current_time.date(), ALLOC_START_TIME)
        full_days_since_replenishment = self.current_time.date().isoweekday() % RPL_CYCLE_DURATION
        open_minutes_current_day = time_diff(shops_open, self.current_time) 
        shops_close = datetime.combine(self.current_time.date(), OP_END_TIME[node_type])

        return full_days_since_replenishment + (open_minutes_current_day / time_diff(shops_open, shops_close))

    def expected_stock_level_at_end_of_rpm_cyle(self, article_index:int, node_index:int, days_since_rplm:float) -> int:

        ''' Support method for Dynamic1.
            Returns the expected stock level for a certain article at the end 
            of the replenishment cycle == before replenishment.'''

        return     (self.stock.current_level[article_index, node_index] \
                -  self.stock.reserved[article_index, node_index]) \
                -  RPL_CYCLE_DURATION * self.demand.__getattr__("avg", article_index, node_index) * (floor(days_since_rplm) - days_since_rplm + 1) \
                / sqrt(self.demand.__getattr__("var", article_index, node_index) * (floor(days_since_rplm) - days_since_rplm + 1))  

    def marginal_op_and_delivery_costs(self, order:Order, node:Node) -> float:

        '''Returns the delivery costs if the order is allocated at the examined node.'''

        prototype_delivery = deepcopy(node.delivery) #type:Delivery
        prototype_delivery.add_order(order)
        prototype_delivery.build_routes()
        delivery_costs =   (prototype_delivery.tot_duration * node.route_rate) \
                         - (node.delivery.tot_duration * node.route_rate) \
                         + (node.tour_rate if len(node.delivery.batches) == 0 else 0)

        return order.number_of_lines * node.order_processing_rate + delivery_costs

    def marginal_costs(self, order:Order, node:Node):
        
        ''' Support method for Dynamic1.
            Returns marginal holding and backorder costs of maintaining 
            one additional unit of article article_index at node node_index.'''

        marg_holding_and_backorder_costs = []
        days_since_rplm = self.days_since_last_replenishment(node.node_type)

        for line in order.lines:
            line:Order.Line

            # calculate cumulative distribution function for the expected stock at the end of the replenishment cycle
            cdf = norm.cdf(self.expected_stock_level_at_end_of_rpm_cyle(line.article.index, node.index, days_since_rplm))

            # calculate and append marginal costs
            marg_holding_and_backorder_costs.append(node.stock_holding_rate * cdf - node.supply_rate * (1 - cdf))

        return ALLOC_OPERATOR(marg_holding_and_backorder_costs) + self.marginal_op_and_delivery_costs(order, node)

    def main(self, order:Order) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on marginal holding and backorder costs of allocating 
            the order at the node.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        marginal_costs = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(self.nodes.dict.values()):
            i:int
            node:Node
            
            indexes[i] = node.index
            marginal_costs[i] = self.marginal_costs(order, node)
        
        return indexes[marginal_costs.argsort()]
