
###############################################################################################

'''This file contains utiliy functions for importing data.'''

###############################################################################################

from os import path
from pandas import read_csv

from configs import DECIMAL_FORMAT, FILE_TYPE, INPUT_DIR, SEP_FORMAT


# def csv_to_numpy(file_name, ignore_lines=None):

#     return genfromtxt(Directory.INPUT + file_name + Formats.FILE, delimiter=Formats.SEP, skip_header=ignore_lines, missing_values=0)

def df_from_file(file_name:str, dir:str=INPUT_DIR, index_col:int=None, specific_columns:int=None, dtype=None):

    '''Returns a pandas DataFrame from a csv file.'''

    return read_csv(path.join(dir, file_name + FILE_TYPE), sep=SEP_FORMAT, decimal=DECIMAL_FORMAT, index_col=index_col, \
                    dtype=dtype, usecols=specific_columns, low_memory=True)

def from_csv(file_name:str, dir:str=INPUT_DIR, read_headers:bool=False):

    '''Returns data as list from a csv file.'''

    with open(path.join(dir, file_name + FILE_TYPE), "r") as input_file:
        
        if read_headers:
            data = input_file.read().splitlines()
    
        else:
            data = input_file.read().splitlines()[1:]

    return [line.split(SEP_FORMAT) for line in data]














        






    


    