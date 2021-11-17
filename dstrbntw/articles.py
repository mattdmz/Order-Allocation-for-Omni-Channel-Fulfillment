

###############################################################################################

'''This file contains the class Articles and its subclass Article.'''

###############################################################################################


from datetime import date
from mysql.connector.errors import DatabaseError

from database.connector import Database, NoDataError
from database.constants import ID
from database.views import Articles_Sold_Online, Articles_Sold_Offline
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
        #self.sold_omline = data[5]
        self.start_stock_rate = float(data[6])


class Articles:

    '''Class to handle a set of articles.'''

    def __init__(self) -> None:
        pass

    @property
    def start_stock_rates(self) -> list:

        '''Returns a list of lists of start stock rates per article.'''

        return list([article.start_stock_rate] for article in self.dict.values())

    def imp(self, db:Database, start:date=None, end:date=None, region_id:int=None) -> None:

        ''' Fetches data from db about articles and stores them as article object in a dict 
            which is set as attribute of Articles with 
            the article.id as key and the article-object as value.'''

        try: 
            data_online = Articles_Sold_Online(db, columns="*", start=start, end=end, fc=region_id).data #type: list
            data_offline = Articles_Sold_Offline(db, columns="*", start=start, end=end, fc=region_id).data #type: list

            if data_offline == None and data_online == None:
                raise NoDataError(Articles_Sold_Offline.__name__ + " or " + Articles_Sold_Online.__name__)

            for line in data_online:
                if not line in data_offline:
                    data_offline.append(line)

            # map articles
            self.dict = create_obj_dict(data_offline, Article, key=ID)

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



        


