
###############################################################################################

'''This file contains all class constants in alphabetical order'''

###############################################################################################

from datetime import datetime


# allocation protocol file

ALLOC_ARR = "allocation"
ITER = "iteration"
OBJ_VALUE = "objective_value"
PUNCTUALITY = "punctuality"
REGION_ID = "region_id"

# ____________________________________________________________________________________________

# file names

RUN_ID =  datetime.now().strftime("%Y%m%d_%H%M%S")

ALLOCATIONS_PROTOCOL_FILE_NAME = RUN_ID + "_allocations_protocol"
DAILY_RESULTS_FILE_NAME = RUN_ID + "_daily_results"
OVERALL_RESULTS_FILE_NAME = RUN_ID + "_overall_results"
ORDERS_EVALUATION_FILE_NAME = RUN_ID + "_order_evaluation"
PARAMETERS_FILE_NAME = RUN_ID + "_parameters"
SALES_EVALUATION_FILE_NAME = RUN_ID + "_sales_evaluation"

# ____________________________________________________________________________________________

# overall results

RESULTS = "results"
DISTANCE = "distance"
REPLENISHMENTS = "replenished_skus"

# ____________________________________________________________________________________________

# processed orders and results file

ALLOCATION_DATETIME = "allocation_datetime"
ARRIVAL_DATETIME = "arrival_datetime"
PROC_DATETIME = "processing_datetime"
ALLOCATED_NODE_ID = "allocated_node_id"
DELIVERY_COSTS = "delivery_costs"
MATERIAL_COSTS = "material_costs"
ONLINE_REVENUE = "online_revenue"
NUMBER_OF_ORDERS = "rechieved_orders"
NUMBER_OF_PROCESSED_ORDERS = "processed_orders"
POTENTIAL_ONLINE_REVENUE = "potential_online_revenue"
PROCESSING_RATE = "processing_rate"
ORDERS = "orders"
ORDER_ID = "order_id"
ORDER_PROCESSING_COSTS = "order_processing_costs"
PROFIT = "profit"
REL_ONLINE_REVENUE = "rel_realized_offline_revenue"
REPLENISHMENT_COSTS = "replenishment_costs"
STOCK_HOLDING_COSTS = "stock_holding_costs"
SUPPLY_COSTS = "supply_costs"

# ____________________________________________________________________________________________

# processed sales file

NUMBER_OF_LINES = "potential_salelines"
LINES_CLOSED = "closed_salelines"
OFFLINE_REVENUE = "offline_revenue"
POTENTIAL_OFFLINE_REVENUE = "potential_offline_revenue"
REGION_ID = "region_id"
REL_OFFLINE_REVENUE = "rel_realized_offline_revenue"
SALES = "sales"
SALES_RATE = "sales_rate"


