
###############################################################################################

'''This file contains functions to init and manage result protocols.'''

###############################################################################################

from numpy import array
from pandas.core.frame import DataFrame
from typing import Union

from protocols.constants import *
from utilities.expdata import create_dir, write_results, write_df, get_parms, write_dict

def create_output_dir_and_files() -> None:

    ''' Creates a directory with a uuid to export results.
        Creates the files to store results into.
        Returns the directory path.'''

    dir_path = create_dir(RUN_ID)

    write_results(init_allocation_protocol(""), ALLOCATIONS_PROTOCOL_FILE_NAME, dir_path)
    write_results(init_order_evaluation(""), ORDERS_EVALUATION_FILE_NAME, dir_path)
    write_results(init_sales_evaluation(""), SALES_EVALUATION_FILE_NAME, dir_path)
    write_results(init_results_evaluation(""), DAILY_RESULTS_FILE_NAME, dir_path)
    write_results(init_results_evaluation(""), OVERALL_RESULTS_FILE_NAME, dir_path)

    return dir_path

def init_allocation_protocol(value_to_set) -> dict:

    '''Returns a dict to store allocation results.'''

    return  {   PROC_DATETIME: value_to_set,
                REGION_ID: value_to_set,
                ITER: value_to_set,
                OBJ_VALUE: value_to_set, 
                PUNCTUALITY: value_to_set,
                ALLOC_ARR: value_to_set
            }

def init_order_evaluation(value_to_set) -> dict:

    '''Returns a dict to store allocation results.'''

    return  {   ORDER_ID: value_to_set,
                REGION_ID: value_to_set,
                ARRIVAL_DATETIME: value_to_set, 
                ALLOCATION_DATETIME: value_to_set, 
                PROC_DATETIME: value_to_set,
                ALLOCATED_NODE_ID: value_to_set,
                POTENTIAL_ONLINE_REVENUE: value_to_set,
                ONLINE_REVENUE: value_to_set,
                SUPPLY_COSTS: value_to_set, 
                ORDER_PROCESSING_COSTS: value_to_set, 
                DELIVERY_COSTS: value_to_set,
                STOCK_HOLDING_COSTS: value_to_set, 
                PROFIT: value_to_set, 
                PUNCTUALITY: value_to_set,
                DISTANCE: value_to_set
            }

def init_sales_evaluation(value_to_set) -> dict:

    '''Returns a dict to store sales evaluation results.'''

    return  {   PROC_DATETIME: value_to_set,
                REGION_ID: value_to_set,
                NUMBER_OF_LINES: value_to_set,
                LINES_CLOSED: value_to_set,
                POTENTIAL_OFFLINE_REVENUE: value_to_set,
                OFFLINE_REVENUE: value_to_set,
            }     
                
def init_results_evaluation(value_to_set) -> dict:

    '''Returns a dict to store daily/periodical results.'''

    return  {   PROC_DATETIME: value_to_set,
                REGION_ID: value_to_set,
                NUMBER_OF_LINES: value_to_set,
                LINES_CLOSED: value_to_set,
                SALES_RATE:value_to_set,
                POTENTIAL_OFFLINE_REVENUE: value_to_set,
                OFFLINE_REVENUE: value_to_set,
                REL_OFFLINE_REVENUE: value_to_set,
                NUMBER_OF_ORDERS: value_to_set,
                NUMBER_OF_PROCESSED_ORDERS: value_to_set,
                PROCESSING_RATE:value_to_set,
                POTENTIAL_ONLINE_REVENUE: value_to_set,
                ONLINE_REVENUE: value_to_set,
                REL_ONLINE_REVENUE: value_to_set,
                SUPPLY_COSTS: value_to_set, 
                ORDER_PROCESSING_COSTS: value_to_set, 
                DELIVERY_COSTS: value_to_set,
                STOCK_HOLDING_COSTS: value_to_set,
                PROFIT: value_to_set, 
                PUNCTUALITY: value_to_set,
                DISTANCE: value_to_set,
                REPLENISHMENTS:value_to_set
            }

def create_dicts(region_ids:list , dict_type) -> dict:

    '''Returns a result dict to store results for each region'''

    dict = {}

    for region_id in region_ids:
        region_id:int

        if dict_type == RESULTS:
            dict[region_id] = init_results_evaluation(0)
        else: # COUNTERS
            dict[region_id] = 0

    return dict

def increment_results(current_results:dict, new_results:Union[dict, DataFrame], result_type:str) -> dict:

    '''Adds values of new_results to the values of current_results for all colums of new_results dict.'''

    if result_type == ORDERS:   

        if isinstance(new_results.loc[0, PROC_DATETIME], datetime):
            current_results[PROC_DATETIME] = new_results.loc[0, PROC_DATETIME].date()

        current_results[REGION_ID] = new_results.loc[0, REGION_ID]
        current_results[PUNCTUALITY] = new_results[PUNCTUALITY].sum()
        number_of_orders = len(new_results.index),
        current_results[NUMBER_OF_ORDERS] = number_of_orders[0]
        current_results[NUMBER_OF_PROCESSED_ORDERS] = int(sum(array(new_results[ALLOCATED_NODE_ID]) > 0))

        for column in init_order_evaluation(0).keys():
            column:str

            if column != ARRIVAL_DATETIME and column != ALLOCATION_DATETIME and column != PROC_DATETIME and \
                column != ALLOCATED_NODE_ID and column != ORDER_ID and column != REGION_ID and column != PUNCTUALITY:      
            
                current_results[column] += sum(new_results[column])

    elif result_type == SALES:

        current_results[PROC_DATETIME] = new_results[PROC_DATETIME].date()
        current_results[REGION_ID] = new_results[REGION_ID]

        for key in [NUMBER_OF_LINES, LINES_CLOSED, POTENTIAL_OFFLINE_REVENUE, OFFLINE_REVENUE]:
            key:str       
            
            current_results[key] += new_results[key] 

    else: # result_type == RESULTS     
            
        current_results[PROC_DATETIME] = new_results[PROC_DATETIME]
        current_results[REGION_ID] = new_results[REGION_ID]

        for key, value in new_results.items():
            key:str
            value:Union[float, int]

            if key != PROC_DATETIME and key != REGION_ID:      
                current_results[key] += value

    return current_results

def evaluate_results(results:dict, counter:int) -> dict:

    '''Calculates average punctuality and distance and returns dict.'''

    if counter > 0:

        results[SALES_RATE] = results[LINES_CLOSED] / results[NUMBER_OF_LINES]
        results[REL_OFFLINE_REVENUE] = results[POTENTIAL_OFFLINE_REVENUE] / results[OFFLINE_REVENUE]
        results[PROCESSING_RATE] = results[NUMBER_OF_PROCESSED_ORDERS] / results[NUMBER_OF_ORDERS]
        results[REL_ONLINE_REVENUE] = results[POTENTIAL_OFFLINE_REVENUE] / results[ONLINE_REVENUE]
        results[PROFIT] =    (results[OFFLINE_REVENUE] + results[ONLINE_REVENUE]) \
                          -  (results[SUPPLY_COSTS] + results[ORDER_PROCESSING_COSTS] + results[DELIVERY_COSTS] + results[STOCK_HOLDING_COSTS])
        results[PUNCTUALITY] = results[PUNCTUALITY] / counter
        results[DISTANCE] = results[DISTANCE] / counter

    return results

class Result_Protocols:

    def __init__(self) -> None:
        
        # store path to output directory
        self.output_dir_path = create_output_dir_and_files()

    def init_results_dict(self, regions:list) -> None:

        # init result dicts
        self.daily_results = create_dicts(regions, RESULTS)
        self.overall_results = create_dicts(regions, RESULTS)

        # init counter for calculating average
        self.daily_counter = create_dicts(regions, 0)
        self.overall_counter = create_dicts(regions, 0)

    def store_orders_evaluation(self, orders_evaluation:Union[dict, DataFrame], region_id:int) -> None:

        ''' Stores main figures of order processing evaluation in the daily results.'''

        self.daily_results[region_id] = increment_results(self.daily_results[region_id], orders_evaluation, ORDERS)

        # raise counter to determine average
        self.daily_counter[region_id] += 1

    def store_sales_evaluation(self, sales_evaluation:dict, region_id:int) -> None:

        ''' Stores main figures of sales evaluation in the daily results.'''

        self.daily_results[region_id] = increment_results(self.daily_results[region_id], sales_evaluation, SALES)

    def store_stock_holding_costs(self, stock_holding_costs:float, region_id:int) -> None:

        ''' Stores stock holding costs in the daily results.'''
        
        self.daily_results[region_id][STOCK_HOLDING_COSTS] = stock_holding_costs

    def store_number_of_replenishments(self, number_of_replenishments:float, region_id:int) -> None:

        ''' Stores number of replenishments in the daily results.'''
        
        self.daily_results[region_id][REPLENISHMENTS] = number_of_replenishments

    def transfer_daily_results_to_overall_results(self, region_id:int) -> None:

        ''' Transfers daily result in overall results and
            resets daily results .'''
            
        self.overall_results[region_id] = increment_results(self.overall_results[region_id], self.daily_results[region_id], RESULTS)
        self.daily_results[region_id] = init_results_evaluation(0)

        self.overall_counter[region_id] += 1

    def export_allocation(self, allocation:dict) -> None:

        '''Exports order processing results to created file.'''

        write_df(DataFrame.from_dict([allocation]), ALLOCATIONS_PROTOCOL_FILE_NAME, dir_path=self.output_dir_path, mode="a")

    def export_orders_evaluation(self, orders_evaluation:DataFrame) -> None:

        '''Exports order evalution to created file.'''

        write_df(orders_evaluation, ORDERS_EVALUATION_FILE_NAME, dir_path=self.output_dir_path, mode="a")

    def export_sales_evaluation(self, sales_evaluation:dict) -> None:

        '''Exports order processing results to created file.'''

        write_df(DataFrame.from_dict([sales_evaluation]), SALES_EVALUATION_FILE_NAME, dir_path=self.output_dir_path, mode="a")

    def export_daily_results(self, region_id:int) -> None:
        
        ''' Exports daily results of region to created file.
            Resets counter.'''

        write_df(DataFrame.from_dict([evaluate_results(self.daily_results[region_id], self.daily_counter[region_id])]), \
                                        DAILY_RESULTS_FILE_NAME, dir_path=self.output_dir_path, mode="a")

        self.daily_counter[region_id] = 0

    def export_overall_results(self) -> None:
        
        ''' Exports overall results of region to created file.
            Resets daily_counter.'''

        for region_id in self.overall_results.keys():
            region_id:int
        
            write_df(DataFrame.from_dict([evaluate_results(self.overall_results[region_id], self.overall_counter[region_id])]), \
                                            OVERALL_RESULTS_FILE_NAME, dir_path=self.output_dir_path, mode="a")

            self.overall_counter[region_id] = 0

    def export_parameters_used(self) -> None:

        '''Exports the parameters used for this run to the created folder.'''

        write_dict(get_parms(), PARAMETERS_FILE_NAME, dir_path=self.output_dir_path)
    