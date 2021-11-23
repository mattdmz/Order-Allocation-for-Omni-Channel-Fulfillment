
###############################################################################################

'''This file contains the class Database.'''

###############################################################################################


from mysql.connector.errors import DatabaseError
from database.constants import CONFIG, NAME
from mysql import connector
from time import sleep


class NoDataError(Exception):
    
    def __init__(self, view_name:str):

        '''Raised when no data could be fethced.'''
        
        #construct error msgs
        self.name = NoDataError.__name__
        self.err_description = ": MySQL Error 1329: No data - zero rows fetched, selected, or processed." + "\n"
        self.low_level_err = (f"Query executed '{view_name}' in database '{CONFIG[NAME]}'." + "\n" + 
                               "Provide different parameters for query.")

        #complite error
        self.msg = self.name + self. err_description + self.low_level_err
        super().__init__(self.msg)


class Database:
    
    def __init__(self):

        '''build a connetion to the database.'''

        try:
            #try to connect to MySQL database by using the config prms defined in constants
            self.connection = connector.connect(**CONFIG)

        except connector.Error as err:
            raise ConnectionError(err)
    
    def __enter__(self):

        '''reeturns a cursor for database'''

        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, type, value, traceback):

        '''close database connection'''

        self.connection.close()

    def fetch_data(self, view:object):

        '''executes passed view'''

        try:
            #excecute query with cursor of database
            self.cursor.execute(view.sql)
            
            #fetch data from database according to query
            data = self.cursor.fetchall()

            #check if data could be fetched
            if data == []:
                #report that query did not fetch any data
                raise NoDataError(view.name)
                
            return data
        
        except NoDataError as err:
            pass #print(err)
            return None

        except connector.Error as err:
            # print error and info to its occurrence
            err = (f"MySQL {err} \n"
                    f"Error occured while runnning view '{view.name}' in database '{CONFIG[NAME]}' on trial: {trials}.") 

        except connector.DatabaseError as err:
            raise connector.DatabaseError(err)


