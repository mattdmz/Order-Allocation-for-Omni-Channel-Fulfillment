
###############################################################################################

'''This file contains Database Views and Database Functions.'''

###############################################################################################

from datetime import date, datetime, time
from typing import Union

from database.connector import Database
from database.constants import *


class Join:

    def customers(joiner:int=None):

        '''Joins the table customers.'''

        if joiner is not None:
            return f", {CUSTOMERS} as {CUSTOMERS[0]} "
        else:
            return " "

    def nodes(joiner:int=None):

        '''Joins the table nodes.'''

        if joiner is not None:
            return f", {NODES} as {NODES[0]} "
        else:
            return " "

    def orders(start:date=None, end:date=None, fc=None):

        if start is not None or end is not None or fc is not None:
            return f", {ORDERS} as {ORDERS[0]} "
        else:
            return " "

class Conditions:

    '''Joining conditions.'''

    def date_time(date_or_time:str, table_abbr:str, start:Union[date, time]=None, end:Union[date, time]=None):

        '''Builds a date/time condition for MySQL queries. returns "" if neither start nor end was provided.'''

        if start is not None and end is not None:
            return  f"{table_abbr}.{date_or_time} BETWEEN '{start}' AND '{end}' "
        elif start is not None and end is None:
            return f"{table_abbr}.{date_or_time} >= '{start}' "
        elif start is None and end is not None:
            return f"{table_abbr}.{date_or_time} <= '{end}' "
        else:
            return ""

    def date_time_cast(table_abbr:str, start:datetime=None, end:datetime=None):

        '''Builds a date/time condition for MySQL queries. returns "" if neither start nor end was provided.'''

        if start is not None and end is not None:
            return f"cast({table_abbr}.{DATE} as datetime) + cast({table_abbr}.{TIME} as time) BETWEEN cast('{start}' as datetime) AND cast('{end}' as datetime)  "
        elif start is not None and end is None:
            return f"cast({table_abbr}.{DATE} as datetime) + cast({table_abbr}.{TIME} as time) >= cast('{start}' as datetime) "
        elif start is None and end is not None:
            return f"cast({table_abbr}.{DATE} as datetime) + cast({table_abbr}.{TIME} as time) =< cast('{end}' as datetime) "
        else:
            return ""

    def join_ids(join, main_table_abbr:str, primary_id:int, joined_table_abbr:str, foreign_id:int):

        '''Builds an addition join conditions for two tables based on their ids.'''

        if join is not None:

            return f"AND {main_table_abbr}.{primary_id} = {joined_table_abbr}.{foreign_id} "
        else:
            return ""

    def specific_value(table_abbr:str, column:str=None, value=None):

        '''Builds a comparison condition based on a certain value for MySQL queries.'''

        if value is not None:
            return  f"AND {table_abbr}.{column} = {value} "
        else:
            return ""


class All_Objects():

    ''' View returning all columns or only specified columns of a table.'''

    def __init__(self, db:Database,  table:str, columns:str=None):

        self.name = All_Objects.__name__
        self.sql = (f"SELECT {columns if columns is not None else '*'} "
                    f"FROM {table} "         
                    f"ORDER BY {table}.{TRSACT_ID if table == ORDERLINES or table == SALELINES else  ID} ASC;")

        #fetch data
        self.data = db.fetch_data(self)


class Value_Matching():

    ''' View returning a specific column from a specific table.'''

    def __init__(self, db:Database,  table:str, specific_column:str, specific_value, columns:str=None):

        self.name = Value_Matching.__name__
        self.sql = (f"SELECT {columns if columns is not None else '*'} "
                    f"FROM {table} as x "
                    f"WHERE x.{specific_column} = x.{specific_value} "
                    f"ORDER BY x.{specific_column} ASC;")

        #fetch data
        self.data = db.fetch_data(self)


class Transactions_in_Period():

    ''' View returning transactions from a table.
        Drill downs:
        - between start datetime and end datetime.'''

    def __init__(self, db:Database,  table:str, columns:str=None, start:datetime=None, end:datetime=None, fc:int=None):

        #extract

        self.name = Transactions_in_Period.__name__
        self.sql = (f"SELECT {table[0]}.{columns if columns is not None else '*'} "
                    f"FROM {table} as {table[0]} {Join.customers(fc) if table == ORDERS else Join.nodes(fc)}"
                    f"WHERE {f'{Conditions.date_time(DATETIME, table[0], start=start, end=end)}' if start is not None or end is not None else ''} "
                    f"{'AND ' if (start is not None or end is not None) and fc is not None else ''}"
                    f"{f'{CUSTOMERS[0] if table == ORDERS else NODES[0]}.{ID} = {table[0]}.{CUSTOMER_ID if table == ORDERS else NODE_ID} ' if fc is not None else ''}"
                    f"{'AND ' if fc is not None else ''}" 
                    f"{f'{CUSTOMERS[0] if table == ORDERS else NODES[0]}.{FC} = {fc} ' if fc is not None else ''}" 
                    f"ORDER BY {table[0]}.{ID} ASC;")

        #fetch data
        self.data = db.fetch_data(self)


class Transactions_on_Day():

    ''' View returning transactions from a table.
        Drill downs:
        - between start and/or time
        - for a specific FC-region. '''

    def __init__(self, db:Database,  table:str, day:date, columns:str=None, start_time:time=None, end_time:time=None, fc:int=None):

        #extract

        self.name = Transactions_in_Period.__name__
        self.sql = (f"SELECT {table[0]}.{columns if columns is not None else '*'} "
                    f"FROM {table} as {table[0]}{Join.customers(fc) if table == ORDERS else Join.nodes(fc)} "
                    f"WHERE {table[0]}.{DATE} = '{day}' {'AND ' if start_time is not None or end_time is not None else ''}"
                    f"{Conditions.date_time(TIME, table[0], start=start_time, end=end_time) if start_time is not None or end_time is not None else ''} "
                    f"{'AND ' if (start_time is not None or end_time is not None) and fc is not None else ''}"
                    f"{f'{CUSTOMERS[0] if table == ORDERS else NODES[0]}.{ID} = {table[0]}.{CUSTOMER_ID if table == ORDERS else NODE_ID} ' if fc is not None else ''}"
                    f"{'AND ' if fc is not None else ''}" 
                    f"{f'{CUSTOMERS[0] if table == ORDERS else NODES[0]}.{FC} = {fc} ' if fc is not None else ''}" 
                    f"ORDER BY {table[0]}.{ID} ASC;")

        #fetch data
        self.data = db.fetch_data(self)


class Lines_of_Transaction():

    ''' View returning all lines of a transactnion (order, sale).'''

    def __init__(self, db:Database, table:str, id:int, columns:str=None):

        self.name = Lines_of_Transaction.__name__
        self.sql = (f"SELECT {columns if columns is not None else '*'} "
                    f"FROM {table} "         
                    f"WHERE {table}.{TRSACT_ID} = {id} "
                    f"ORDER BY {table}.{TRSACT_ID} ASC;")

        #fetch data
        self.data = db.fetch_data(self)


class Orders_in_Zip_Region():

    ''' View returning all orders recieved.
        Drill downs:
        - within a zip region 
        - between start and/or ende_date.'''

    def __init__(self, db:Database,  columns:str=None, start:date=None, end:date=None, zip_region:int=None):

        self.name = Orders_in_Zip_Region.__name__
        self.sql = (f"SELECT {columns if columns is not None else '*'} "
                    f"FROM {ORDERS} as o "
                    f"WHERE o.{CUSTOMER_ID} IN ("
                                                            f"SELECT {CUSTOMER_ID} " 
                                                            f"FROM {ORDERS} as o, {CUSTOMERS} as c "
                                                            f"WHERE o.{CUSTOMER_ID} = c.{ID} "
                                                                    f"{'AND ' if start is not None or end is not None else ''}"
                                                                    f"{Conditions.date_time(DATE, 'o', start, end)} "
                                                                    f"{Conditions.specific_value('c', ZIP_REGION, zip_region)} "
                                                            f"ORDER BY o.{ID} ASC);")

        #fetch data
        self.data = db.fetch_data(self)


class Articles_Sold():

    ''' View returning all articles sold online and offline.
        Drill Downs:
        - between start and/or ende_date.'''

    def __init__(self, db:Database, columns:str=None, start:date=None, end:date=None, fc:int=None):

        self.name = Articles_Sold.__name__
        self.sql = (f"SELECT {columns if columns is not None else '*'} "
                    f"FROM {ARTICLES} as a "        
                    f"WHERE a.{ID} IN ("
                                                f"SELECT ol.{ARTICLE_ID} " 
                                                f"FROM {ORDERS} as o, {ORDERLINES} as ol{Join.customers(fc)} "
                                                f"WHERE o.{ID} = ol.{TRSACT_ID} "
                                                        f"{'AND ' if start is not None or end is not None else ''}"
                                                        f"{Conditions.date_time(DATE, 'o', start, end)} "
                                                        f"{Conditions.join_ids(fc, 'c', ID, 'o', CUSTOMER_ID)}"
                                                        f"{Conditions.specific_value('c', FC, fc)}"
                                                f"GROUP BY ol.{ARTICLE_ID}) "
                    f"OR a.{ID} IN ("
                                                f"SELECT sl.{ARTICLE_ID} " 
                                                f"FROM {SALES} as s, {SALELINES} as sl{Join.nodes(fc)} "
                                                f"WHERE s.{ID} = sl.{TRSACT_ID} "
                                                        f"{'AND ' if start is not None or end is not None else ''}"
                                                        f"{Conditions.date_time(DATE, 's', start, end)} "
                                                        f"{Conditions.join_ids(fc, 'n', ID, 's', NODE_ID)}"
                                                        f"{Conditions.specific_value('n', FC, fc)}"
                                                f"GROUP BY sl.{ARTICLE_ID}) "
                    f"ORDER BY a.{ID} ASC;")

        #fetch data 
        self.data = db.fetch_data(self)


class Articles_Sold_Online():

    ''' View returning all articles sold online.
        Drill downs:
        - between start and/or ende_date.'''

    def __init__(self, db:Database, columns:str=None, start:date=None, end:date=None):

        self.name = Articles_Sold_Online.__name__
        self.sql = (f"SELECT {columns if columns is not None else '*'} "
                    f"FROM {ARTICLES} as a "         
                    f"WHERE a.{ID} IN ("
                                                f"SELECT ol.{ARTICLE_ID} " 
                                                f"FROM {ORDERS} as o, {ORDERLINES} as ol "
                                                f"WHERE o.{ID} = ol.{TRSACT_ID} "
                                                        f"{'AND ' if start is not None or end is not None else ''}"
                                                        f"{Conditions.date_time(DATE, 'o', start, end)} "
                                                f"GROUP BY ol.{ARTICLE_ID} "
                    f"ORDER BY a.{ID} ASC);")

        #fetch data 
        self.data = db.fetch_data(self)


class Quantity_Of_Articles_Sold_Online():

    ''' View returning the quantity (operator) sold online of articles.
        Drill downs:
        - specific article_id 
        - between start and/or ende_date
        - in a specific zip_region
        - in a specific fc region.'''

    def __init__(self,  db:Database, operator:str, avg:bool=None, columns:str=None, article_id:int=None, start:date=None, end:date=None, zip_region:int=None, fc:int=None):

        self.name = Quantity_Of_Articles_Sold_Online.__name__
        self.sql = (f"SELECT {'ol.' + columns + ', ' if columns is not None else ''} "
                    f"{operator + '(ol.'+ QUANTITY + ')'}{'/' + str((end-start).days) + ' ' if avg else ''} as {'avg' if avg else operator} "
                    f"FROM {ORDERS} as o, {ORDERLINES} as ol{Join.customers((zip_region, fc))} "
                    f"WHERE o.{ID} = ol.{TRSACT_ID} "
                            f"{Conditions.specific_value('ol', ARTICLE_ID, article_id)}"
                            f"{Conditions.join_ids((zip_region, fc), 'c', ID, 'o', CUSTOMER_ID)}"
                            f"{'AND ' if start is not None or end is not None else ''}"
                            f"{Conditions.date_time(DATE, 'o', start, end)}"
                            f"{Conditions.specific_value('c', ZIP_REGION, zip_region)}"
                            f"{Conditions.specific_value('c', FC, fc)}"
                    f"GROUP BY ol.{ARTICLE_ID} "
                    f"ORDER BY ol.{ARTICLE_ID} ASC;")

        #fetch data
        self.data = db.fetch_data(self)


class Quantity_Of_Articles_Sold_Offline():

    ''' View returning the quantity (operator) sold offline of articles.
        Drill downs:
        - specific article_id 
        - between start and/or ende_date
        - in a specific node
        - in a specific zip_region
        - in a specific fc region.'''

    def __init__(self, db:Database, operator:str, avg:bool=None, columns:str=None, article_id:int=None, start:date=None, end:date=None, node_id:id=None, zip_region:int=None, fc:int=None):

        self.name = Quantity_Of_Articles_Sold_Offline.__name__
        self.sql = (f"SELECT{' sl.' + columns + ', ' if columns is not None else ''} "
                    f"{operator + '(sl.'+ QUANTITY + ')'}{'/' + str((end-start).days) + ' ' if avg else ''} as {'avg' if avg else operator} "
                    f"FROM {SALES} as s, {SALELINES} as sl{Join.nodes(node_id or zip_region or fc)}"
                    f"WHERE s.{ID} = sl.{TRSACT_ID} "
                            f"{Conditions.specific_value('sl', ARTICLE_ID, article_id)}"
                            f"{Conditions.join_ids((node_id or zip_region or fc), 'n', ID, 's', NODE_ID)}"
                            f"{'AND ' if start is not None or end is not None else ''}"
                            f"{Conditions.date_time(DATE, 's', start, end)}"
                            f"{Conditions.specific_value('n', ID, node_id)}"
                            f"{Conditions.specific_value('n', ZIP_REGION, zip_region)}"
                            f"{Conditions.specific_value('n', FC, fc)}"
                    f"GROUP BY sl.{ARTICLE_ID} "
                    f"ORDER BY sl.{ARTICLE_ID} ASC;")
        
        #fetch data
        self.data = db.fetch_data(self)


class Customers_Buying_Online():

    ''' View returning all online customers.
        Drill downs:
        - between start and/or ende_date
        - in a specific fc region.'''

    def __init__(self, db:Database, columns:str=None, start:date=None, end:date=None, fc:int=None):

        self.name = Customers_Buying_Online.__name__
        self.sql = (f"SELECT {columns if columns is not None else '*'} "
                    f"FROM {CUSTOMERS} as c{Join.orders(start=start, end=end, fc=fc)}"   
                    f"{'WHERE ' if start is not None or start is not None else ''}"    
                        f"{f'c.{ID} = o.{CUSTOMER_ID}' if start is not None or end is not None or fc is not None else ''} "    
                        f"{'AND ' if start is not None or end is not None or fc is not None else ''}"
                        f"{Conditions.date_time(DATE, 'o', start, end)} "
                        f"{Conditions.specific_value('c', FC, fc)} "
                    f"GROUP BY c.{ID} "
                    f"ORDER BY c.{ID} ASC;")

        #fetch data
        self.data = db.fetch_data(self)


class Customer_Info():

    ''' View returning a special column from online customers.
        Drill downs:
        - between start and/or ende_date'''

    def __init__(self, db:Database, column:str=None, start:date=None, end:date=None):

        self.name = Customer_Info.__name__
        self.sql = (f"SELECT c.{column} "
                    f"FROM {CUSTOMERS} as c{Join.orders(start=start, end=end)}"   
                    f"{'WHERE ' if start is not None or start is not None else ''}"    
                        f"{f'c.{ID} = o.{CUSTOMER_ID}' if start is not None or end is not None else ''} "    
                        f"{'AND ' if start is not None or end is not None else ''}"
                        f"{Conditions.date_time(DATE, 'o', start, end)} "
                    f"GROUP BY c.{column} "
                    f"ORDER BY c.{column} ASC;")

        #fetch data
        self.data = db.fetch_data(self)


class Specific_Nodes():

    ''' View retuning nodes.
        Drill downs:
        - between start and/or ende_date
        - in a specific region_column (zip_region, fc).'''

    def __init__(self, db:Database, columns:str=None, node_type:int=None, region_column:str=None, region:int=None):

        self.name = Specific_Nodes.__name__
        self.sql = (f"SELECT {columns if columns is not None else '*'} "
                    f"FROM {NODES} as n "
                    f"{'WHERE ' if region is not None or node_type is not None else ''}"         
                            f"{f'n.{region_column} = {region}' if region is not None else ''} "
                            f"{'AND ' if region is not None and node_type is not None else ''}"
                            f"{f'n.{NODE_TYPE} = {node_type} ' if node_type is not None else ''}"
                    f"ORDER BY n.{ID} ASC;")

        #fetch data
        self.data = db.fetch_data(self)
