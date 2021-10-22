

###############################################################################################

'''This file contains all class constant in alphabetical order.'''

###############################################################################################

# ____________________________________________________________________________________________

# Attributes

ACCEPTING_ORDERS = "accepting_orders"
CUSTOMER = "customer"
INDEX = "index"
LOCATION = "location"
HOLDING_COSTS = "stock_holding_costs"
PROCESSABLE = "processabe"
PROFIT = "profit"
REPLENISHMENTS = "replenished_skus"
ROUTE_INDEX = "route_index"
VEHICLE = "vehicle"

# ___________________________________________________________________________________________

# Calculated Input/Output

AVG_DEMAND = "avg_demand"
DEMAND = "demand"
SUM_DEMAND = "sum_demand"
VAR_DEMAND = "var_demand"

# ___________________________________________________________________________________________

# Calculated Output

CURRENT_STOCK_LEVEL = "current_stock_level"
REORDER_STOCK_LEVEL = "reorder_stock_level"
TARGET_STOCK_LEVEL = "target_stock_level"

# ___________________________________________________________________________________________

# constants to use in parameters.Stock.SEED parameters

A = "a"
B = "b"
C = "c"
FIX_LEVEL = 1000
RNDM_BTWN_REORDER_AND_TARGET_LEVEL = "random_between_reorder_and_target_level"
TARGET_LEVEL = "target_level"

# ____________________________________________________________________________________________

# types of nodes in model

FULFILLMENT_CENTER = 2
REGULAR_STORE = 1
SMALL_STORE = 0
LIST_OF_NODE_TYPES = [SMALL_STORE, REGULAR_STORE, FULFILLMENT_CENTER]
FC_ID_LIMIT = 1000

# ____________________________________________________________________________________________

# Objective Funciton

ALLOCATION = "node_id"
DELIVERY_COSTS = "delivery_costs"
ORDER_PROCESSING_COSTS = "order_processing_costs"
REPLENISHMENT_COSTS = "replenishment_costs"
STOCK_HOLDING_COSTS = "stock_holding_costs"
SUPPLY_COSTS = "supply_costs"

# ____________________________________________________________________________________________

# Rates and Capacity Attributes

ORDER_PROCESSING_CAPACITY = "order_processing_capacity"
ORDER_PROCESSING_RATE = "order_processing_rate"
ROUTE_RATE = "route_rate"
STOCK_HOLDING_RATE = "stock_holding_rate"
SUPPLY_RATE  = "supply_rate"
TOUR_RATE = "tour_rate"

# ____________________________________________________________________________________________

# Sales

REGION_ID = "region_id"
PROC_TIME = "processing_datetime"
LINES = "salelines"
LINES_CLOSED = "closed_salelines"
REL_LINES_CLOSED = "relative_closed_salelines"
POTENTIAL_REVENUE = "potential_revenue"
REALIZED_REVENUE = "realized_revenue"
REL_REALIZED_REVENUE = "relative_realized_revenue"




