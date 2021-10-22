
###############################################################################################

'''This file contains the class Tours and its subclass Tour.'''

###############################################################################################

from datetime import datetime, time
from numpy import array, append, concatenate, delete, float32, insert, zeros
from util import sol2routes


from dstrbntw.constants import ROUTE_INDEX
from dstrbntw.location import distance
from dstrbntw.customers import Customer
from parameters import *
from utilities.constants import ADD, SUBTRACT
from utilities.timesim import calc_time
from transactions.orders import Order
from vrp.paersenssavings import paessens_savings_init

class Vehicle:

    '''Parent class for each Tour containing all constant attributes and methodsconcering the delivey vehicle.'''

    def __init__(self, vehicle_type:int) -> None:

        '''Sets constant attributes based on vehicle_type.'''
        
        #define vehicle attributes
        self.loading_time_per_order = LOADING_TIME_PER_ORDER[vehicle_type]
        self.service_time_per_order = SERVICE_TIME_PER_ORDER[vehicle_type]
        self.avg_speed = AVG_SPEED[vehicle_type]
        self.volume_capacity = MAX_LOADING_VOLUME[vehicle_type]
        self.pause_btw_tours = PAUSE_BTW_TOURS[vehicle_type]

    def operation_time(self, distances:array) -> float:

        ''' Returns the driving time for an array of distances for the delivery vehicle
            and adds the loading time / service time (hand over time) in proportion 
            to the number of stops. '''

        return (self.avg_speed * distances) + ((self.loading_time_per_order + self.service_time_per_order) / len(distances))

class Tour(Vehicle):

    def __init__(self, node) -> None:

        '''Inherits vehicle constants.
            
            Inputs to VRP:
            --> duration_matrix (D = duration/distance/cost)
            --> order_vol (d = demand)
            --> available_volume (L = additional capacity constraint)
            
            Outputs from VRP:
            <-- route (solution = result from optimization)
            <-- duration (obj_v = result from objective function)'''

        #inherit delivery vehicle
        super().__init__(node.node_type)

        # delivery attributes
        self.depot = node

        #list of orders assigned to the tour
        self.orders_to_deliver = []

        #duration matrix used to build route
        self.duration_matrix = array([0.0], dtype=float32)

        # list of order volumes to deliver         
        self.delivery_volume = [0.0]

        # total duration
        self.tot_duration = 0

        # list of location ids in delivery sequence
        self.routes = [0, 0]

        # list of order batches that form a single delivery run 
        self.batches =  []

    def calc_duration_to_other_stops(self, customer:Customer) -> array:

        ''' Calculates the distance based driving duration
            to each other stop of the tour incl. loading time for each order (stop) and service time
            for the handover of the order.'''

        #calculates stop to distance matrix
        new_distances = zeros(len(self.orders_to_deliver))

        #calcualte distance to depot
        new_distances[0] = distance(self.depot.location, customer.location)

        #calcualte distances of new stop to other delivery locations of the tour
        if len(self.orders_to_deliver) > 1:
            for index, order in enumerate(self.orders_to_deliver[1:], start=1):
                new_distances[index] = distance(order.customer.location, customer.location)

        return self.operation_time(new_distances)

    def add_to_duration_matrix(self, new_durations) -> None:

        ''' Adds the precalculted distances of an order (stop) to the existing duration matrix. '''

        #add column to distance matrix with the stop.id as column name
        if len(self.orders_to_deliver) == 1:
            self.duration_matrix = concatenate((self.duration_matrix, new_durations))
            self.duration_matrix = concatenate((self.duration_matrix[None,:], append(new_durations, 0)[None,:]), axis=0)
        else:
            self.duration_matrix = concatenate((self.duration_matrix, new_durations[:,None]), axis=1)
            self.duration_matrix = concatenate((self.duration_matrix, append(new_durations, 0)[None,:]), axis=0)

    def remove_from_duration_matrix(self, order:Order) -> None:

        '''Removes location form duration matrix.'''

        delete(self.duration_matrix, order.route_index, axis=0)
        delete(self.duration_matrix, order.route_index, axis=1)

    def load(self, order) -> None:

        '''Reduces available delivery volume of vehicle by volume required by order'''

        self.delivery_volume[order.id] = order.volume

    def unload(self, order) -> None:

        '''Raises available delivery volume of vehicle by volume required by order'''

        del self.delivery_volume[order.id]

    def add_order(self, order:Order) -> array:

        '''Adds order to delivery tour.'''

        #add a new stop to the tour
        self.orders_to_deliver.append(order)
        self.delivery_volume.append(order.volume)

        #set a loading index to find order on all tours
        setattr(order, ROUTE_INDEX, len(self.orders_to_deliver))

        #calculate durations to drive to all existing stops and to carry out loading and delivery operations 
        new_durations = self.calc_duration_to_other_stops(order.customer)

        #add stop to distance matrix
        self.add_to_duration_matrix(new_durations)

        return new_durations

    def remove_order(self, order:Order) -> None:

        '''Removes order from delivery tour.'''
        
        #add a new stop to the tour
        del self.orders_to_deliver[order.route_index]
        del self.delivery_volume[order.route_index]

        #remove stop to distance matrix
        self.remove_from_duration_matrix(order)

        #remove order from route
        self.routes.remove(order.route_index)

        #set a loading index to find order on all tours
        setattr(order, ROUTE_INDEX, 0)

    def position_with_nearest_neighbours(self, new_durations:array) -> int:

        '''Returns the positions in the route at which an order has the shortest duration to 2 already inserted stops'''

        #init variables
        shortest_duration = 1000000

        #determine best position on route
        for index in range(1, len(self.routes)):
            
            # calculate duration if node would be inserted between routes[index-1] and routes[index]
            new_dur = new_durations[self.routes[index-1]] + new_durations[self.routes[index]]
            
            if new_dur < shortest_duration:
                # set index as new best
                best_position = index
                shortest_duration = new_dur

        return best_position

    def build_routes(self, time_capacity_per_tour:int=MAX_WORKING_TIME, node_type:int=None, max_iterations_ls:int=PS_88_MAX_ITER_LOC_SEARCH) -> None:

        ''' Passes parameters to VRP Solver.
            Time_capacity_per_tour defines max time for every delivery tour
            Stores the returned route list with the stop ids (self.routes)
            and objective funciton value (self.tot_duration).'''

        self.routes, self.tot_duration = paessens_savings_init(self.duration_matrix, self.delivery_volume, self.volume_capacity, 
                                                            MAX_WORKING_TIME[node_type] if time_capacity_per_tour is None else time_capacity_per_tour, 
                                                            minimize_K=False, max_iterations_ls=max_iterations_ls, return_objv=True)

    def approximate_routes(self, new_durations:array) -> None:

        '''Add the new order to deliver between its two nearest neighbours on the existing route.'''
        
        #check if the order is the first one added to the tour (len == 2 because tour has the depot index 0 as start and end value).
        if len(self.routes) == 2:
            #insert between tour start and tour end at depot
            self.routes.insert(1, len(self.orders_to_deliver)) 
        
        else: # orders to deliver where already added to tour.

            #insert index of last added order in duration matrix on the delivery route betwenn its two nearest neighgours
            self.routes.insert(self.position_with_nearest_neighbours(new_durations), len(self.orders_to_deliver))

        #calculate overall duration for all tours
        self.tot_duration = self.route_duration(self.routes)

    def route_duration(self, route:list) -> int:

        '''Returns the rounded duration of a tour in minutes.'''

        return int(round(sum(self.duration_matrix[route[r], route[r+1]] for r in range(len(route) - 1)), 0))

    def get_orders_of_route(self, route:list) -> list:

        '''Returns a list of orders to deliver on route.'''

        return list(self.orders_to_deliver[index - 1] for index in route[1:-1])

    def delivery_start(self, batches:list, delivery_duration:int) -> time:

        '''Retunrns the start time of the delivery tour.'''

        # is last batch
        if len(batches) == 1:
            # set tour start to min(OP_END (=node closure), or END_OF_TOURS - tour duration)
            return min(OP_END[self.depot.node_type], calc_time(END_OF_TOURS, delivery_duration + self.pause_btw_tours, SUBTRACT))
        else:
            # set tour start to end of privous tour + a small pause
            return calc_time(batches[len(batches)-1].delivery_end, self.pause_btw_tours, ADD)    

    class Batch:

        ''' A batch of orders resulting from a delivery tour that is processed togheter at a node before delivery.
            Given its size, it defines the start and end of the delivery tour as well as the start of the order processing.'''

        def __init__(self, processing_node, orders:list, delivery_duration:int) -> None:

            '''Assigns arguments as instance attributes.'''
            
            self.processing_node = processing_node
            self.orders = orders
            self.delivery_duration = delivery_duration

        @property
        def delivery_costs(self) -> float:

            '''Returns the delivery costs for this batch.'''

            return self.processing_node.tour_rate + self.processing_node.route_rate * self.delivery_duration

        @property
        def processing_duration(self) -> int:
        
            '''Returns processing duration for a batch of orders'''

            return self.processing_node.processing_duration(sum(order.number_of_lines for order in self.orders))

        def schedule(self, delivery_start:datetime) -> None:

            ''' Carries out backward scheduling for order processing start and forward scheduling for delivery end
                based on delivery start of a batch.'''

            self.delivery_start = delivery_start
            self.delivery_end = calc_time(self.delivery_start, self.delivery_duration, ADD)
            self.order_processing_start =  calc_time(self.delivery_start, self.processing_duration, SUBTRACT)
            

    def create_batches(self) -> list:

        ''' Separetes single tours and creates batches.
            Schedules operations for batch. '''

        batches = []

        # split allroutes and store them as single routes with their duration
        for route in sol2routes(self.routes):
            
            #calcualte duration of route. Use route duration calculated when creating tour if there is only 1 route in sol2routes
            delivery_duration = self.tot_duration if route == self.routes else self.route_duration(route)
            
            # create a batch of orders to deliver on a tour
            new_batch = self.Batch(self.depot, self.get_orders_of_route(route), delivery_duration)
            
            # sort batches descending according to their duration
            if len(batches) == 0:
                batches.append(new_batch)
            else:
                for index, batch in enumerate(batches):
                    if batch.delivery_duration < new_batch.delivery_duration:
                        batches.insert(index, new_batch)
                        break
        
        # schedule operations for batches
        for batch in batches:
            batch.schedule(self.delivery_start(batches, batch.delivery_duration))
        
        # sort routs in descending order based on their duration
        return batches                         #sorted(key=lambda batch: batch.order_processing_start, reverse=True)

    def schedule_batches(self) -> None:
        
        '''Reschedules tour and creates batches of orders to process and deliver together.'''

        self.batches = self.create_batches()

    def execution_start(self) -> time:
        
        '''Returns the start time of the order processing and delivery the tour.'''

        try:
            return self.batches[0].order_processing_start
        
        except IndexError:
            # no batches added yet
            return time(23, 59, 59)

    def batch_to_process(self) -> list:
        
        ''' Returns batch of orders that needs to be processed from bacthces
            Deletes batch from list.'''

        batch = self.batches[0]
        del self.batches[0]
        return batch

    def on_time(self, current_time:datetime) -> bool:

        '''Returns True if order processing is starts after current_time, else returns False.'''

        return True if self.execution_start() > current_time.time() else False


