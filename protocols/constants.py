
###############################################################################################

'''This file contains all class constants in alphabetical order'''

###############################################################################################

from datetime import datetime


# allocation protocol file

ALLOC_ARR = "allocation"
BEST_OBJ_VALUE = "best_obj_value"
ITER = "iteration"
OBJ_VALUE = "objective_value"
REGION_ID = "region_id"
RETRY = "allocation_retried"
STRATEGY = "strategy"

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

AVG_DISTANCE = "avg_distance"
AVG_DELIVERY_DURATION = "avg_delivery_duration_per_order"
DELIVERED_ORDERS = "delivered"
DELIVERY_DURATION = "prop_delivery_duration"
DISTANCE = "tot_distance"
REPLENISHMENTS = "replenished_skus"
SAMEDAY_DELIVERY = "orders_with_sameday_delivery"
SAMEDAY_DELIVERY_RATE = "sameday_delivery_rate"

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
POTENTIAL_ONLINE_REVENUE = "potential_online_revenue"
ORDERS = "orders"
ORDER_ID = "order_id"
ORDER_PROCESSING_COSTS = "order_processing_costs"
PROFIT = "profit"
REL_ONLINE_REVENUE = "rel_realized_online_revenue"
REPLENISHMENT_COSTS = "replenishment_costs"
STOCK_HOLDING_COSTS = "stock_holding_costs"
DIMINUISHED_STOCK_VALUE = "diminuished_stock_value"
SUPPLY_COSTS = "supply_costs"

# ____________________________________________________________________________________________

# processed sales file

NUMBER_OF_LINES = "potential_salelines"
LINES_CLOSED = "closed_salelines"
OFFLINE_REVENUE = "offline_revenue"
POTENTIAL_OFFLINE_REVENUE = "potential_offline_revenue"
REGION_ID = "region_id"
REL_LINES_CLOSED = "rel_salelines_closed"
REL_OFFLINE_REVENUE = "rel_realized_offline_revenue"
SALES = "sales"
SALES_RATE = "sales_rate"


