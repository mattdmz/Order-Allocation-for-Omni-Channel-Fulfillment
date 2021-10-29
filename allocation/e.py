
###############################################################################################

'''This file contains the model elements and the model's objective function.'''

###############################################################################################


from numpy import array, sum
from typing import Union

from allocation.constants import DURATIONS, TOUR_RATES
from dstrbntw.region import Region


def replace(obj:object, attr:str, new_value:array):

    '''Replaces the value (array) of the passed objects attribute.'''

    setattr(obj, attr, new_value) 

def update(obj:object, attr:str, index:int, new_value:Union[int, float]):

    '''Updates the array of the passed objects attribute at the index position.'''

    getattr(obj, attr)[index] = new_value

def improvement(obj:object, attr:str, index:int, new_value:Union[int, float]) -> None:

    ''' Returns improvement as delta between new allocation based value and current value at position index.
        A positive return value means the value descreased and viceversa.'''

    return new_value - getattr(obj, attr)[index] if attr != TOUR_RATES else new_value - getattr(obj, attr)[index] * (getattr(obj, DURATIONS)[index]> 0)


class Orders:

    def __init__(self) -> None:
        
        # init placeholder
        self.possible_revenue = None

    def init_array(self, new_orders:list, attr:str) -> array:

        arr = []

        for index, order in enumerate(new_orders):
            arr[index] = getattr(order, attr)

        return array(arr)


class Supply:

    def __init__(self) -> None:

        # init placeholders
        self.rates = None
        self.volumes = None


class Stock:

    def __init__(self, current_level:array, reserved:array, holding_rates:array) -> None:

        '''Store current_level and holding_rates.'''

        self.current_level = current_level
        self.reserved = reserved
        self.rates = holding_rates
    
        # set placeholder
        self.demanded = None


class Order_Processing:

    def __init__(self) -> None:
        
        # init placeholders
        self.rates = None
        self.orderlines = None


class Tours:

    def __init__(self, tour_rates:array, route_rates:array) -> None:

        '''Stores tour_rates and route_rates.'''

        self.tour_rates = tour_rates
        self.route_rates = route_rates

        # set placeholder
        self.durations = None


class Evaluation_Model:

    def __init__(self, current_level:array, reserved:array, holding_rates:array, tour_rates:array, route_rates:array) -> None:

        '''Inits a evaluation model.'''
        
        #add model attributes
        self.orders = Orders()
        self.supply = Supply()
        self.stock = Stock(current_level, reserved, holding_rates)
        self.order_processing = Order_Processing()
        self.tours = Tours(tour_rates, route_rates)

    def __init__(self, region:Region) -> None:

        '''Inits a evaluation model.'''
        
        #add model attributes
        self.orders = Orders(region.orders.)
        self.supply = Supply()
        self.stock = Stock(current_level, reserved, holding_rates)
        self.order_processing = Order_Processing()
        self.tours = Tours(tour_rates, route_rates)

    def objective_function(self, allocation:array) -> float:

        '''Evaluates an allocation and returns its objective value.'''

        print("revenue: ", sum(self.orders.possible_revenue * (allocation > -1)))
        print("stock: ", sum((sum((self.stock.current_level- self.stock.reserved) * (self.stock.demanded > 0)  - self.stock.demanded, axis=0) * self.stock.rates)))
        print("supply: ", sum(self.supply.volumes * self.supply.rates * (allocation > -1)))
        print("order proc: ", sum(self.order_processing.orderlines * self.order_processing.rates * (allocation > -1)))
        print("tours: ", sum(self.tours.tour_rates * (self.tours.durations > 0)))
        print("tours: ", sum(self.tours.route_rates * self.tours.durations))


        return    sum(self.orders.possible_revenue * (allocation > -1)) \
                + sum((sum((self.stock.current_level- self.stock.reserved) * (self.stock.demanded > 0)  - self.stock.demanded, axis=0) * self.stock.rates)) \
                - sum(self.supply.volumes * self.supply.rates * (allocation > -1)) \
                - sum(self.order_processing.orderlines * self.order_processing.rates * (allocation > -1)) \
                - sum(self.tours.tour_rates * (self.tours.durations > 0)) \
                - sum(self.tours.route_rates * self.tours.durations)
