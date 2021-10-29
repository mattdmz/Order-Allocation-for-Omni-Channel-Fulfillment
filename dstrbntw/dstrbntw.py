
###############################################################################################

'''This file contains the class Distribution_network.'''

###############################################################################################

from mysql.connector.errors import DatabaseError
from numpy import float32

from database.connector import Database, NoDataError
from database.constants import FC
from database.views import Customer_Info
from dstrbntw.constants import *
from dstrbntw.errors import ImportModelDataError
from dstrbntw.region import Region
from parameters import ALLOC_REGIONS, ORDER_PROCESSING_START, ORDER_PROCESSING_END
from utilities.general import fill_nan_in_df_with_zeros
from utilities.impdata import df_from_file


class Distribution_Network:

    def __init__(self) -> None:
        
        ''' Inits a distribution network model based which shall be based on  
            the date range delimited by the parameters ORDER_PROCESSING_START and ORDER_PROCESSING_END.'''

        # set demand analysis dates
        self.start = ORDER_PROCESSING_START
        self.end = ORDER_PROCESSING_END

    def imp_regional_data(self) -> None:

        ''' Inits region classes with all subclass (arcticles, customers, nodes, locations, deliveries)
            and import the respecitive data to feed the objects.'''

        # import data and init model
        try:

            with Database() as db:

                dict = {}

                #check if user overruled regions
                if ALLOC_REGIONS == "all":
                    
                    #import list of regions to serve
                    list_of_regions = Customer_Info(db, FC, self.start, self.end).data

                    if list_of_regions == None:
                        raise NoDataError(Customer_Info.__name__ + f"about '{FC}'")
            
                    #add regions to dict
                    for r in list_of_regions:
                        r:tuple
                        
                        region = Region()
                        region.imp(db, r[0], self.start, self.end)
                        dict[r[0]] = region
                
                else:
                    #use list of regions provided by user
                    list_of_regions = ALLOC_REGIONS

                    #add regions to dict
                    for id in list_of_regions:
                        id:int

                        region = Region()
                        region.imp(db, id, self.start, self.end)
                        dict[id] = region

            self.regions = dict

        except NoDataError as err:
            raise ImportModelDataError("database", err_name=NoDataError.__name__, err=err)
        
        except ConnectionError as err:
            raise ImportModelDataError("database", err_name=ConnectionError.__name__, err=err)
        
        except DatabaseError as err:     
            raise ImportModelDataError("database", err_name=DatabaseError.__name__, err=err)

    def determine_demand(self) -> None:

        '''Imports demand for all nodes and articles of a region.'''

        #import demand
        sum = fill_nan_in_df_with_zeros(df_from_file(SUM_DEMAND, index_col=0, dtype=float32))
        avg = fill_nan_in_df_with_zeros(df_from_file(AVG_DEMAND, index_col=0, dtype=float32))
        var = fill_nan_in_df_with_zeros(df_from_file(VAR_DEMAND, index_col=0, dtype=float32))

        #determine and store demand for each region
        for region in self.regions.values():
            region:Region

            region.store_demand(sum, avg, var)    

    def init_stock(self) -> None:
        
        '''Inits stock for all regions.'''

        for region in self.regions.values():
            region:Region

            region.analyse_demand()
            region.init_stock()



        


