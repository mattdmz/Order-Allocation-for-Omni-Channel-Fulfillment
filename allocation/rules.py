
###############################################################################################

'''This file contains all allocation rules.'''

###############################################################################################


from datetime import datetime, time
from math import sqrt
from numpy import array, concatenate, float64, zeros 
from scipy.stats import norm

from allocation.ruler import Rule
from allocation.constants import RULE_BASED
from dstrbntw.location import distance
from dstrbntw.nodes import Node
from dstrbntw.region import Region
from parameters import ORDER_PROCESSING_START, OP_END_TIME, RPL_CYCLE_DURATION
from transactions.orders import Order
from utilities.datetime import time_diff


class Nearest_Nodes(Rule):

    ''' Allocates an order to the closest node that does not violate the allocaiton restrictions.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime, cut_off_time:datetime, operator:str=None) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, cut_off_time, operator, self.main)

    def main(self, order:Order, operator:str) -> array:

        ''' Returns an numpy array with all node indexes (of nodes accepting orders only)
            in ascending order based on the distance to the order's delivery location.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        distances = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(self.nodes.dict.values()):
            i:int
            node:Node

            indexes[i] = node.index
            distances[i] = distance(node.location, order.customer.location)
        
        return indexes[distances.argsort()]


class Nearest_Already_Allocated_Nodes(Rule):

    ''' Allocates an order to the closest node that has already another order assigned and does not violate the allocaiton restrictions.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime, cut_off_time:datetime, operator:str) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, cut_off_time, operator, self.main)

    def main(self, order:Order, operator:str) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on the distance to the other already allocated order's delivery location.'''

        nodes_allocated_to  = (order.allocated_node for order in self.orders.allocated)

        indexes = not_allocated_indexes = []
        distances = not_allocated_distances = []

        for node in self.nodes.dict.values():
            node:Node

            if node in nodes_allocated_to:
                indexes.append(order.allocation.index)
                distances.append(distance(order.customer.location, node.location))
            else:
                not_allocated_indexes.append(order.allocation.index)
                not_allocated_distances.append(distance(order.customer.location, node.location))

        #transfrom to numpy arrays to perfrom argsort
        indexes = array(indexes)
        distances = array(distances)
        not_allocated_indexes = array(not_allocated_indexes)
        not_allocated_distances = array(not_allocated_distances)

        return concatenate(indexes[distances.argsort()], not_allocated_indexes[not_allocated_distances.argsort()])


class Smallest_Demand_Variance(Rule):

    ''' Allocates an order to the node with the smallest max (min/median) demand variance for all the articles ordered.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime, cut_off_time:datetime, operator:str) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, cut_off_time, operator, self.main)

    def main(self, order:Order, operator:str) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on the smallest variance.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        variances = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(self.nodes.dict.values()):
            i:int
            node:Node

            indexes[i] = node.index
            variances[i] = operator(self.demand.__getattr__("var", line.article.index, node.index) for line in order.lines)

        return indexes[variances.argsort()]


class Longest_Stock_Duration(Rule):

    ''' Allocates the order to the node with the longest max (min, median, max) stock duration among all articles ordered.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime, cut_off_time:datetime, operator:str) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, cut_off_time, operator, self.main)

    def main(self, order:Order, operator:str) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on the operator (min, median, max) of stock duration 
            for each article ordered at eh respective node.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        stock_duration = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(self.nodes.dict.values()):
            i:int
            node:Node

            indexes[i] = node.index
            stock_duration[i] = operator((self.stock.current_level[line.article.index, node.index] 
                                        - self.demand.__getattr__("avg", line.article.index, node.index)) for line in order.lines)

        return indexes[stock_duration.argsort()[::-1]]


class Dynamic_1(Rule):

    ''' Allocates the order to the node with based on a certain calculated criterium.'''

    __type__ = RULE_BASED

    def __init__(self, region:Region, current_time:datetime, cut_off_time:datetime, operator:str) -> None:

        '''Inits parent class.'''
        
        super().__init__(region, current_time, cut_off_time, operator, self.main)

    def remaining_days_until_replenishment(self, node_type:int) -> float:
        
        ''' Support method for Dynamic1.
            Returns the remaining number in days until the next replenishment as floating point value.'''
        
        shops_open = datetime.combine(self.current_time.date(), time(8, 0, 0))
        full_days_to_next_replenishment =  (RPL_CYCLE_DURATION - ((self.current_time.date() - ORDER_PROCESSING_START).days % RPL_CYCLE_DURATION) - 1)
        opening_minutes = time_diff(shops_open, OP_END_TIME[node_type])
        remaining_time_current_day = time_diff(shops_open, self.current_time)

        return (full_days_to_next_replenishment * opening_minutes + remaining_time_current_day) / opening_minutes

    def expected_stock_level_at_end_of_rpm_cyle(self, article_index:int, node_index:int, days_until_replenishment:int) -> int:

        ''' Support method for Dynamic1.
            Returns the expected stock level for a certain article at the end 
            of the replenishment cycle == before replenishment.'''
        
        return self.stock.current_level[article_index, node_index] - (self.demand.__get__("avg", article_index, node_index) * days_until_replenishment) \
                / (sqrt(self.demand.__get__("var", article_index, node_index)) * sqrt(days_until_replenishment))

    def marg_holding_backorder_cost(self, order:Order, node:Node, operator:str):
        
        ''' Support method for Dynamic1.
            Returns marginal holding and backorder costs of maintaining 
            one additional unit of article article_index at node node_index.'''

        marginal_costs = []
        days_until_replenishment = self.expected_stock_level_at_end_of_rpm_cyle(node.node_type)

        for line in order.lines:
            line:Order.Line

            # calculate cumulative distribution function for the expected stock at the end of the replenishment cycle
            cdf = norm.cdf(self.expected_stock_level_at_end_of_rpm_cyle(line.article.index, node.index, days_until_replenishment))

            # calculate and append marginal costs
            marginal_costs.append(node.stock_holding_rate * cdf - order.supply_rate(node) * (1 - cdf))
        
        # return operator of marginal costs (min, modus, max)
        return operator(marginal_costs)

    def main(self, order:Order, operator) -> array:

        ''' Returns an numpy array with all node indexes
            in ascending order based on marginal holding and backorder costs of allocating 
            the order at the node.'''

        indexes = zeros(shape=(len(self.nodes.dict)), dtype=int)
        marginal_costs = zeros(shape=(len(self.nodes.dict)), dtype=float64)

        for i, node in enumerate(self.nodes.dict.values()):
            i:int
            node:Node
            
            indexes[i] = node.index
            marginal_costs[i] = self.marg_holding_backorder_cost(order, node, operator)
        
        return indexes[marginal_costs.argsort()]




