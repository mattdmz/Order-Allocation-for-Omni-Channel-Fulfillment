
###############################################################################################

'''This file contains the class Distribution_network.'''

###############################################################################################

from datetime import datetime, timedelta, time
from mysql.connector.errors import DatabaseError
from numpy import float32
from pandas import DataFrame

from allocmethod import ALLOC_METHOD, ALLOC_OPERATOR
from allocation.constants import *
from configs import ALLOCATIONS_FILE_NAME, PROCESSED_ORDERS_FILE_NAME, PROCESSED_SALES_FILE_NAME, RESULTS_FILE_NAME
from database.connector import Database, NoDataError
from database.constants import DATE, FC, ID
from database.views import Customer_Info
from dstrbntw.constants import *
from dstrbntw.errors import ImportModelDataError
from dstrbntw.region import Region
from parameters import ALLOC_PERIOD, ALLOC_REGIONS, CUT_OFF_TIME, DEMAND_ANALYSIS_START, DEMAND_ANALYSIS_END, ORDER_PROCESSING_START, ORDER_PROCESSING_END
from utilities.expdata import create_output_dir, create_output_files, write_df, write_results
from utilities.general import fill_nan_in_df_with_0s
from utilities.impdata import df_from_file
from utilities.timesim import daterange, timerange


class Distribution_Network:

    def __init__(self) -> None:
        
        '''Inits a model and sets default dates from parameters (DEMAND_ANALYSIS_START, DEMAND_ANALYSIS_END) 
            if not overrwritten by user if not specified.'''

        # set demand analysis dates
        self.start = DEMAND_ANALYSIS_START
        self.end = DEMAND_ANALYSIS_END

        # set order processing dates
        self.op_start = ORDER_PROCESSING_START
        self.op_end = ORDER_PROCESSING_END

        self.alloc_period = ALLOC_PERIOD

    @property
    def next_allocation_time(self) -> datetime:

        '''Returns the next time orders should be processed.'''

        return self.allocation_schedule[0] if len(self.allocation_schedule) > 0 else None

    def imp_data(self) -> dict:

        '''Fetches data from db from a region and stores it as region object in a dict.'''

        try:

            with Database() as db:

                dict = {}

                #check if user overruled regions
                if ALLOC_REGIONS == None:
                    
                        #import list of regions to serve
                        list_of_regions = Customer_Info(db, FC, self.start, self.end).data

                        if list_of_regions == None:
                            raise NoDataError(Customer_Info.__name__ + f"about '{FC}'")
                
                        #add regions to dict
                        for r in list_of_regions:
                            region = Region()
                            region.add(db, r, self.start, self.end)
                            dict[r[0]] = region
                
                else:
                    #use list of regions provided by user
                    list_of_regions = ALLOC_REGIONS

                    #add regions to dict
                    for id in list_of_regions:
                        region = Region()
                        region.add(db, id, self.start, self.end)
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
        sum = fill_nan_in_df_with_0s(df_from_file(SUM_DEMAND, index_col=0, dtype=float32))
        avg = fill_nan_in_df_with_0s(df_from_file(AVG_DEMAND, index_col=0, dtype=float32))
        var = fill_nan_in_df_with_0s(df_from_file(VAR_DEMAND, index_col=0, dtype=float32))

        #determine and store demand for each region
        for region in self.regions.values():
            region.store_demand(sum, avg, var)    

    def init_stock(self) -> None:
        
        '''Inits stock for all regions.'''

        for region in self.regions.values():
            region.analyse_demand()
            region.init_stock()

    def init_evaluation_model(self) -> None:

        '''Inits model to evaluate allocations.'''
        for region in self.regions.values():
            region.init_evaluation_model()

    def init_allocation_schedule(self) -> list:

        '''Returns an allocation schedule based on self.alloc_period.'''

        #init optimization schedule
        allocation_schedule = []

        for date in daterange(self.op_start, self.op_end):

            this_time = datetime.combine(date, time(0,0,0))
            end_time = datetime.combine(date + timedelta(days=1), time(0,0,0))

            #construct optimization schedule
            while this_time + self.alloc_period < end_time:         

                #determine next cut-off for optimization
                this_time += self.alloc_period
                #add time to schedule
                allocation_schedule.append(this_time)

        return allocation_schedule

    def init_protocols_and_export_files(self) -> None:

        #init optimization schedule
        self.allocation_schedule = self.init_allocation_schedule() 

        # create dir to store output files
        self.output_dir = create_output_dir()

        create_output_files(self.output_dir)  

    def terminate_allocation(self) -> None:
        
        '''Deletes allocation time from allocation schedule after it was completed.'''

        del self.allocation_schedule[0] 

    def actions(self, current_time:datetime, cut_off_time:datetime) -> None:

        '''Actions to carry out during time simulation.'''

        # determine actions to be carried out at current_time
        for region in self.regions.values():

            # collect profit generated from processing orders and closing sales
            processing_results = region.actions(current_time, cut_off_time)

            if processing_results is not None:

                # export processing_results
                write_df(processing_results, PROCESSED_ORDERS_FILE_NAME, self.output_dir, mode="a")
        
            # check if allocation must occure at current time based on predefined optimizaiton schedule
            if current_time == self.next_allocation_time:
                
                # allocate orders and check processability of sales and export results from alloaction
                allocation = region.start_allocation(ALLOC_METHOD, current_time, self.alloc_period, cut_off_time, ALLOC_OPERATOR)
                write_results(allocation, ALLOCATIONS_FILE_NAME, self.output_dir, mode="a")

                # evaluate sales and export results from evaluation
                if len(region.sales.list) > 0:

                    selling_results = region.sales.evaluate(region.id, current_time)
                    write_results(selling_results, PROCESSED_SALES_FILE_NAME, self.output_dir, mode="a")

                    # store revenue calcualted when evaluating sales and clear list of imported sales
                    region.sales.store_revenue(selling_results)
                    region.sales.clear()

                self.terminate_allocation()

    def start_timesim(self) -> None:

        ''' Iterates through time between order_processing_start and order_processing_end to determine 
            actions to be carried out at certain timestamps'''

        # days
        for date in daterange(ORDER_PROCESSING_START, ORDER_PROCESSING_END + timedelta(days=1)):

            # set new cut off time for order processing
            cut_off_time = datetime.combine(date, CUT_OFF_TIME)

            start_date_time = datetime.combine(date, time(0, 0, 1))
            end_date_time = datetime.combine(date, time(23, 59, 0))

            # hours
            for hour in timerange(start_date_time, end_date_time, "hours"):

                start_date_time_2 = datetime.combine(start_date_time, time(hour.hour, 0, 1))
                end_date_time_2 = datetime.combine(end_date_time, time(hour.hour, 0, 0))

                # minutes
                for minute in timerange(start_date_time_2, end_date_time_2 + timedelta(hours=1, minutes=1), "minutes"):
                    
                    # define current time
                    current_time = datetime.combine(start_date_time_2, time(hour.hour, minute.minute, 0))

                    # check if actions need to be taken for current time
                    self.actions(current_time, cut_off_time)                   

    def export_results(self) -> None:

        '''Exports results of timesim in created directory.'''

        results = DataFrame(columns=[DATE, ID, PROFIT, REPLENISHMENTS, HOLDING_COSTS])

        for region in self.regions.values():

            # get results dict
            results = results.append(region.summarize_results(), ignore_index=True)

        # export results to file
        write_df(results, RESULTS_FILE_NAME, header=True, index=False)

