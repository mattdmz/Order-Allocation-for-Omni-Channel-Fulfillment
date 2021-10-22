

###############################################################################################

'''This file contains the class Articles and its subclass Article.'''

###############################################################################################


from datetime import date
from mysql.connector.errors import DatabaseError

from database.connector import Database, NoDataError
from database.constants import ID
from database.views import Articles_Sold
from dstrbntw.errors import ImportModelDataError
from utilities.general import create_obj_dict

class Article:

    def __init__(self, index:int, data:list):
        
        '''Assigns index (int) to instance and 
            assigns imported data to attributes.'''

        #index used to access this element in an array/matrix
        self.index = index        
    
        #assign impoorted values to attributes
        self.id = data[0]
        self.price = float(data[1])
        self.volume = float(data[2])
        self.weight = float(data[3])
        #self.min_order_quantity = data[4]


class Articles:

    '''Class to handle a set of articles.'''

    def __init__(self) -> None:
        pass

    def imp(self, db:Database, start:date=None, end:date=None, region_id:int=None) -> None:

        '''Fetches data from db about articles and stores them as article object in a dict 
            which is set as attribute of Articles with 
            the article.id as key and the article-object as value.'''

        try: 
            data = Articles_Sold(db, columns="*", start=start, end=end, fc=region_id).data

            if data == None:
                raise NoDataError(Articles_Sold.__name__)

            self.dict = create_obj_dict(data, Article, key=ID)

        except NoDataError as err:
            raise ImportModelDataError("database", err_name=NoDataError.__name__, err=err)
        
        except ConnectionError as err:
            raise ImportModelDataError("database", err_name=ConnectionError.__name__, err=err)
        
        except DatabaseError as err:     
            raise ImportModelDataError("database", err_name=DatabaseError.__name__, err=err)

    def __get__(self, id:int) -> Article:

        '''Returns an article from the articles.dict based on its id.'''

        return self.dict[id]

    def __getattr__(self, id:int, attr:str):

        '''Returns an article's attribute based on its id in the articles.dict.'''

        return getattr(self.dict[id], attr)

    def list(self) -> list:

        '''Returns a list of all article_indexes'''

        return list(article.index for article in self.dict.values())


        


