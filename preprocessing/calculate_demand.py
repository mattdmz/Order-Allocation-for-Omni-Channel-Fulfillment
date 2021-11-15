
###############################################################################################

'''This script creates files with demand (sum, avg, var) between start and end
    based on orders and sales. start and end can be defined as optional parameters.'''

###############################################################################################

from datetime import date
from mysql.connector import DatabaseError
from numpy import double
from pandas import DataFrame

from database.connector import Database
from database.constants import ARTICLE_ID, FC
from database.views import Quantity_Of_Articles_Sold_Online, Quantity_Of_Articles_Sold_Offline, Customer_Info
from dstrbntw.constants import DEMAND, AVG_DEMAND
from dstrbntw.nodes import Nodes, Node
from parameters import DEMAND_ANALYSIS_START, DEMAND_ANALYSIS_END
from utilities.expdata import write_df

def demand_per_article_and_node(operator:str, start:date=DEMAND_ANALYSIS_START, end:date=DEMAND_ANALYSIS_END, export:bool=None):

    ''' Fetches demand data from database for each zip_region and article and stores it in a dataframe.'''

    try:

        # connect to db and get cursor
        with Database() as db:

            # import region id's and nodes
            region_ids = [region_id[0] for region_id in Customer_Info(db, column=FC, start=start, end=end).data]
            nodes = Nodes()
            nodes.imp(db)

            # init DataFrame to store demand data in
            df = DataFrame()

            for region_id in region_ids:
                region_id:int

                # import regional demand data
                online_article_demand = Quantity_Of_Articles_Sold_Online(db, columns=ARTICLE_ID, operator=operator, start=start, end=end, fc=region_id).data
                
                # import regions's nodes
                regional_nodes = [node for node in nodes.dict.values() if node.fc == region_id]

                for node in regional_nodes:
                    node:Node

                    # add new column for node
                    df[node.id] = float(0)

                    # store online demand data at all nodes
                    if online_article_demand is not None:
                        for row in online_article_demand:

                            # extract data
                            article_id = row[0]
                            regional_demand = row[1]
                            try:
                                if operator == "sum":
                                    df.loc[article_id, node.id] += float(regional_demand)

                                else: # "var" -> use max btw. offline and online
                                    df.loc[article_id, node.id] = max(df.loc[article_id, node.id], float(regional_demand))
                            except KeyError:
                                df.loc[article_id, node.id] = float(regional_demand)
                    
                    # import offline demand data
                    offline_article_demand = Quantity_Of_Articles_Sold_Offline(db, columns=ARTICLE_ID, operator=operator, start=start, end=end, node_id=node.id).data

                    # store online demand data at all nodes
                    if offline_article_demand is not None:
                        for row in offline_article_demand:

                            # extract data
                            article_id = row[0]
                            node_demand = row[1]
                            try:
                                if operator == "sum":
                                    df.loc[article_id, node.id] += float(node_demand)

                                else: # "var" -> use max btw. offline and online
                                    df.loc[article_id, node.id] = max(df.loc[article_id, node.id], float(node_demand))
                            except KeyError:
                                df.loc[article_id, node.id] = float(node_demand)
        
        if export:                       
            write_df(df, operator + "_" + DEMAND + "_2", header=True, index=True)
        
        return df

    except ConnectionError or DatabaseError as err:      
        
        print(err)
        return DataFrame()

def average_demand(df:DataFrame, start:date=DEMAND_ANALYSIS_START, end:date=DEMAND_ANALYSIS_END, export:bool=None):

    ''' Imports sum_demand file from default data input directory.
        Divides sum of demand with the number of days between start and end
        of demand analysis to get the average daily demand for each article and location
        (zip_region, fc, node).'''

    # divide total demand by number of days in period of analysis to get average daily demand
    number_of_days = (end - start).days

    # calculate daily average demand
    sum_demand = df.to_numpy()
    daily_avg_demand = sum_demand / number_of_days
    avg_demand = DataFrame(daily_avg_demand, columns=df.columns.values, index=df.index.values)

    # check if result sould be exported
    if export:
        write_df(avg_demand, AVG_DEMAND, header=True, index=True)
    
    return avg_demand

def main():

    '''Calculates sum, avg and variance demand between start end end period.'''

    sum_demand = demand_per_article_and_node("sum", export=True)
    average_demand(sum_demand, export=True)
    demand_per_article_and_node("variance", export=True)

if __name__ == "__main__":

    main()




    