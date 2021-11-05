
from mysql.connector.errors import DatabaseError

from database.connector import Database
from database.views import *

def test(view_to_test:object) -> None:
    
    ''' Function to test a view with predefined parameters.
        Returns the first 5 results fetched or an error. '''

    # example parameters for testing
    start = "2019-03-01"
    end = "2019-03-02"
    day = "2019-03-01"
    start_time = "00:00:00"
    end_time = "05:00:00"
    start_datetime = start + " " + start_time
    end_datetime = end + " " + end_time
    fc = 1001
    zip_region = 10
    node_id = 3
    article_id = 1690
    order_id = 790660
    columns="*"
    operator = "sum"

    try:

        #connect to db and get cursor
        with Database() as db:
            
            if view_to_test == All_Objects:
                data = All_Objects(db, columns, NODES).data
            
            elif view_to_test == Transactions_in_Period:
                data = Transactions_in_Period(db, ORDERS, start=start_datetime, end=end_datetime, fc=fc).data
            
            elif view_to_test == Transactions_on_Day:
                data = Transactions_on_Day(db, ORDERS, day=day, start_time=start_time, end_time=end_time, fc=fc).data               
            
            elif view_to_test == Lines_of_Transaction:
                data = Lines_of_Transaction(db, columns=columns, table=ORDERLINES, id=order_id).data

            elif view_to_test == Orders_in_Zip_Region:
                data = Orders_in_Zip_Region(db, columns=columns, start=start, end=end, zip_region=zip_region)
            
            elif view_to_test == Articles_Sold:
                data = Articles_Sold(db, columns=columns, start=start, end=end, fc=fc).data
            
            elif view_to_test == Articles_Sold_Online:
                data = Articles_Sold_Online(db, columns=columns, start=start, end=end).data
            
            elif view_to_test == Quantity_Of_Articles_Sold_Online:
                data = Quantity_Of_Articles_Sold_Online(db, operator=operator, columns=ARTICLE_ID, article_id=article_id, start=start, end=end, fc=fc).data
            
            elif view_to_test == Quantity_Of_Articles_Sold_Offline:
                data = Quantity_Of_Articles_Sold_Offline(db, columns=ARTICLE_ID, start=start, end=end, node_id=node_id).data
            
            elif view_to_test == Customers_Buying_Online:
                data = Customers_Buying_Online(db, columns, end=end, zip_region=zip_region).data
            
            elif view_to_test == Specific_Nodes:
                data = Specific_Nodes(db, columns, type=1, region_column=FC, region=fc).data

            #test print
            if data is not None:
                for row in range (0, (5 if len(data) > 5 else len(data))):
                    print(data[row])
    
    except SyntaxError as err:
        print(SyntaxError.__name__, err.args[0])

    except ConnectionError as err:
        print(ConnectionError.__name__, err.args[0])
        
    except DatabaseError as err:     
        print(DatabaseError.__name__, err.args[0])

    except TypeError as err:
        print(TypeError.__name__, err.args[0])


if __name__ == "__main__":

    test(Transactions_in_Period)
