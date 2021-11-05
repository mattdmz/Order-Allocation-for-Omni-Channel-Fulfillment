
###############################################################################################

'''This file contains utiliy functions for exporting data.'''

###############################################################################################

from csv import writer
from numpy import array, savetxt
from os import path, makedirs
from pandas import DataFrame

from configs import *

def write_df(df:DataFrame, file_name:str, dir_path:str=OUTPUT_DIR, mode:str="w", header:bool=False, index:bool=False)-> None:

    ''' Writes a dataframe into an export file.
        If no directory is specified, the default output directory is used.'''

    df.to_csv(path.join(dir_path, file_name + FILE_TYPE), mode=mode, sep=SEP_FORMAT, decimal=DECIMAL_FORMAT, 
                        header=header, index=index, line_terminator=LINE_TERM, float_format="%.4f")

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
        else: # mode == "a"
            # write values
            csv_writer.writerow(list(dict.values()))

def write_numpy_array(arr:array, file_name:str, dir_path:str=OUTPUT_DIR)-> None:

    '''Converts a np_array to a pandas DataFrame and
        writes the DataFrame into an export file.'''

    savetxt(file_name + FILE_TYPE, arr, fmt="%i", delimiter=SEP_FORMAT)

def write_output_file(data:list, file_name:str, dir_path:str=OUTPUT_DIR, mode:str="w")-> None:

    '''Writes data (list format) into an output file using csv writer.'''

    with open(path.join(dir_path, file_name + FILE_TYPE), mode=mode, newline="") as output_file:
        
        file_writer = writer(output_file, delimiter=SEP_FORMAT, lineterminator=LINE_TERM)
        file_writer.writerows(data)

def create_dir(dir_name:str, path_str:str=OUTPUT_DIR) -> str:
    
    '''Creates a directory inside the default output path and returns path to access it.'''

    dir_path = path.join(path_str, dir_name)

    if not path.exists(dir_path):
        makedirs(dir_path)
        return dir_path
    else:
        return None

def get_parms() -> dict:

    '''Returns a dict of the used parameters.'''

    from datetime import date, time, datetime
    import parameters as prms

    return dict([(name, constant) for name, constant in prms.__dict__.items() if isinstance(constant, (str, int, float, dict, time, date, datetime))])