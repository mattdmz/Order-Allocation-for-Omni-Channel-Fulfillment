
###############################################################################################

'''This file contains all class constants in alphabetical order'''

###############################################################################################

# ____________________________________________________________________________________________

# Columns

ARTICLE_ID = "article_id"
CUSTOMER_ID = "customer_id"
DATE = "its_date"
DATETIME = "its_datetime"
DATE_TIME = "date_time"
FC = "fc"
ID = "id"
LATITUDE = "latitude"
LONGITUDE = "longitude"
NODE_ID = "node_id"
NODE_TYPE = "node_type"
PRICE = "price"
QUANTITY = "quantity"
SUPPLY_DISTANCE = "supply_distance"
TIME = "its_time"
TOUR = "tour"
TRSACT_ID = "transaction_id"
VOLUME = "volume"
ZIP_REGION = "zip_region"

# ____________________________________________________________________________________________

#Database Tables

ARTICLES = "articles"
CUSTOMERS = "customers"
FCS = "fulfillment_centers"
NODES = "nodes"
ORDERS = "orders"
ORDERLINES = "orderlines"
REGIONS = "regions"
SALES = "sales"
SALELINES = "salelines"
STORES = "stores"

# ____________________________________________________________________________________________

#configuration

USER = "user"
NAME = "database"
WARNINGS = "raise_on_warnings"
HOST = "host"
PSW = "password"

CONFIG = {  USER: "root",
            PSW: "Masterarbeit",
            HOST: "localhost", #"127.0.0.1",
            NAME: "masterarbeit",
            WARNINGS: True           
}