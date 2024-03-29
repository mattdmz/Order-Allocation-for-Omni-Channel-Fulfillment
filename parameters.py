

##########################################################################################################

'''This file contains all distribution network model and fulfillment parameters in alphabetical order.'''

##########################################################################################################


from datetime import date, time, timedelta
from numpy.lib.function_base import median

from database.constants import FC, ZIP_REGION
from dstrbntw.constants import A, B, C, FULFILLMENT_CENTER, PREDEFINED_LEVEL, RNDM_BTWN_REORDER_AND_TARGET_LEVEL, SMALL_STORE, REGULAR_STORE, TARGET_LEVEL 

# _________________________________________________________________________________________________________________________________________________

# Allocation

ALLOC_OPERATOR = median

# Assortment and Stock

EXP_INITIAL_STOCK = False

FIX_LEVEL = 100     # fix stock level set as starting evel and target level for the whole assortment at every nodee stock.
                    # (not every article at every node, because articles != assortment)
    
LISTING_LIMIT = {   SMALL_STORE: 0,         # {1 >= SMALL_STORE >= REGULAR_STORE}
                    REGULAR_STORE: 0,        # {SMALL_STORE >= REGULAR_STORE >= FC}
                    FULFILLMENT_CENTER: 0      # {REGULAR_STORE >= FC >= 0}
    }

# planned duration of stock calculated in addition to replenishment cycle duration (e.g. CYCLE_DURATION= 1 day + PLANED_STOCK_DURATION = 2 days  
# --> pursued stock duration = 3 days)
PLANED_STOCK_DURATION = {   A: 5,    #{int >= 1}
                            B: 7,    #{int >= 1}
                            C: 10      #{int >= 1}
}

# Determines the limit for a categorization between A and B / B and C level based on cumulated relative demand
STOCK_A_B_LIMIT = 0.3      # {STOCK_A_B_LIMIT < STOCK_B_C_LIMIT}
STOCK_B_C_LIMIT = 0.65      # {STOCK_B_C_LIMIT < = 1}

# service degree pursued for certain stock type
STOCK_BETA_SERVICE_DEGREE = { A: 0.995,    #{0 - 1}
                              B: 0.995,    #{0 - 1}
                              C: 0.995      #{0 - 1}
}

# €/unit of stock per day
STOCK_HOLDING_RATE = {  SMALL_STORE: 0.05,
                        REGULAR_STORE: 0.025,
                        FULFILLMENT_CENTER: 0.005
}

# Determines the start level of the stock
STOCK_SEED = PREDEFINED_LEVEL      # options: FIX_LEVEL, RNDM_BTWN_REORDER_AND_TARGET_LEVEL, TARGET_LEVEL, PREDEFINED_LEVEL 


# _________________________________________________________________________________________________________________________________________________

# Delivery_Vehicles:

# source E-Cargobike --> SMALL_STORE: https://www.biek.de/download.html?getfile=508  S.71
# source Spinter-Van --> REGULAR STORE: https://www.mercedes-benz.de/vans/de/sprinter/panel-van/technical-data --> 3t
# source Delivery Van --> FULFILLMENT CENTER: https://www.iveco.com/germany/neufahrzeuge/pages/iveco_daily_7_tonner.aspx#overview --> 7,5t

# km/min ( / 3.14 -> Annahme der Annähreung der echten Fahrzeit, da Entferung in Luftlinie gemessen wird)
AVG_SPEED = {   SMALL_STORE: 0.25,           # 15 km/h 
                REGULAR_STORE: 0.5,          # 30 km/h 
                FULFILLMENT_CENTER: 0.83,    # 50 km/h 
}

END_OF_TOURS = time(21, 0, 0)

# min.
LOADING_TIME_PER_ORDER = {  SMALL_STORE: 0.25,
                            REGULAR_STORE: 0.5,
                            FULFILLMENT_CENTER: 0.75
}

# min.
MAX_WORKING_TIME = {    SMALL_STORE: 240,
                        REGULAR_STORE: 360,
                        FULFILLMENT_CENTER: 480
}

# cm3
MAX_LOADING_VOLUME = {  SMALL_STORE: 1330000,
                        REGULAR_STORE: 7800000,
                        FULFILLMENT_CENTER: 35000000
}

# min
PAUSE_BTW_TOURS = { SMALL_STORE: 5,  
                    REGULAR_STORE: 10, 
                    FULFILLMENT_CENTER: 15 
}

# €/min. 
ROUTE_RATE = {  SMALL_STORE: 0.3,
                REGULAR_STORE: 0.35,
                FULFILLMENT_CENTER: 0.4
} 

# min.
SERVICE_TIME_PER_ORDER = {  SMALL_STORE: 3.5,
                            REGULAR_STORE: 4,
                            FULFILLMENT_CENTER: 4
}

# €/Tour
TOUR_RATE = {   SMALL_STORE: 40,
                REGULAR_STORE: 60,
                FULFILLMENT_CENTER: 80
}

# _________________________________________________________________________________________________________________________________________________

# Demand

# period of time used to analyse demand
DEMAND_ANALYSIS_START = date(2019, 3, 1)
DEMAND_ANALYSIS_END = date(2019, 5, 31)

# SUBTRACTS EXPECTED DEMAND OF THE DAY FOR A CERTAIN ARTICLE IN A CERTAIN REGION WHEN CHECKING IF STOCK IS AVAILABLE
SUBTRACT_EXPECTED_STOCK_DEMAND = True

# _________________________________________________________________________________________________________________________________________________

# Order Processing

# start and end of order allocation
ALLOC_START_TIME = time(5, 00, 0)
ALLOC_END_TIME = time(20, 00, 0)

# lastest time an order qualifies for same day delivery
CUT_OFF_TIME = time(17, 00, 0)

NUMBER_OF_WORKDAYS = 6

# order processing capacity in orderlines per minute
OP_CAPACITY = { SMALL_STORE: 1,   #60 orderlines/hour
                REGULAR_STORE: 1.5,    #90 orderlines/hour
                FULFILLMENT_CENTER: 40  #2500 orderlines/hour
}

# end time of order processing  = latest possible start of delivery tour
OP_END_TIME = { SMALL_STORE: time(19, 00, 0),
                REGULAR_STORE: time(19, 30, 0),
                FULFILLMENT_CENTER: time(20, 00, 0)  # -> replenishment of store must be made afterwards
}

# €/orderline
ORDER_PROCESSING_RATE = {   SMALL_STORE: 0.5,
                            REGULAR_STORE: 0.35,
                            FULFILLMENT_CENTER: 0.2
}

ORDER_PROCESSING_START = date(2019, 3, 1)
ORDER_PROCESSING_END = date(2019, 3, 2)

# _________________________________________________________________________________________________________________________________________________

# Replenishment / Supply

# max volume of 1 pallet in cm3 (120 * 60 * 180)
MAX_PAL_VOLUME = 1728000 * 0.75

# €/PAL/km
PAL_RATE = 2

# dureation of replenishment cyle in days
RPL_CYCLE_DURATION =   2 #{1 - 30}

# _________________________________________________________________________________________________________________________________________________

# VRP

# local search
PS_88_MAX_ITER_LOC_SEARCH = 40



