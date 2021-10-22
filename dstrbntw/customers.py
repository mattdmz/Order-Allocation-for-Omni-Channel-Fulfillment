
###############################################################################################

'''This file contains the class Customers and its subclass Customer.'''

###############################################################################################


from datetime import date
from mysql.connector.errors import DatabaseError

from database.connector import Database, NoDataError
from database.constants import ID
from database.views import Customers_Buying_Online
from dstrbntw.errors import ImportModelDataError
from utilities.general import create_obj_dict
from dstrbntw.location import Location


class Customer:

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
        #self.zip_region = data[4]
        #self.city = data[5]
        #self.gkz = data[6]
        self.location = Location(self.id, float(data[7]), float(data[8]))
        self.fc = data[9]


class Customers:

    '''Class to handle a set of customers.'''

    def __init__(self) -> None:
        pass

    def imp(self, db:Database, fc:int, start:date=None, end:date=None) -> None:

        '''Fetches data from db about customers and stores them as customer object in a dict 
            which is set as attribute of Customers with 
            the customer.id as key and the customer-object as value.'''

        try:

            data = Customers_Buying_Online(db, columns="*", start=start, end=end, fc=fc).data
            
            if data == None:
                raise NoDataError(Customers_Buying_Online.__name__ + f"for fulfuillment region: {fc}")
            
            self.dict = create_obj_dict(data, Customer, key=ID)

        except NoDataError as err:
            raise ImportModelDataError("database", err_name=NoDataError.__name__, err=err)
        
        except ConnectionError as err:
            raise ImportModelDataError("database", err_name=ConnectionError.__name__, err=err)
        
        except DatabaseError as err:     
            raise ImportModelDataError("database", err_name=DatabaseError.__name__, err=err)

    def __get__(self, id:int) -> Customer:

        '''Returns a customer from the customers.dict based on its id.'''

        return self.dict[id]

    def __getattr__(self, id:int, attr:str):

        '''Returns a customer's attribute based on its id in the customers.dict.'''

        return getattr(self.dict[id], attr)
