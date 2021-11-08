
###############################################################################################

'''This file contains the class Node and its subclass Node and its subclass Vehicle.'''

###############################################################################################

from datetime import datetime, time
from mysql.connector.errors import DatabaseError

from database.connector import Database, NoDataError
from database.constants import ID
from dstrbntw.abcanalysis import Abc_Analysis 
from dstrbntw.errors import ImportModelDataError
from dstrbntw.location import Location
from dstrbntw.delivery import Delivery
from database.views import Specific_Nodes
from parameters import *
from utilities.datetime import delivered_on
from utilities.general import create_obj_dict


class Node():

    def __init__(self, index:int, data:list) -> None:

        '''Assigns index (int) to instance and 
            assigns imported data to attributes.'''

        #index used to access this element in an array/matrix
        self.index = index
        
        #assign attributes
        self.id = data[0]
        self.node_type = data[1]
        #self.address = data[2]
        #self.zip = data[3]
        self.zip_region = data[4]
        self.city = data[5]
        #self.gkz = data[6]
        self.location = Location(self.id, float(data[7]), float(data[8]))
        self.fc = data[9]
        self.supply_distance = float(data[10])
        self.start_stock_rate = float(data[11])

        #set up order acceptance status
        self.accepting_orders = True

        #init delivery delivery_tour
        self.delivery = Delivery(self.node_type, self.location)

    @property
    def supply_rate(self) -> float:

        '''Returns pallet rate for the supply of the node, depending on the node's supply distance.'''

        return PAL_RATE * self.supply_distance

    @property
    def stock_holding_rate(self) -> float:

        '''Returns stock holding rate based on node type.'''

        return STOCK_HOLDING_RATE[self.node_type]
        
    @property
    def order_processing_rate(self) -> float:

        '''returns order processing rate based on node type'''
            
        return ORDER_PROCESSING_RATE[self.node_type]

    @property
    def tour_rate(self) -> float:

        '''returns fix delivery rate per delivery tour'''

        return TOUR_RATE[self.node_type]
        
    @property
    def route_rate(self) -> float:

        '''returns variable cost rate per working minute'''

        return ROUTE_RATE[self.node_type]  

    @property
    def order_processing_capacity(self) -> float:

        '''Returns the order processing capacity in number of orderlines per minute for a specific node type.'''

        return OP_CAPACITY[self.node_type]   

    def set_order_acceptance_status(self, new_status:bool) -> None:

        '''sets the status of order aceptance of the node to True or False. 
            If True, orders are accepted for processing.'''

        self.accepting_orders = new_status

    def delivery_restarts_tomorrow(self, current_time:datetime) -> None:

        '''Sets node.delivery.day on current date + 1 day.'''

        self.delivery.day = delivered_on(datetime.combine(current_time.date() + timedelta(days = 1), time(0, 1, 0)), self.node_type) 

    def store_demand_analysis(self, abc_analysis_demand:Abc_Analysis)-> None:

        '''Carries out abc analysis of demand at node.'''

        self.abc_analysis_demand = abc_analysis_demand

    def processing_duration(self, lines_to_process:int) -> int:

        '''Returns the rounded processing duration for a batch of orderlines to process in minutes.'''

        return int(round(self.order_processing_capacity * lines_to_process, 0))

    def reset_delivery(self) -> None:

        '''Resets delivery object.'''

        self.delivery = Delivery(self.node_type, self.location)

class Nodes:

    def __init__(self) -> None:
        pass
    
    @property
    def stock_holding_rates(self) -> list:

        '''Returns a list of stock holding rates per node.'''

        return list(node.stock_holding_rate for node in self.dict.values())
    
    @property
    def tour_rates(self) -> list:

        '''Returns a list of tour rates per node.'''

        return list(node.tour_rate for node in self.dict.values())
        
    @property
    def route_rates(self) -> list:

        '''Returns a list of route rates per node.'''

        return list(node.route_rate for node in self.dict.values())

    @property
    def start_stock_rates(self) -> list:

        '''Returns a list of start stock rates per node.'''

        return list(node.start_stock_rate for node in self.dict.values())

    @property
    def tour_durations(self) -> list:

        ''' Returns a list of all delivery_tour durations.'''

        return list(node.delivery.tot_duration for node in self.dict.values())

    @property
    def accepting_orders(self) -> list:

        '''Returns a list of currently available nodes based on the accepting_orders status of each node.'''

        return list(node for node in self.dict.values() if node.accepting_orders)

    def imp(self, db:Database, node_type:int=None, region_column:str=None, region_id:int=None) -> None:

        ''' Fetches data from db about nodes and stores them as node object in a dict 
            which is set as attribute of Nodes with 
            the node.id as key and the node-object as value.'''

        try:

            data = Specific_Nodes(db, columns="*", node_type=node_type, region_column=region_column, region=region_id).data

            if data == None:
                raise NoDataError(Specific_Nodes.__name__ + f"for {region_column}: {region_id}")
            
            self.dict = create_obj_dict(data, Node, key=ID)
            self.index_dict = self.create_index_dict()

        except NoDataError as err:
            raise ImportModelDataError("database", err_name=NoDataError.__name__, err=err)
        
        except ConnectionError as err:
            raise ImportModelDataError("database", err_name=ConnectionError.__name__, err=err)
        
        except DatabaseError as err:     
            raise ImportModelDataError("database", err_name=DatabaseError.__name__, err=err)

    def __get__(self, id:int=None, index:int=None) -> Node:

        '''Returns a node from the nodes.dict based on its id or index.'''

        return self.dict[self.index_dict[index]] if index is not None else self.dict[id]

    def __getattr__(self, attr:str, id:int=None, index:int=None):

        '''Returns a node's attribute based on its id orindex in the nodes.dict.'''

        return getattr(self.dict[self.index_dict[index]], attr) if index is not None else getattr(self.dict[id], attr) 

    def create_index_dict(self):

        '''Returns a dict where nodes can be accessed by their indexes.'''
        
        index_dict = {}

        for node in self.dict.values():
            node:Node

            index_dict[node.index] = node.id

        return index_dict

    def change_order_acceptance_status(self, status:bool) -> None:

        '''Sets order accepting status for all nodes to True/False depending on status.'''

        for node in self.dict.values():
            node:Node
            
            node.accepting_orders = status 
            

















