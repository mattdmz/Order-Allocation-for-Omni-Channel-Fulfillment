
###############################################################################################

'''This file contains the class Sales and its subclass Sale and its child class Lines.'''

###############################################################################################


from datetime import datetime

from dstrbntw.articles import Articles
from dstrbntw.nodes import Nodes
from protocols.constants import REGION_ID, PROC_DATETIME, NUMBER_OF_LINES, LINES_CLOSED, POTENTIAL_OFFLINE_REVENUE, OFFLINE_REVENUE


class Sale():

    def __init__(self, data:list, nodes:Nodes) -> None:

        ''' Assigns index (int) to instance and 
            assigns imported data to attributes.'''
        
        # assign attributes
        self.id = data[0]
        node_id = data[1]
        self.date_time = datetime.combine(data[2], datetime.min.time()) + data[3]
        self.price = float(data[4])
        # self.volume = float(data[5])
        # self.weight = float(data[6])

        # adds the node where the sale took place based on the node_id imported
        self.node = nodes.__get__(id=node_id)

        # init sales lines (to be added)
        self.lines = []

    @property
    def lines_closed(self) -> int:

        '''Returns the number of salelines closed.'''

        return sum(line.closed for line in self.lines)


    class Line():
    
        def __init__(self, data:list, articles:Articles):

            '''Assigns imported data to attributes.'''
            
            # self.transaction_id = data[0]
            article_id = data[1]
            self.quantity = data[2]

            # mark saleline as not closed yet
            self.closed = False

            # add aricle based on the article_id imported
            self.article = articles.__get__(article_id)

        @property
        def revenue(self) -> float:

            '''Returns the revenue generated if the sale was closed.'''

            return self.article.price * self.quantity if self.closed else 0


class Sales:

    def __init__(self) -> None:

        '''Inits sales instance.'''

        # init revenue attr and list to store sales
        self.list = []
        self.revenue = 0

    @property
    def potential_revenue(self) -> float:

        '''Returns the potential revenue 'sale.price  * (1-MARGE)' for all sales.'''

        return sum(sale.price for sale in self.list)
    
    @property
    def number_of_lines(self) -> int:

        '''Returns the sum of all salelines to process.'''

        return sum(len(sale.lines) for sale in self.list)

    @property
    def number_of_lines_closed(self) -> int:

        '''Returns the sum of all salelines successfully closed.'''

        return sum(sale.lines_closed for sale in self.list)

    def store_realized_revenue(self, realized_revenue:float) -> None:

        '''Stores the realized revenue from processing sales.'''

        self.revenue = realized_revenue

    def clear(self) -> None:

        '''Clears list of sales.'''
    
        self.list = []
        self.revenue = 0

    def process(self, current_time:datetime, region_id:int) -> dict:

        ''' Evaluates how many salelines could be closed and how much revenue was generated.
            Empties list of sales.'''

        if self.list != []:

            return {PROC_DATETIME: current_time,
                    REGION_ID: region_id,
                    NUMBER_OF_LINES: self.number_of_lines,
                    LINES_CLOSED: self.number_of_lines_closed,
                    POTENTIAL_OFFLINE_REVENUE: self.potential_revenue,
                    OFFLINE_REVENUE: self.revenue,
            }
        
        else:
            return None


        
