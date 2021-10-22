
###############################################################################################

'''This file contains the model elements and the model's objective function.'''

###############################################################################################


from numpy import array, sum


class Orders:

    def __init__(self) -> None:
        
        pass

    def init_array(self, new_orders:list, attr:str) -> array:

        arr = []

        for index, order in enumerate(new_orders):
            arr[index] = getattr(order, attr)

        return array(arr)

    def set_possible_revenue(self, possible_revenue:array) -> None:

        '''Sets possible revenues from orders.'''

        self.possible_revenue = possible_revenue

class Supply:

    def __init__(self) -> None:
        pass

    def set_volumes(self, volumes:array) -> None:

        '''Sets volume per order to supply to each delivering node.'''

        self.volumes = volumes

    def replace_rates(self, rates:array) -> None:

        '''Replaces all allocation based supply_rates.'''

        self.rates = rates

    def rate_improvement(self, order_index:int, allocation_based_rate:float) -> None:

        ''' Returns improvement as delta between new allocation based rate and current rate.
            A positive return value means the rate descreased and viceversa.'''

        return allocation_based_rate - self.rates[order_index]

    def update_rate(self, order_index:int, allocation_based_rate:float) -> None:

        ''' Updates rate with allocation based order processing rate.
            Returns improvement as delta between new allocation based rate and current rate.
            A positive return value means the rate descreased and viceversa.'''

        improvement = allocation_based_rate - self.rates[order_index]
        self.rates[order_index] = allocation_based_rate

        return improvement

class Stock:

    def __init__(self, current_level:array, reserved:array, holding_rates:array) -> None:

        '''Store current_level and holding_rates.'''

        self.current_level = current_level
        self.reserved = reserved
        self.holding_rates = holding_rates

    def rate_improvement(self, node_index:int, allocation_based_rate:float) -> None:

        ''' Returns improvement as delta between new allocation based rate and current rate.
            A positive return value means the rate descreased and viceversa.'''

        return sum(allocation_based_rate - self.holding_rates[node_index])

class Order_Processing:

    def __init__(self) -> None:
        pass

    def set_orderlines(self, orderlines:array) -> None:

        '''Sets orderlines per order to process to each delivering node.'''

        self.orderlines = orderlines

    def replace_rates(self, rates:array) -> None:

        '''Replaces all allocation based orer processing rates.'''

        self.rates = rates

    def rate_improvement(self, order_index:int, allocation_based_rate:float) -> None:

        ''' Returns improvement as delta between new allocation based rate and current rate.
            A positive return value means the rate descreased and viceversa.'''

        return allocation_based_rate - self.rates[order_index]

    def update_rate(self, order_index:int, allocation_based_rate:float) -> None:

        '''Updates rate with allocation based order processing rate.'''

        self.rates[order_index] = allocation_based_rate

class Tours:

    def __init__(self, tour_rates:array, route_rates:array) -> None:

        '''Stores tour_rates and route_rates.'''

        self.tour_rates = tour_rates
        self.route_rates = route_rates

    def replace_durations(self, durations:array) -> None:

        '''Stores tour_rates and route_rates.'''

        self.durations = durations

    def tour_rate_improvement(self, node_index:int, allocation_based_rate:float) -> None:

        ''' Returns improvement as delta between new allocation based tour rate and current tour rate.
            A positive return value means the tour rate descreased and viceversa.'''

        return (allocation_based_rate - self.tour_rates[node_index]) * (self.durations[node_index] > 0)

    def route_rate_improvement(self, node_index:int, allocation_based_rate:float) -> None:

        ''' Returns improvement as delta between new allocation based route rate and current route rate.
            A positive return value means the route rate descreased and viceversa.'''

        return allocation_based_rate - self.route_rates[node_index]

    def duration_improvement(self, node_index:int, duration:float) -> None:

        ''' Returns improvement as delta between new allocation based delivery tour duration and current delivery tour duration.
            A positive return value means the duration of the delivery tour descreased and viceversa.'''

        return duration - self.durations[node_index]

    def update_duration(self, node_index:int, duration:int) -> None:

        '''Updates tour durations.'''

        self.durations[node_index] = duration

class Evaluation_Model:

    def __init__(self, current_level:array, reserved:array, holding_rates:array, tour_rates:array, route_rates:array) -> None:

        '''Inits a evaluation model.'''
        
        #add model attributes
        self.orders = Orders()
        self.supply = Supply()
        self.stock = Stock(current_level, reserved, holding_rates)
        self.order_processing = Order_Processing()
        self.tours = Tours(tour_rates, route_rates)

    def objective_function(self, allocation:array) -> float:

        '''Evaluates an allocation and returns its objective value.'''

        return    sum(self.orders.possible_revenue * (allocation > -1)) \
                - sum(self.supply.volumes * self.supply.rates * (allocation > 1)) \
                - sum(self.order_processing.orderlines * self.order_processing.rates * (allocation > -1)) \
                - sum(sum(self.stock.current_level - self.stock.reserved, axis=0) * self.stock.holding_rates) \
                - sum(self.tours.durations * self.tours.route_rates) + sum(self.tours.tour_rates * (self.tours.durations > 0))
