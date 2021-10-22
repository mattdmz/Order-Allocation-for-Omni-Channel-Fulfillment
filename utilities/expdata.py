
###############################################################################################

'''This file contains utiliy functions for exporting data.'''

###############################################################################################

from csv import writer
from numpy import array
from os import path, makedirs
from pandas import DataFrame
from uuid import uuid4
from allocation.constants import ALLOC_ARR, ITER, OBJ_VALUE, PUNCTUALITY

from configs import *
from database.constants import ID
from dstrbntw.constants import *

def write_df(df:DataFrame, file_name:str, dir_path:str=OUTPUT_DIR, mode:str="w", header:bool=False, index:bool=False)-> None:

    ''' Writes a dataframe into an export file.
        If no directory is specified, the default output directory is used.'''

    df.to_csv(path.join(dir_path, file_name + FILE_TYPE), mode=mode ,sep=SEP_FORMAT, decimal=DECIMAL_FORMAT, header=header, index=index, line_terminator=LINE_TERM)

def write_dict(dict:dict, file_name:str, dir_path:str=OUTPUT_DIR, mode:str="w") -> None:
    
    '''Writes a dict into an export file.'''

    with open(path.join(dir_path, file_name + FILE_TYPE), mode=mode, newline="") as output_file:  
        
        csv_writer = writer(output_file, delimiter=SEP_FORMAT, lineterminator=LINE_TERM)
        
        for key, value in dict.items():
            csv_writer.writerow([key, value])

def write_results(dict:dict, file_name:str, dir_path:str=OUTPUT_DIR, mode:str="w") -> None:
    
    '''Writes a dict into an export file.'''

    with open(path.join(dir_path, file_name + FILE_TYPE), mode=mode, newline="") as output_file:  
        
        csv_writer = writer(output_file, delimiter=SEP_FORMAT, lineterminator=LINE_TERM)
        
        if mode == "w":
            # write headers
            csv_writer.writerow(list(dict.keys()))
        else:
            # write values
            csv_writer.writerow(list(dict.values()))

def write_numpy_array(arr:array, file_name:str, dir_path:str=OUTPUT_DIR, header:list=None, index:list=None)-> None:

    '''Converts a np_array to a pandas DataFrame and
        writes the DataFrame into an export file.'''

    df = DataFrame(arr, columns=[header], index=[index])

    #determine if headers and indexes should be written
    header = True if header is not None else False
    index = True if index is not None else False

    #write df to csv
    df.to_csv(path.join(dir_path, file_name + FILE_TYPE), sep=SEP_FORMAT, decimal=DECIMAL_FORMAT, mode='w', header=header, index=index)

def write_output_file(data:list, file_name:str, dir_path:str=OUTPUT_DIR, mode:str="w")-> None:

    '''Writes data (list format) into an output file using csv writer.'''

    with open(path.join(dir_path, file_name + FILE_TYPE), mode=mode, newline="") as output_file:
        
        file_writer = writer(output_file, delimiter=SEP_FORMAT, lineterminator=LINE_TERM)
        file_writer.writerows(data)

def make_dir(dir_name:str, path_str:str=OUTPUT_DIR) -> str:
    
    '''Creates a directory inside the default output path and returns path to access it.'''
    
    try:

        dir_path = path.join(path_str, dir_name)

        if not path.exists(dir_path):
            makedirs(dir_path)

            return dir_path

    except OSError:
        print ('Error: Creating directory: ' +  dir_path)

def create_output_dir() -> str:

    ''' Creates a directory with an uuid to export results.
        Returns the directory path.'''

    return make_dir(str(uuid4()))

def create_output_files(output_dir:str) -> None:

    '''Creates files to export results to.'''

    # create file to store results from order allocations
    write_results({ PROC_TIME: "",
                    REGION_ID: "",
                    ITER: "", 
                    OBJ_VALUE: "", 
                    PUNCTUALITY: "",
                    ALLOC_ARR: ""}, 
                    ALLOCATIONS_FILE_NAME, output_dir)

    # create file to store results from order allocations
    write_results({ ID: "",
                    ALLOCATION: "",
                    PROFIT: "", 
                    SUPPLY_COSTS: "", 
                    ORDER_PROCESSING_COSTS: "", 
                    DELIVERY_COSTS: ""}, 
                    PROCESSED_ORDERS_FILE_NAME, output_dir)

    # create file to store results from sales
    write_results({ PROC_TIME: "",
                    REGION_ID: "",
                    LINES: "",
                    LINES_CLOSED: "",
                    REL_LINES_CLOSED: "",
                    POTENTIAL_REVENUE: "",
                    REALIZED_REVENUE: "",
                    REL_REALIZED_REVENUE: ""}, 
                    PROCESSED_SALES_FILE_NAME, output_dir)

def exp_results(dir_path:str, allocations:DataFrame, results:DataFrame) -> None:

    ''' Creates export files with the results from timesim.'''

    write_df(allocations, ALLOCATIONS_FILE_NAME, dir=dir_path, header=True, index=True)
    write_df(results, RESULTS_FILE_NAME, dir=dir_path, header=True, index=True)

