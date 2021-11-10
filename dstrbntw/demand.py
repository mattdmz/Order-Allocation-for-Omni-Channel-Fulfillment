
###############################################################################################

'''This file contains the class Demand.'''

###############################################################################################

from datetime import datetime
from math import ceil
from numpy import array

from parameters import RPL_CYCLE_DURATION
from utilities.datetime import time_diff

class Demand():

    def __init__(self)-> None:
        pass

    def store(self, sum:array, avg:array, var:array) -> None:

        ''' Stores demand for all nodes and articles of a region.
            Stores regions's articles and nodes to ease access to their info.'''

        self.sum = sum
        self.avg = avg
        self.var = var 

    def __getattr__(self, attr:str, article_index:int, node_index:int) -> float:

        ''' Returns value from column(table) for a specific index (article id)'''
        
        return getattr(self, attr)[article_index, node_index]

    def expected(self, article_index:int, node_index:int, current_time:datetime, op_end_time:datetime) -> int:

        ''' Returns the expected reounded demand for the remaining time of the day (12h) for a specific article at a specific node
            if SUBTRACT_EXPECTED_STOCK_DEMAND == True else returns 0.'''

        avg_demand = self.__getattr__("avg", article_index, node_index)
        td = time_diff(op_end_time, current_time)

        return int(ceil((avg_demand / 720 * td) if td > 0 else 0 + avg_demand if current_time.date().isoweekday() % RPL_CYCLE_DURATION != 0 else 0))



