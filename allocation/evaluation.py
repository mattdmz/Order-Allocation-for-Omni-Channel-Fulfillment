
###############################################################################################

'''This file contains the model elements and the model's objective function.'''

###############################################################################################


from datetime import datetime
from numpy import array, sum, unique
from typing import Union

from transactions.orders import Orders
from transactions.sales import Sales


class Evaluation_Model:

    def __init__(self, sales:Sales, orders:Orders,  stock_holding_rates:array, tour_rates:list, route_rates:list) -> None:

        ''' Inits a model to evaluate allocations.
            In order to return correct results, the evaluation model method prepare must be run 
            before calculting the objective function of an allocation or calculating punctuality.'''

        # sales
        self.potential_offline_revenue = array(sales.potential_revenue)
        self.offline_revenue = None

        # orders info
        self.orders_list = orders.list
        self.potential_online_revenue = array(orders.potential_revenue)
        self.supply_costs = None
        self.processing_costs = None
        
        # stock info
        self.stock_holding_rates = stock_holding_rates
        self.demanded_stock = None

        # delivery info
        self.tour_rates = array(tour_rates)
        self.route_rates = array(route_rates)
        self.delivery_durations = None

        # helper funciton for determining punctuality
        self.delivered_sameday_func = orders.delivered_sameday
        
    def update(self, attr:str, index:int, new_value:Union[int, float]):

        '''Updates the array of the passed attribute at the index position.'''

        getattr(self, attr)[index] = new_value

    def prepare(self, supply_costs:list, processing_costs:list, demanded_stock:array, tour_durations:list, offline_revenue:float, diminuished_stock_value:float) -> None:

        '''Provides evaluation model with all allocation based infos to evaluate allocation.'''

        self.supply_costs = array(supply_costs)
        self.order_processing_costs = array(processing_costs)
        self.demanded_stock = demanded_stock
        self.tour_durations = array(tour_durations)
        self.offline_revenue = offline_revenue
        self.diminuished_stock_value_from_sales = diminuished_stock_value

    def objective_function(self, allocation:array) -> float:

        '''Evaluates an allocation and returns its objective value.'''

        return      self.offline_revenue \
                +   self.diminuished_stock_value_from_sales \
                +   sum(self.potential_online_revenue * (allocation > -1)) \
                +   sum(self.demanded_stock * self.stock_holding_rates) \
                -   sum(self.supply_costs * (allocation > -1)) \
                -   sum(self.order_processing_costs * (allocation > -1)) \
                -   sum(self.tour_rates * ((self.tour_durations > 0) / len(unique(allocation >= 0)))) \
                -   sum(self.route_rates * self.tour_durations)

    def sameday_delivery(self, current_time:datetime) -> float:

        ''' Returns the number of orders that will be deliverd same-day.
            Same-day == the the day the order arrives, if cut_off_time is not yet reached, 
            else same-day == the day the order arrives + 1, if the order arrives after cut_off_time.'''

        return self.delivered_sameday_func(current_time) / len(self.orders_list) if len(self.orders_list) > 0 else 0
