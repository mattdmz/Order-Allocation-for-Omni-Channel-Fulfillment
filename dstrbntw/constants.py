

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
PIECES = "pieces"
PROCESSABLE = "processable"

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
RNDM_BTWN_REORDER_AND_TARGET_LEVEL = "random_between_reorder_and_target_level"
TARGET_LEVEL = "target_level"
PREDEFINED_LEVEL = "predefined_level"

# ____________________________________________________________________________________________

# types of nodes in model

FULFILLMENT_CENTER = 2
REGULAR_STORE = 1
SMALL_STORE = 0
LIST_OF_NODE_TYPES = [SMALL_STORE, REGULAR_STORE, FULFILLMENT_CENTER]
FC_ID_LIMIT = 1000





