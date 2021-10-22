
###############################################################################################

'''This file contains the class Orders and its subclass Order and its child class Lines.'''

###############################################################################################

from datetime import datetime, timedelta

from dstrbntw.articles import Articles
from dstrbntw.constants import SUPPLY_RATE, ORDER_PROCESSING_RATE, PROFIT
from dstrbntw.customers import Customers
from parameters import MAX_PAL_VOLUME


class Order():

        def __init__(self, data:list, customers:Customers) -> None:

            '''Assigns index (int) to instance and 
                assigns imported data to attributes.'''
            
            #assign attributes
            self.id = data[0]
            customer_id = data[1]
            self.date_time = datetime.combine(data[2], datetime.min.time()) + data[3]
            self.price = float(data[4])
            self.volume = float(data[5])
            #self.weight = float(data[6])

            #add customer with the customer_id imported
            self.customer = customers.__get__(customer_id)

            #init sales lines (to be added)
            self.lines = []

            #init allocation (set to not allocated) --> node
            self.allocation =  None

        @property
        def number_of_lines(self) -> int:

            '''Returns number of lines of an order.'''

            return len(self.lines)

        @property
        def supply_rate(self, node=None) -> float:

            '''Return the costs to supply the demanded articles from the order to the delivering node.'''

            return getattr(self.allocation if node is None else node, SUPPLY_RATE)  * self.volume / MAX_PAL_VOLUME

        @property
        def supply_costs(self) -> float:

            '''Returns the supply costs for an order based on its allocation.'''

            return self.allocation.supply_rate * self.volume
        
        @property
        def processing_costs(self) -> float:

            '''Returns the processing costs for an order based on its allocation.'''

            return self.number_of_lines * self.allocation.order_processing_rate


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

        # init profit from processing orders
        self.profit = 0

    @property
    def possible_revenue(self) -> list:

        '''Returns a list of with the price for all orders.'''

        return list(order.price for order in self.list)

    @property
    def volume_supplied(self) -> list:

        '''Returns a list of with the volume for all orders.'''

        return list(order.volume for order in self.list)

    @property
    def lines_to_process(self) -> list:

        '''Returns a list of with the number of orderlines for all orders.'''

        return list(order.number_of_lines for order in self.list)

    @property
    def arrival_datetimes(self) -> list:

        '''Returns a list of order arrival datetime for all orders.'''

        return list(order.date_time for order in self.list)

    @property
    def allocated(self) -> list:

        '''Returns a list of already allocated orders.'''

        return list(order for order in self.list if order.allocation != None)

    @property
    def already_allocated(self) -> list:

        '''Returns a list of True/False based depending if the order was already allocated or not.'''

        return list(True if order.allocation != None else False for order in self.list)

    @property
    def allocation_based_supply_rates(self) -> list:

        '''Returns a list of allocation based supply rates based on the node_type for all orders.'''

        return list(order.supply_rate if order.allocation is not None else 0 for order in self.list)

    @property
    def allocation_based_processing_rates(self) -> list:

        '''Returns a list of allocation based order processing rates based on the node_type for all orders.'''

        return list(getattr(order.allocation, ORDER_PROCESSING_RATE) if order.allocation is not None else 0 for order in self.list)

    def __get__(self, index:int) -> Order:

        '''Returns an order from the orders.list based on its index in the list.'''

        return self.list[index]

    def __getattr__(self, index:int, attr:str):

        '''Returns an order's attribute from the orders.list based on its index in the list.'''

        return getattr(self.list[index], attr)

    def clear(self) -> None:

        '''Clears list of orders.'''
    
        self.list = []

    def store_profit(self, result:dict) -> None:

        '''Adds profit to current profit'''

        self.profit += sum(result[PROFIT])

    def collect_profit(self) -> float:

        '''Returns profit and resets profit attribute'''

        profit = self.profit
        self.profit = 0
        return profit

    def delivered_sameday(self, current_time:datetime, cut_off_time:datetime) -> list:

        '''Returns a list of booleans depending if the order is delivered sameday or not for all orders.'''

        return list(True if (order.date_time <= cut_off_time and order.allocation !=None) or \
                            (order.date_time > cut_off_time and (current_time + timedelta(days=1)).date() == order.date_time.date())
                        else False for order in self.list)

    def reschedule_allocation(self) -> None:

        ''' Removes orders that could not be allocated from orders.list
            and adds them to orders.allocation_retry_needed.'''

        for order in self.list:

            if order.allocation == None:
                self.allocation_retry_needed.append(order)

    def retry_allocation(self) -> None:

        ''' Removes orders that could not be allocated from orders.allocation_retry_needed
            and readds them to orders.list.'''

        for index, in range(self.allocation_retry_needed):
                self.list.append(self.allocation_retry_needed.pop(index))



