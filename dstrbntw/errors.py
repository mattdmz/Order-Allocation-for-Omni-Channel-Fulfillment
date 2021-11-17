
###############################################################################################

'''This file contains customized errors for dstrbntw.'''

###############################################################################################


from datetime import time
from mysql.connector.errors import Error

from database.constants import CONFIG, NAME

class ImportModelDataError(Exception):
    
    '''Raised when data could not be imported'''
    
    def __init__(self, import_source, dict_name=None, err_name=None, err=None):
        
        #construct error msgs
        self.name_mid_level_error = ImportModelDataError.__name__
        self.mid_level_error = f": An error occured while importing data{' for ' + dict_name if dict_name is not None else ''} from {import_source}. \n"
        self.name_low_level_error = str(err_name) + ": "
        self.low_level_err = "something went wrong" if isinstance(err.args[0], int) else err.args[0]

        #concatenate error msg
        self.msg = self.name_mid_level_error + self.mid_level_error + self.name_low_level_error + self.low_level_err
        super().__init__(self.msg)


class InitStockError(Exception):
    
    '''Raised when model could not be initialized.'''
    
    def __init__(self, err_name:str, err:Error)-> None:
        
        self.mid_level_err_name = InitStockError.__name__
        self.mid_level_error = ": Model could not be initialized with imported data. \n"
        self.low_level_err_name = err_name + ": "
        self.low_level_error = err.args[0] if isinstance(err.args[0], str) else str(err.args[0])
        self.msg = self.mid_level_err_name + self.mid_level_error + self.low_level_err_name + self.low_level_error
        super().__init__(self.msg)


class ImportTransactionsError(Exception):

    '''Raised when order data could not be imported.'''
    
    def __init__(self, table:str, start:time, end:time, err_name:str=None, err:Error=None):
        
        #construct error msgs
        self.name_mid_level_error = ImportTransactionsError.__name__
        self.mid_level_error = f": An error occured while importing {table} data between {start} and {end} from database '{CONFIG[NAME]}'. \n"
        self.name_low_level_error = str(err_name) + ": "
        self.low_level_err = str(err.args[0])

        #concatenate error msg
        self.msg = self.name_mid_level_error + self.mid_level_error + self.name_low_level_error + self.low_level_err
        super().__init__(self.msg)



