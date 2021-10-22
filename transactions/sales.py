
###############################################################################################

'''This file contains the class Sales and its subclass Sale and its child class Lines.'''

###############################################################################################


from datetime import datetime

from dstrbntw.articles import Articles
from dstrbntw.constants import REGION_ID, PROC_TIME, LINES, LINES_CLOSED, POTENTIAL_REVENUE, REALIZED_REVENUE, REL_LINES_CLOSED, REL_REALIZED_REVENUE
from dstrbntw.nodes import Nodes


class Sale():

    def __init__(self, data:list, nodes:Nodes) -> None:

        ''' Assigns index (int) to instance and 
            assigns imported data to attributes.'''
        
        # assign attributes
        self.id = data[0]
        node_id = data[1]
        self.date_time = datetime.combine(data[2], datetime.min.time()) + data[3]
        # self.price = float(data[4])
        # self.volume = float(data[5])
        # self.weight = float(data[6])

        # adds the node where the sale took place based on the node_id imported
        self.node = nodes.__get__(node_id)

        # init sales lines (to be added)
        self.lines = []

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

        # init list to store sales
        self.list = []

        # init revenue
        self.revenue = 0

    def __get__(self, id:int) -> Sale:

        '''Returns a sale from the sales.list based on its id.'''

        return self.list[id]

    def __getattr__(self, id:int, attr:str):

        '''Returns an sale's attribute based on its id in the sales.list.'''

        return getattr(self.list[id], attr)

    def clear(self) -> None:

        '''Clears list of sales.'''
    
        self.list = []

    def store_revenue(self, result:dict) -> None:

        '''Adds revenue to current revenue.'''

        self.revenue += result[REALIZED_REVENUE]
        
    def collect_revenue(self) -> float:

        '''Returns revenue and resets revenue attribute.'''

        revenue = self.revenue
        self.revenue = 0
        return revenue

    def evaluate(self, region_id:int, current_time:datetime) -> dict:

        ''' Evaluates how many salelines could be closed and how much revenue was generated.
            Empties list of sales.'''

        # init counters
        realized_revenue = 0
        potential_revenue = 0
        assessed_lines = 0
        closed_lines = 0

        # determine realised revenue and processed_lines and closed_lines
        for sale in self.list:
            assessed_lines += len(sale.lines)
            for line in sale.lines:
                closed_lines += 1 if line.closed else 0
                realized_revenue += line.revenue
                potential_revenue += line.article.price * line.quantity

        self.list = []

        return {PROC_TIME: current_time,
                REGION_ID: region_id,
                LINES: assessed_lines,
                LINES_CLOSED: closed_lines,
                REL_LINES_CLOSED: assessed_lines / closed_lines,
                POTENTIAL_REVENUE: potential_revenue,
                REALIZED_REVENUE: realized_revenue,
                REL_REALIZED_REVENUE: potential_revenue / realized_revenue
        }


        
