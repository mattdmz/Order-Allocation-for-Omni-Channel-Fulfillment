
###############################################################################################

'''This script creates files with demand (sum, avg, var) between start and end
    based on orders and sales. start and end can be defined as optional parameters.'''

###############################################################################################

from datetime import date
from mysql.connector import DatabaseError
from pandas import DataFrame

from database.connector import Database
from database.constants import ARTICLE_ID, ZIP_REGION
from database.views import Quantity_Of_Articles_Sold_Online, Quantity_Of_Articles_Sold_Offline, Customer_Info
from dstrbntw.constants import DEMAND, SUM_DEMAND, VAR_DEMAND
from parameters import DEMAND_ANALYSIS_START, DEMAND_ANALYSIS_END
from utilities.expdata import write_df
from utilities.impdata import df_from_file

def demand_per_article_and_node(view:object, start:date, end:date, operator:str):

    ''' Fetches demand data ffrom database for each zip_region and article and stores it in a dataframe.'''

    try:

        #connect to db and get cursor
        with Database() as db:

            zip_regions = Customer_Info(db, column=ZIP_REGION, start=start, end=end).data

            df = DataFrame(columns=[ARTICLE_ID, zip_regions])

            for zip_region in zip_regions:
                data = view(db, columns=ARTICLE_ID, operator=operator, start=start, end=end, zip_region=zip_region[0]).data
            
                #store data
                if data is not None:
                    for row in data:
                        df.loc[row[0], zip_region] = row[1]

        return df

    except ConnectionError or DatabaseError as err:      
        
        print(err)
        return DataFrame()


def merge_demand(operator:str, df_online:DataFrame, df_offline:DataFrame):

    ''' Merges the online and offline demand dataframes based on their field indexes.
        If operator == "sum", online and offline demand are added togheter.
        if operator == "var", var demand is determined by max(online, offline). '''

    #iterate through the dataframe
    for node_id in df_online.columns:
        for article_id in df_online.index:

            try:
                if operator == "sum":
                    #add the online demand to the offline demand
                    df_offline.loc[article_id, node_id] += df_online.loc[article_id, node_id]
                else: # max
                    df_offline.loc[article_id, node_id] = max(df_online.loc[article_id, node_id], df_offline.loc[article_id, node_id])
            
            except KeyError:
                #if an article is missing in the online demand df as there was no demand for it, add a new index for the article
                df_offline.loc[article_id, node_id] = df_online.loc[article_id, node_id]

    return df_offline

def overall_demand(operator:str, table:str, df_online:DataFrame=None, df_offline:DataFrame=None, export:bool=None):

    ''' Uses demand passed or imports demand from default data input directory.
        Calles merge_demand_function.
        Results can be exported or returned by setting export = True/False. '''

    if df_online is not None and df_offline is not None:
        # use predetermined demand
        merged_demand = merge_demand(operator, df_online, df_offline)
    else:
        try:
            # import online and offline demand from default input directory
            merged_demand = merge_demand(operator, df_from_file(table + "_online", index_col=0), df_from_file(table + "_offline", index_col=0))
        except FileNotFoundError as err:
            print(err)
            exit()

    #check if result sould be exported
    if export:
        write_df(merged_demand, operator + "_" + DEMAND, header=True, index=True)
    else:
        return merged_demand

def average_demand(df_online:DataFrame=None, df_offline:DataFrame=None, start:date=None, end:date=None, export:bool=None):

    ''' Imports sum_demand file from default data input directory.
        Divides sum of demand with the number of days between start and end
        of demand analysis to get the average daily demand for each article and location
        (zip_region, fc, node).'''

    # get demand
    df = overall_demand("sum", df_online, df_offline)

    #use default dates if not specified
    if start is None:
        start = DEMAND_ANALYSIS_START
    
    if end is None:
        end = DEMAND_ANALYSIS_END

    #divide total demand by number of days in period of analysis to get average daily demand
    number_of_days = (end - start).days

    #calculate daily average demand
    sum_demand = df.to_numpy()
    daily_avg_demand = sum_demand / number_of_days
    avg_demand = DataFrame(daily_avg_demand, columns=df.columns.values, index=df.index.values)

    #check if result sould be exported
    if export:
        write_df(avg_demand, "avg_" + DEMAND, header=True, index=True)
    else:
        return avg_demand

def determine_online_and_offline_demand(operator:str, start:date=None, end:date=None, export:bool=None):

    ''' Manages queries to fetchdemand from database and exports/returns results.'''

    #use default dates if not specified
    if start is None:
        start = DEMAND_ANALYSIS_START
    
    if end is None:
        end = DEMAND_ANALYSIS_END
        
    df_online = demand_per_article_and_node(Quantity_Of_Articles_Sold_Online, start, end, operator)
    df_offline = demand_per_article_and_node(Quantity_Of_Articles_Sold_Offline, start, end, operator)

    if export:
        write_df(df_online, operator + "_" + DEMAND + "_online", header=True, index=True)
        write_df(df_offline, operator + "_" + DEMAND + "_offline", header=True, index=True)
    else:
        return df_online, df_offline

if __name__ == "__main__":

    # determine_online_and_offline_demand("sum", export=True)
    # determine_online_and_offline_demand("variance", export=True)

    # overall_demand("sum", SUM_DEMAND, export=True)
    overall_demand("var", VAR_DEMAND, export=True)

    # average_demand("avg", export=True)