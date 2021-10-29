
###############################################################################################

'''This file contains general utiliy functions.'''

###############################################################################################

from pandas.core.frame import DataFrame

from database.constants import ID


def create_obj_dict(data:list, obj:object, key:str=ID, imp_dict:dict=None) -> dict:

    '''Creates a dict from the data passed. 
    Each row of the data is converted to an instance of the oject passed. 
    The instance is added to the dict with its id attribute as key.'''

    dict = {}

    if data is not None:

        #convert data to instance of object and add to dictionary with its id as key
        for index, row in enumerate(data):
            index:int
            row:list

            if imp_dict == None:
                new_entry = obj(index, row)
            else:
                new_entry = obj(index, row, imp_dict)
            dict[getattr(new_entry, ID) if key == ID else index] = new_entry

        return dict
    else:
        return None

def create_obj_list(data:list, obj:object, dict:dict) -> list:

    '''Creates a list from the data passed. 
    Each row of the data is converted to an instance of the oject passed. 
    The instance is added to the list.'''

    list = []

    #convert data to instance of object and append to list
    if data is not None:
        for row in data:
            row:list
            
            list.append(obj(row, dict))

    return list   

def fill_nan_in_df_with_zeros(df:DataFrame)-> DataFrame:

    '''Returns a DataFrame with nan replaced with 0s.'''

    df.fillna(0, inplace=True)

    return df

    
        
    
