
###############################################################################################

'''This file contains functions to init and manage result protocols.'''

###############################################################################################

from datetime import datetime, date
from pandas.core.frame import DataFrame
from typing import Union

from allocation.constants import DELIVERY_NOT_EXECUTABLE, STOCK_NOT_AVAILABLE
from dstrbntw.constants import FULFILLMENT_CENTER, REGULAR_STORE, SMALL_STORE
from protocols.constants import *
from utilities.expdata import create_dir, write_results, write_df, get_parms, write_dict
from utilities.general import count_occurrences

def create_output_dir_and_files(experiment_dir_path:str, run_id:str) -> None:

    ''' Creates a directory at experiment_dir_path.
        Creates the files to store results into.
        Returns the directory path.'''

    dir_path = create_dir(experiment_dir_path)

    write_results(init_allocation_protocol(""), run_id + ALLOCATIONS_PROTOCOL_FILE_NAME, dir_path)
    write_results(init_order_evaluation(""), run_id + ORDERS_EVALUATION_FILE_NAME, dir_path)
    write_results(init_sales_evaluation(""), run_id + SALES_EVALUATION_FILE_NAME, dir_path)
    write_results(init_results_evaluation(""), run_id + DAILY_RESULTS_FILE_NAME, dir_path)
    write_results(init_results_evaluation(""), run_id + OVERALL_RESULTS_FILE_NAME, dir_path)

    return dir_path

def init_allocation_protocol(value_to_set) -> dict:

    '''Returns a dict to store allocation results.'''

    return  {   PROC_DATETIME: value_to_set,
                REGION_ID: value_to_set,
                ITER: value_to_set,
                BEST_OBJ_VALUE: value_to_set, 
                NUMBER_OF_ORDERS: value_to_set,
                RETRY: value_to_set,
                SAMEDAY_DELIVERY: value_to_set, 
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
                DIMINUISHED_STOCK_VALUE: value_to_set, 
                PROFIT: value_to_set,
                DELIVERED_ORDERS: value_to_set, 
                SAMEDAY_DELIVERY: value_to_set,
                RETRY: value_to_set,
                DELIVERY_DURATION: value_to_set,  
                DISTANCE: value_to_set,
                NODE_TYPE: value_to_set
    }

def init_sales_evaluation(value_to_set) -> dict:

    '''Returns a dict to store sales evaluation results.'''

    return  {   PROC_DATETIME: value_to_set,
                REGION_ID: value_to_set,
                NUMBER_OF_LINES: value_to_set,
                LINES_CLOSED: value_to_set,
                REL_LINES_CLOSED: value_to_set,
                POTENTIAL_OFFLINE_REVENUE: value_to_set,
                OFFLINE_REVENUE: value_to_set,
                REL_OFFLINE_REVENUE: value_to_set,
                DIMINUISHED_STOCK_VALUE: value_to_set,
            }     
                
def init_results_evaluation(value_to_set) -> dict:

    '''Returns a dict to store daily/periodical results.'''

    return  {   ALGORITHM_USED:value_to_set,
                PROC_DATETIME: value_to_set,
                REGION_ID: value_to_set,
                NUMBER_OF_LINES: value_to_set,
                LINES_CLOSED: value_to_set,
                SALES_RATE:value_to_set,
                POTENTIAL_OFFLINE_REVENUE: value_to_set,
                OFFLINE_REVENUE: value_to_set,
                REL_OFFLINE_REVENUE: value_to_set,
                POTENTIAL_ONLINE_REVENUE: value_to_set,
                ONLINE_REVENUE: value_to_set,
                REL_ONLINE_REVENUE: value_to_set,
                DIMINUISHED_STOCK_VALUE: value_to_set,
                SUPPLY_COSTS: value_to_set, 
                ORDER_PROCESSING_COSTS: value_to_set, 
                DELIVERY_COSTS: value_to_set,
                PROFIT: value_to_set,
                STOCK_HOLDING_COSTS: value_to_set,
                NUMBER_OF_ORDERS: value_to_set,
                DELIVERED_ORDERS: value_to_set,
                SAMEDAY_DELIVERY: value_to_set, 
                SAMEDAY_DELIVERY_RATE: value_to_set,
                RETRY: value_to_set,
                DELIVERY_DURATION: value_to_set,
                AVG_DELIVERY_DURATION: value_to_set,
                DISTANCE: value_to_set,
                AVG_DISTANCE: value_to_set,
                OUT_OF_STOCK: value_to_set,
                REPLENISHMENTS: value_to_set,
                MISSING_STOCK: value_to_set,
                DELIVERY_UNEXECUTABLE: value_to_set,
                FC_ALLOCATION: value_to_set,
                REGULAR_STORE_ALLOCATION: value_to_set,
                SMALL_STORE_ALLOCATION: value_to_set
    }

def create_dicts(region_ids:list) -> dict:

    '''Returns a result dict to store results for each region'''

    dict = {}

    for region_id in region_ids:
        region_id:int

        dict[region_id] = init_results_evaluation(0)

    return dict

def increment_results(current_results:dict, new_results:Union[dict, DataFrame], keys:list) -> None:

    '''Adds values of new_results to the values of current_results in dict for all passed keys.'''

    for key in keys:
        if isinstance(new_results, dict):
            current_results[key] += new_results[key]
        else:
            current_results[key] += new_results[key].sum()

def evaluate_results(results:dict, daily:bool, algorithm_used:str, proc_days:str) -> dict:

    '''Calculates average SAMEDAY_DELIVERY and distance and returns dict.'''

    results[ALGORITHM_USED] = algorithm_used
    results[PROC_DATETIME] = proc_days

    results[SALES_RATE] = results[LINES_CLOSED] / results[NUMBER_OF_LINES] if not results[NUMBER_OF_LINES] == 0 else 0
    results[REL_OFFLINE_REVENUE] = results[OFFLINE_REVENUE] / results[POTENTIAL_OFFLINE_REVENUE] if not results[POTENTIAL_OFFLINE_REVENUE] == 0 else 0
    results[REL_ONLINE_REVENUE] = results[ONLINE_REVENUE] / results[POTENTIAL_ONLINE_REVENUE] if not results[POTENTIAL_ONLINE_REVENUE] == 0 else 0
    results[PROFIT] =    results[OFFLINE_REVENUE] + results[ONLINE_REVENUE] + results[DIMINUISHED_STOCK_VALUE] \
                        -  results[SUPPLY_COSTS] - results[ORDER_PROCESSING_COSTS] - results[DELIVERY_COSTS]
    results[AVG_DELIVERY_DURATION] = results[DELIVERY_DURATION] / results[DELIVERED_ORDERS] if not results[DELIVERED_ORDERS] == 0 else 0
    results[AVG_DISTANCE] = results[DISTANCE] / results[DELIVERED_ORDERS] if not results[DELIVERED_ORDERS] == 0 else 0

    if daily:
        results[SAMEDAY_DELIVERY_RATE] = results[SAMEDAY_DELIVERY] / results[DELIVERED_ORDERS] if not results[DELIVERED_ORDERS] == 0 else 0
    else: # False -> overall
        results[SAMEDAY_DELIVERY_RATE] = results[SAMEDAY_DELIVERY] / results[NUMBER_OF_ORDERS] if not results[NUMBER_OF_ORDERS] == 0 else 0

    return results

class Result_Protocols:

    def __init__(self, experiment_dir_path:str, run_id:str, allocation_method:object) -> None:
        
        '''Sets a run id with the current datetime and creates an output directory with the result protocol files.'''
        
        self.run_id =  run_id
        self.output_dir_path = create_output_dir_and_files(experiment_dir_path, self.run_id)
        self.allocation_method = allocation_method.__name__

    def init_results_dict(self, regions:list) -> None:

        # init result dicts
        self.daily_results = create_dicts(regions)
        self.overall_results = create_dicts(regions)

    def store_imported_trsct_eval(self,  imported_trsct_evaluation:dict, region_id:int) -> None:

        '''Stores information about imported transactions (orders, sales).'''

        if not imported_trsct_evaluation == {}:

            keys = [NUMBER_OF_ORDERS, POTENTIAL_ONLINE_REVENUE, NUMBER_OF_LINES, POTENTIAL_OFFLINE_REVENUE]
            
            increment_results(self.daily_results[region_id], imported_trsct_evaluation, keys)

    def store_orders_evaluation(self, orders_evaluation:Union[DataFrame, dict], region_id:int) -> None:

        ''' Stores main figures of order processing evaluation in the daily results.'''

        if len(orders_evaluation.index) > 0:

            self.daily_results[region_id][REGION_ID] = region_id
            self.daily_results[region_id][PROC_DATETIME] = orders_evaluation.loc[0, PROC_DATETIME].date() \
                                                           if isinstance(orders_evaluation.loc[0, PROC_DATETIME], datetime) \
                                                           else self.daily_results[region_id][PROC_DATETIME] 
            self.daily_results[region_id][FC_ALLOCATION] +=   count_occurrences(orders_evaluation, NODE_TYPE, FULFILLMENT_CENTER)
            self.daily_results[region_id][REGULAR_STORE_ALLOCATION] +=   count_occurrences(orders_evaluation, NODE_TYPE, REGULAR_STORE)
            self.daily_results[region_id][SMALL_STORE_ALLOCATION] +=  count_occurrences(orders_evaluation, NODE_TYPE, SMALL_STORE)
            self.daily_results[region_id][MISSING_STOCK] +=  count_occurrences(orders_evaluation, ALLOCATED_NODE_ID, STOCK_NOT_AVAILABLE)
            self.daily_results[region_id][DELIVERY_UNEXECUTABLE] +=  count_occurrences(orders_evaluation, ALLOCATED_NODE_ID, DELIVERY_NOT_EXECUTABLE)

            keys = [DELIVERED_ORDERS, ONLINE_REVENUE, DIMINUISHED_STOCK_VALUE, SUPPLY_COSTS, ORDER_PROCESSING_COSTS, 
                    DELIVERY_COSTS, RETRY, SAMEDAY_DELIVERY, DISTANCE, DELIVERY_DURATION]
            
            increment_results(self.daily_results[region_id], orders_evaluation, keys)

    def store_sales_evaluation(self, sales_evaluation:dict, region_id:int, current_time:datetime) -> None:

        ''' Stores main figures of sales evaluation in the daily results.'''

        if not sales_evaluation == {}:
            
            self.daily_results[region_id][REGION_ID] = region_id
            self.daily_results[region_id][PROC_DATETIME] = current_time.date()
        
            keys = [LINES_CLOSED, OFFLINE_REVENUE, DIMINUISHED_STOCK_VALUE]
            increment_results(self.daily_results[region_id], sales_evaluation, keys)

    def store_out_of_stock_situations(self, out_of_stocks:int, region_id:int) -> None:

        ''' Stores stock holding costs in the daily results.'''
        
        self.daily_results[region_id][OUT_OF_STOCK] += out_of_stocks

    def store_stock_holding_costs(self, stock_holding_costs:float, region_id:int) -> None:

        ''' Stores stock holding costs in the daily results.'''
        
        self.daily_results[region_id][STOCK_HOLDING_COSTS] += stock_holding_costs

    def store_number_of_replenishments(self, number_of_replenishments:float, region_id:int) -> None:

        ''' Stores number of replenishments in the daily results.'''
        
        self.daily_results[region_id][REPLENISHMENTS] += number_of_replenishments

    def transfer_daily_results_to_overall_results(self, region_id:int) -> None:

        ''' Transfers daily result in overall results and
            resets daily results .'''

        self.overall_results[region_id][REGION_ID] = region_id

        keys = [NUMBER_OF_LINES, LINES_CLOSED, POTENTIAL_OFFLINE_REVENUE, OFFLINE_REVENUE,
                DELIVERED_ORDERS, NUMBER_OF_ORDERS, POTENTIAL_ONLINE_REVENUE, ONLINE_REVENUE, 
                DIMINUISHED_STOCK_VALUE, SUPPLY_COSTS, REPLENISHMENTS, OUT_OF_STOCK, ORDER_PROCESSING_COSTS, DELIVERY_COSTS, 
                STOCK_HOLDING_COSTS, RETRY, SAMEDAY_DELIVERY, DELIVERY_DURATION, DISTANCE, 
                FC_ALLOCATION, REGULAR_STORE_ALLOCATION, SMALL_STORE_ALLOCATION,
                MISSING_STOCK, DELIVERY_UNEXECUTABLE]
               
        increment_results(self.overall_results[region_id], self.daily_results[region_id], keys)

        # reset daily results
        self.daily_results[region_id] = init_results_evaluation(0)

    def export_allocation(self, allocation:dict) -> None:

        '''Exports order processing results to created file.'''

        write_df(DataFrame.from_dict([allocation]), self.run_id + ALLOCATIONS_PROTOCOL_FILE_NAME, dir_path=self.output_dir_path, mode="a")

    def export_orders_evaluation(self, orders_evaluation:DataFrame) -> None:

        '''Exports order evalution to created file.'''

        write_df(orders_evaluation, self.run_id + ORDERS_EVALUATION_FILE_NAME, dir_path=self.output_dir_path, mode="a")

    def export_optimization_protocol(self, optimization_protocol:DataFrame, current_time:datetime) -> None:

        '''Exports optimization protocol.'''

        write_df(optimization_protocol, self.run_id + OPT_PROTOCOL_FILE_NAME + current_time.strftime("%m%d%h%m"), \
                 dir_path=self.output_dir_path, header=True, index=True)

    def export_sales_evaluation(self, sales_evaluation:dict) -> None:

        '''Exports order processing results to created file.'''

        write_df(DataFrame.from_dict([sales_evaluation]), self.run_id + SALES_EVALUATION_FILE_NAME, dir_path=self.output_dir_path, mode="a")

    def export_daily_results(self, region_id:int, current_time:datetime) -> None:
        
        ''' Exports daily results of region to created file.
            Resets counter.'''

        write_df(DataFrame.from_dict([evaluate_results(self.daily_results[region_id], True, self.allocation_method, current_time.date().strftime("%m-%d"))]), \
                                        self.run_id + DAILY_RESULTS_FILE_NAME, dir_path=self.output_dir_path, mode="a")

    def export_overall_results(self, start:date, end:date) -> None:
        
        ''' Exports overall results of region to created file.
            Resets daily_counter.'''

        proc_period = start.strftime("%Y-%m-%d") + "_" + end.strftime("%Y-%m-%d")

        for region_id in self.overall_results.keys():
            region_id:int
        
            write_df(DataFrame.from_dict([evaluate_results(self.overall_results[region_id], True, self.allocation_method, proc_period)]), \
                                            self.run_id + OVERALL_RESULTS_FILE_NAME, dir_path=self.output_dir_path, mode="a")

    def export_parameters_used(self) -> None:

        '''Exports the parameters used for this run to the created folder.'''

        write_dict(get_parms(), self.run_id + PARAMETERS_FILE_NAME, dir_path=self.output_dir_path)
    