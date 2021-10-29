
###############################################################################################

'''This file contains the class Orders and its subclass Order and its child class Lines.'''

###############################################################################################

from datetime import datetime, timedelta

from dstrbntw.articles import Articles
from dstrbntw.customers import Customers
from dstrbntw.location import distance
from parameters import MAX_PAL_VOLUME
from protocols.constants import *


class Order():

        def __init__(self, data:list, customers:Customers) -> None:

            '''Assigns index (int) to instance and 
                assigns imported data to attributes.'''
            
            # assign attributes
            self.id = data[0]
            customer_id = data[1]
            self.date_time = datetime.combine(data[2], datetime.min.time()) + data[3]
            self.price = float(data[4])
            self.volume = float(data[5])
            # self.weight = float(data[6])

            # add customer with the customer_id imported
            self.customer = customers.__get__(customer_id)

            #  init sales lines (to be added)
            self.lines = []

            # set placeholders
            self.processable = None
            self.allocated_node =  None
            self.allocation_time = None
            self.delivery_index = None

        @property
        def number_of_lines(self) -> int:

            '''Returns number of lines of an order.'''

            return len(self.lines)

        @property
        def pieces(self) -> int:

            '''Returns the sum of pieces ordered.'''

            return sum(line.quantity for line in self.lines)

        @property
        def supply_costs(self) -> float:

            '''Returns the supply costs for an order based on its allocation.'''

            return self.allocated_node.supply_rate * self.volume / MAX_PAL_VOLUME
        
        @property
        def processing_costs(self) -> float:

            '''Returns the processing costs for an order based on its allocation.'''

            return self.number_of_lines * self.allocated_node.order_processing_rate

        def delivered_sameday(self, current_time:datetime, cut_off_time:datetime) -> bool:

            ''' Returns True or False depending if the order is delivered sameday or not
                For orders coming in after cut_off_time, sameday == True if they are deliverd on the subsequent day.'''

            return True if (self.date_time <= cut_off_time and self.allocated_node !=None) or \
                            (self.date_time > cut_off_time and (current_time + timedelta(days=1)).date() == self.date_time.date()) else False

        def protocol(self, region_id:int, current_time:datetime,  cut_off_time:datetime=None, delivery_costs:float=None, stock_holding_costs:float=None, failure:int=None) -> dict:

            '''Returns a dict documenting the (not) processing of the order and its related costs.'''

            if self.allocated_node != None:

                supply_costs = self.supply_costs
                processing_costs = self.processing_costs
                
                # calculate values for successfully allocated order
                return {    ORDER_ID: self.id,
                            REGION_ID: region_id,
                            ARRIVAL_DATETIME: self.date_time,
                            ALLOCATION_DATETIME: self.allocation_time,
                            PROC_DATETIME: current_time,
                            ALLOCATED_NODE_ID: self.allocated_node.id,
                            POTENTIAL_ONLINE_REVENUE: self.price,
                            ONLINE_REVENUE: self.price,
                            SUPPLY_COSTS: supply_costs, 
                            ORDER_PROCESSING_COSTS: processing_costs, 
                            DELIVERY_COSTS: delivery_costs,
                            STOCK_HOLDING_COSTS: stock_holding_costs,
                            PROFIT: self.price - supply_costs - processing_costs - delivery_costs - stock_holding_costs,
                            PUNCTUALITY: self.delivered_sameday(current_time, cut_off_time),
                            DISTANCE: distance(self.customer.location, self.allocated_node.location)
                        }
            else:
                # return zeros for unsuccessfully allocated order
                return {    ORDER_ID: self.id,
                            REGION_ID: region_id,
                            ARRIVAL_DATETIME: self.date_time,
                            ALLOCATION_DATETIME: current_time,
                            PROC_DATETIME: "",
                            ALLOCATED_NODE_ID: failure,
                            POTENTIAL_ONLINE_REVENUE: self.price,
                            ONLINE_REVENUE: 0,
                            SUPPLY_COSTS: 0, 
                            ORDER_PROCESSING_COSTS: 0, 
                            DELIVERY_COSTS: 0,
                            STOCK_HOLDING_COSTS: 0,
                            PROFIT: 0,
                            PUNCTUALITY: False,
                            DISTANCE: 0
                        }


        class Line():
        
            def __init__(self, data:list, articles:Articles)-> None:

                '''Assigns imported data to attributes.'''
                
                #self.transaction_id = data[0] --> not necessary
                article_id = data[1]
                self.quantity = data[2]
                
                #add article based on the article id
                self.article = articles.__get__(article_id)

            @property
            def volume(self):

                '''Returns the article volume of the ordered articles.'''

                return self.article.volume * self.quantity


class Orders:

    def __init__(self) -> None:
        
        '''Inits orders instance.'''

        # init list to store orders
        self.list = []
        self.allocation_retry_needed = []

    @property
    def potential_revenue(self) -> list:

        '''Returns a list of with 'order.price  * (1-MARGE)' for all orders.'''

        return list(order.price for order in self.list)

    @property
    def arrival_datetimes(self) -> list:

        '''Returns a list of order arrival datetime for all orders.'''

        return list(order.date_time for order in self.list)

    @property
    def allocated(self) -> list:

        '''Returns a list of already allocated orders.'''

        return list(order for order in self.list if order.allocated_node != None)

    @property
    def already_allocated(self) -> list:

        '''Returns a list of True/False based depending if the order was already allocated or not.'''

        return list(True if order.allocated_node != None else False for order in self.list)

    def __get__(self, index:int) -> Order:

        '''Returns an order from the orders.list based on its index in the list.'''

        return self.list[index]

    def __getattr__(self, index:int, attr:str):

        '''Returns an order's attribute from the orders.list based on its index in the list.'''

        return getattr(self.list[index], attr)

    def clear(self) -> None:

        '''Clears list of orders.'''
    
        self.list = []

    def allocation_based_supply_costs(self) -> list:

        '''Returns a list of allocation based supply costs based on the node_type for all orders.'''

        return list(order.supply_costs if order.allocated_node is not None else 0 for order in self.list)

    def allocation_based_processing_costs(self) -> list:

        '''Returns a list of allocation based order processing costs based on the node_type for all orders.'''

        return list(order.processing_costs if order.allocated_node is not None else 0 for order in self.list)

    def delivered_sameday(self, current_time:datetime, cut_off_time:datetime) -> list:

        ''' Returns True or False depending if the order is delivered sameday or not
            For orders coming in after cut_off_time, sameday == True if they are deliverd on the subsequent day.'''

        return list(order.delivered_sameday(current_time, cut_off_time) for order in self.list)

    def allocation_retry(self, order:Order) -> None:

        '''Adds an order which could not be allocated to the allocation_retry_needed list.'''

        self.allocation_retry_needed.append(order)

    def reschedule_unallocated(self) -> None:

        ''' Removes orders that could not be allocated and need a allocation retry 
            from orders.allocation_retry_needed and adds them to orders.list.'''

        self.list = self.allocation_retry_needed
        self.allocation_retry_needed = []



