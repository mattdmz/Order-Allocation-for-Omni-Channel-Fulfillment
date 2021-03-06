###############################################################################################

'''This file contains the class Tours and its subclass Tour.'''

###############################################################################################

from copy import deepcopy
from datetime import datetime, time
from numpy import array, append, concatenate, delete, float32, zeros
from util import sol2routes


from dstrbntw.location import Location, distance
from dstrbntw.customers import Customer
from parameters import *
from transactions.orders import Order
from utilities.constants import SUBTRACT
from utilities.datetime import calc_time
from vrp.paersenssavings import paessens_savings_init

class Vehicle:

    '''Parent class for each delivery containing all constant attributes and methodsconcering the delivey vehicle.'''

    def __init__(self, vehicle_type:int) -> None:

        '''Sets constant attributes based on vehicle_type.'''
        
        #define vehicle attributes
        self.loading_time_per_order = LOADING_TIME_PER_ORDER[vehicle_type]
        self.service_time_per_order = SERVICE_TIME_PER_ORDER[vehicle_type]
        self.avg_speed = AVG_SPEED[vehicle_type]
        self.volume_capacity = MAX_LOADING_VOLUME[vehicle_type]
        self.pause_btw_tours = PAUSE_BTW_TOURS[vehicle_type]

    def operation_time(self, distances:array) -> array:

        ''' Returns the driving time for an array of distances for the delivery vehicle
            and adds the loading time / service time (hand over time). '''

        return (distances/self.avg_speed) + (self.loading_time_per_order + self.service_time_per_order)

class Delivery(Vehicle):

    def __init__(self, depot_type:int, depot_location:Location) -> None:

        '''Inherits vehicle constants.
            
            Inputs to VRP:
            --> duration_matrix (D = duration/distance/cost)
            --> order_vol (d = demand)
            --> available_volume (L = additional capacity constraint)
            
            Outputs from VRP:
            <-- route (solution = result from optimization)
            <-- duration (obj_v = result from objective function)'''

        #inherit delivery vehicle
        super().__init__(depot_type)

        # delivery attributes
        self.depot_type = depot_type
        self.depot_location = depot_location

        # list of orders assigned to the delivery tour
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

        # placeholder for the day the next deliveries will take place at this depot.
        self.day = None

    def calc_duration_to_other_stops(self, customer:Customer) -> array:

        ''' Calculates the distance based driving duration
            to each other stop of the delivery tour incl. loading time for each order (stop) and service time
            for the handover of the order.'''

        # calculates stop to distance matrix
        new_distances = zeros(self.duration_matrix.shape[0])

        # calcualte distance to depot
        new_distances[0] = distance(self.depot_location, customer.location)

        # calcualte distances of new stop to other delivery locations of the delivery tour
        if len(self.orders_to_deliver) > 1:
            for index, order in enumerate(self.orders_to_deliver[1:], start=1):
                new_distances[index] = distance(order.customer.location, customer.location)

        return self.operation_time(new_distances)

    def add_to_duration_matrix(self, new_durations:array) -> None:

        ''' Adds the precalculted distances of an order (stop) to the existing duration matrix. '''

        #add column to distance matrix with the stop.id as column name
        if len(self.orders_to_deliver) == 1:
            self.duration_matrix = concatenate((self.duration_matrix, new_durations))
            self.duration_matrix = concatenate((self.duration_matrix[None,:], append(new_durations, 0)[None,:]), axis=0)
        else:
            self.duration_matrix = concatenate((self.duration_matrix, new_durations[:,None]), axis=1)
            self.duration_matrix = concatenate((self.duration_matrix, append(new_durations, 0)[None,:]), axis=0)

    def remove_from_duration_matrix(self, delivery_index_from_order_to_remove:int) -> None:

        '''Removes location form duration matrix.'''

        self.duration_matrix = delete(self.duration_matrix, delivery_index_from_order_to_remove, axis=0) 
        self.duration_matrix = delete(self.duration_matrix, delivery_index_from_order_to_remove, axis=1)

        if len(self.duration_matrix) == 1:
            self.duration_matrix = array([0.0], dtype=float32)

    def add_order(self, order:Order) -> array:

        '''Adds order to delivery tour.'''
            
        # add a new stop to the delivery tour
        self.orders_to_deliver.append(order)
        self.delivery_volume.append(order.volume)

        # calculate durations to drive to all existing stops and to carry out loading and delivery operations 
        new_durations = self.calc_duration_to_other_stops(order.customer)

        # add stop to distance matrix
        self.add_to_duration_matrix(new_durations)

        # set a loading index to find order on all tours
        #order.delivery_index = len(self.orders_to_deliver)

        return new_durations

    def remove_order(self, order:Order) -> None:

        '''Removes order from delivery delivery tour.'''

        index_of_order_to_remove = None

        if order in self.orders_to_deliver:
            index_of_order_to_remove = self.orders_to_deliver.index(order)
            self.orders_to_deliver.remove(order)
            self.delivery_volume.remove(order.volume)

        if index_of_order_to_remove is not None:
            self.remove_from_duration_matrix(index_of_order_to_remove+1)
            self.remove_from_batches(order)

    def position_with_nearest_neighbours(self, new_durations:array) -> int:

        '''Returns the positions in the route at which an order has the shortest duration to 2 already inserted stops'''

        #init variables
        shortest_duration = 1000000

        #determine best position on route
        for index in range(1, len(self.routes)):
            index:int

            # calculate duration if node would be inserted between routes[index-1] and routes[index]
            new_dur = new_durations[self.routes[index-1]] + new_durations[self.routes[index]]
            
            if new_dur < shortest_duration:
                # set index as new best
                best_position = index
                shortest_duration = new_dur

        return best_position

    def build_routes(self, time_capacity_per_tour:int=MAX_WORKING_TIME[0], max_iterations_ls:int=PS_88_MAX_ITER_LOC_SEARCH) -> None:

        ''' Passes parameters to VRP Solver.
            Time_capacity_per_tour defines max time for every delivery delivery tour
            Stores the returned route list with the stop ids (self.routes)
            and objective funciton value (self.tot_duration).'''

        self.routes, self.tot_duration = paessens_savings_init( self.duration_matrix, self.delivery_volume, self.volume_capacity, 
                                                            time_capacity_per_tour, minimize_K=False, max_iterations_ls=max_iterations_ls, 
                                                            return_objv=True)

    def approximate_routes(self, new_durations:array) -> None:

        '''Add the new order to deliver between its two nearest neighbours on the existing route.'''
        
        #check if the order is the first one added to the tour (len == 2 because delivery tour has the depot index 0 as start and end value).
        if len(self.routes) == 2:
            #insert between delivery tour start and delivery tour end at depot
            self.routes.insert(1, len(self.orders_to_deliver)) 
        
        else: # orders to deliver where already added to delivery tour.

            #insert index of last added order in duration matrix on the delivery route betwenn its two nearest neighgours
            self.routes.insert(self.position_with_nearest_neighbours(new_durations), len(self.orders_to_deliver))

        #calculate overall duration for all tours
        self.tot_duration = self.route_duration(self.routes)

    def route_duration(self, route:list) -> int:

        '''Returns the rounded duration of a delivery tour in minutes.'''

        return int(round(sum(self.duration_matrix[route[r], route[r+1]] for r in range(len(route) - 1)), 0)) if len(route) > 2 else 0

    def get_orders_of_route(self, route:list) -> list:

        '''Returns a list of orders to deliver on route.'''

        return list(self.orders_to_deliver[index-1] for index in route[1:-1])

    def delivery_end(self, batch_index:int, batches:list, current_time:datetime) -> time:

        '''Retunrns the end time of the delivery tour.'''

        if batch_index == 0:
            
            # set delivery tour end to END_OF_TOURS
           end_time = END_OF_TOURS
            
        else:
            # set delivery tour start to end of privous delivery tour + a small pause
            end_time = calc_time(batches[batch_index - 1].delivery_start.time(), self.pause_btw_tours, SUBTRACT)
            
        return datetime.combine(current_time.date(), end_time) 

    def approx_delivery_end(self, current_time:datetime, order_processing_capacity:float) -> datetime:

        '''Retunrs the approximate end time of a delivery (all batches).'''

        for route in sol2routes(self.routes):
            orderlines_of_first_batch = sum(order.number_of_lines for order in self.get_orders_of_route(route))
        
        return  current_time + timedelta(minutes=int(round(orderlines_of_first_batch * order_processing_capacity, 0)) + self.tot_duration)
    
    
    class Batch:

        ''' A batch of orders resulting from a delivery tour that is processed togheter at a node before delivery.
            Given its size, it defines the start and end of the delivery delivery tour as well as the start of the order processing.'''

        def __init__(self, processing_node_type, orders:list, delivery_duration:int) -> None:

            '''Assigns arguments as instance attributes.'''
            
            self.processing_node_type = processing_node_type
            self.orders = orders
            self.delivery_duration = delivery_duration

        @property
        def order_processing_rate(self) -> float:

            '''returns order processing rate based on node type'''
            
            return ORDER_PROCESSING_RATE[self.processing_node_type]

        @property
        def tour_rate(self) -> float:

            '''returns fix delivery rate per delivery tour'''

            return TOUR_RATE[self.processing_node_type]
        
        @property
        def route_rate(self) -> float:

            '''returns variable cost rate per working minute'''

            return ROUTE_RATE[self.processing_node_type]  

        @property
        def order_processing_capacity(self) -> float:

            '''Returns the order processing capacity in number of orderlines per minute for a specific node type.'''

            return OP_CAPACITY[self.processing_node_type]   

        @property
        def delivery_costs(self) -> float:

            '''Returns the delivery costs for this batch.'''

            return self.tour_rate + self.route_rate * self.delivery_duration

        @property
        def processing_duration(self) -> int:
        
            '''Returns processing duration for a batch of orders in minutes.'''

            return int(round(sum(order.number_of_lines for order in self.orders) * self.order_processing_capacity, 0))

        def schedule(self, delivery_end:datetime, pause_btw_tours:int) -> None:

            ''' Carries out backward scheduling for order processing start and forward scheduling for delivery end
                based on delivery start of a batch.'''

            self.delivery_end = delivery_end
            self.delivery_start = self.delivery_end - timedelta(minutes=self.delivery_duration + pause_btw_tours)
            self.processing_start =  self.delivery_start - timedelta(minutes=self.processing_duration)
  
            
    def create_batches(self, current_time:datetime) -> None:

        ''' Separetes single tours and creates batches.
            Schedules operations for batch
            Stores batches as attribute list. '''

        batches = []

        # split allroutes and store them as single routes with their duration
        for route in sol2routes(self.routes):
            route:list
            
            #calcualte duration of route. Use route duration calculated when creating tour if there is only 1 route in sol2routes
            delivery_duration = self.tot_duration if route == self.routes else self.route_duration(route)
            
            # create a batch of orders to deliver on a tour
            new_batch = self.Batch(self.depot_type, self.get_orders_of_route(route), delivery_duration)
            
            # sort batches descending according to their duration
            if len(batches) == 0:
                batches.append(new_batch)
            
            else:
                # sort batches in descending order based on their route duration
                for index in range(len(batches) + 1):
                    index:int

                    try:
                        if new_batch.delivery_duration < batches[index].delivery_duration:
                            batches.insert(index, new_batch)
                            break
                    except:
                        batches.append(new_batch)
                        break
        
        # schedule operations for batches
        for index, batch in enumerate(batches):
            index:int
            batch:Delivery.Batch
            
            batch.schedule(self.delivery_end(index, batches, current_time), self.pause_btw_tours)
        
        # sort routs in descending order based on their duration
        self.batches = batches

    def remove_from_batches(self, order:Order) -> None:

        '''Removes an order form batches. the schedule batches method must be run rerun after having called this method.'''

        for batch in self.batches:
            batch:Delivery.Batch

            if order in batch.orders:
                batch.orders.remove(order)

    def processing_start(self) -> datetime:
        
        '''Returns the start time of the order processing and delivery the tour.'''

        try:
            return self.batches[len(self.batches) - 1].processing_start
        
        except IndexError:
            # no batches added yet
            return datetime(2050, 1, 1, 1, 1)

    def batch_to_process(self) -> Batch:
        
        ''' Returns batch of orders that needs to be processed from batchces (if there is any)
            Deletes batch from list and removes the orders from the delivery.'''

        try:
            return self.batches.pop()
        except IndexError:
            return None

    def on_time(self, current_time:datetime) -> bool:

        '''Returns True if order processing is starts after current_time, else returns False.'''

        return True if self.processing_start() > current_time else False


def create_prototype(current_delivery:Delivery, order:Order) -> Delivery:

    ''' Copies the current delivery and passes the already allocated orders to prevent duplication of order objects.
        Adds new order to delivery tour and builds routes for the new delivery tour.'''

    # copy existing delivery
    prototype_delivery = deepcopy(current_delivery)
    
    # reset orders to deliver and 
    prototype_delivery.orders_to_deliver = [order for order in current_delivery.orders_to_deliver]

    # construct prototype delivery with or without additional order 
    # (based if prototype is constructed for adding or dropping order form tour)
    if order not in prototype_delivery.orders_to_deliver:
        prototype_delivery.add_order(order)
        
    prototype_delivery.build_routes()

    return prototype_delivery


