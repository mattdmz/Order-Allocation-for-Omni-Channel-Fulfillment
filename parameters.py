

##########################################################################################################

'''This file contains all distribution network model and fulfillment parameters in alphabetical order.'''

##########################################################################################################


from datetime import date, time, timedelta

from dstrbntw.constants import A, B, C, SMALL_STORE, REGULAR_STORE, FULFILLMENT_CENTER, FIX_LEVEL, RNDM_BTWN_REORDER_AND_TARGET_LEVEL, TARGET_LEVEL 


# _________________________________________________________________________________________________________________________________________________

# Allocation

# period of time in which transactions (orders, sales) are collected and allocated/fulfilled
ALLOC_PERIOD = timedelta(hours=4, minutes=0, seconds=0)
ALLOC_REGIONS = [1005] #None                                  #Filter of regions to allocated orders in

MIN_ORDERS_TO_PROCESS = 0 #min = 0

# period of time used to execute orders
ORDER_PROCESSING_START = date(2019,3,1)
ORDER_PROCESSING_END = date(2019,3,2)

# _________________________________________________________________________________________________________________________________________________

# Assortment
    
LISTING_LIMIT = {   SMALL_STORE: 0.75,         # {1 >= SMALL_STORE >= REGULAR_STORE}
                    REGULAR_STORE: 0.3,        # {SMALL_STORE >= REGULAR_STORE >= FC}
                    FULFILLMENT_CENTER: 0      # {REGULAR_STORE >= FC >= 0}
    }

# Determines the start level of the stock
STOCK_SEED = FIX_LEVEL      # options: FIX_LEVEL, RNDM_BTWN_REORDER_AND_TARGET_LEVEL, TARGET_LEVEL 

# Determines the limit for a categorization between A and B / B and C level based on cumulated relative demand
STOCK_A_B_LIMIT = 0.3      # {STOCK_A_B_LIMIT < STOCK_B_C_LIMIT}
STOCK_B_C_LIMIT = 0.65      # {STOCK_B_C_LIMIT < = 1}


# €/unit of stock per day
STOCK_HOLDING_RATE = {  SMALL_STORE: 0.025,
                        REGULAR_STORE: 0.01,
                        FULFILLMENT_CENTER: 0.005
}

# €/orderline
ORDER_PROCESSING_RATE = {   SMALL_STORE: 0.25,
                            REGULAR_STORE: 0.2,
                            FULFILLMENT_CENTER: 0.05
}

# €/min. 
ROUTE_RATE = {  SMALL_STORE: 0.75,
                REGULAR_STORE: 0.3,
                FULFILLMENT_CENTER: 0.25
} 

# €/Tour
TOUR_RATE = {   SMALL_STORE: 10,
                REGULAR_STORE: 10,
                FULFILLMENT_CENTER: 10
}

# €/PAL/km
PAL_RATE = 2

# _________________________________________________________________________________________________________________________________________________

# Capacitites

SUBTRACT_EXPECTED_STOCK_DEMAND = True

# _________________________________________________________________________________________________________________________________________________

# Delivery_Vehicles:

# source E-Cargobike --> SMALL_STORE: https://www.biek.de/download.html?getfile=508  S.71
# source Spinter-Van --> REGULAR STORE: https://www.mercedes-benz.de/vans/de/sprinter/panel-van/technical-data --> 3t
# source Delivery Van --> FULFILLMENT CENTER: https://www.iveco.com/germany/neufahrzeuge/pages/iveco_daily_7_tonner.aspx#overview --> 7,5t

# km/min
AVG_SPEED = {   SMALL_STORE: 0.1,  #6 km/h 
                REGULAR_STORE: 0.5, #30 km/h 
                FULFILLMENT_CENTER: 0.83 #50 km/h 
}

END_OF_TOURS = time(20, 0, 0)

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

# min.
SERVICE_TIME_PER_ORDER = {  SMALL_STORE: 3.5,
                            REGULAR_STORE: 4,
                            FULFILLMENT_CENTER: 4
}

# _________________________________________________________________________________________________________________________________________________

# Demand

# period of time used to analyse demand
DEMAND_ANALYSIS_START = date(2019, 3, 1)
DEMAND_ANALYSIS_END = date(2019, 5, 31)

# _________________________________________________________________________________________________________________________________________________

# Order Processing


# end of order processing
CUT_OFF_TIME = time(17, 30, 0)

# order processing capacity in orderlines per minute
OP_END = { SMALL_STORE: time(18, 00, 0),
           REGULAR_STORE: time(19, 00, 0),
           FULFILLMENT_CENTER: time(21, 00, 0)
}

# order processing capacity in orderlines per minute
OP_CAPACITY = { SMALL_STORE: 0.83,   #50 orderlines/hour
                REGULAR_STORE: 1.5,    #100 orderlines/hour
                FULFILLMENT_CENTER: 41  #2500 orderlines/hour
}

# _________________________________________________________________________________________________________________________________________________

# Replenishment

# max volume of 1 pallet in cm3
MAX_PAL_VOLUME = 1728000

# service degree pursued for certain stock type
STOCK_BETA_SERVICE_DEGREE = { A: 0.995,    #{0 - 1}
                              B: 0.99,    #{0 - 1}
                              C: 0.97      #{0 - 1}
}
# dureation of replenishment cyle in days
RPL_CYCLE_DURATION =   3 #{1 - 30}

# planned duration of stock calculated in addition to replenishment cycle duration (e.g. CYCLE_DURATION= 1 day + PLANED_STOCK_DURATION = 2 days  
# --> pursued stock duration = 3 days)
PLANED_STOCK_DURATION = {   A: 3,    #{int >= 1}
                            B: 5,    #{int >= 1}
                            C: 10      #{int >= 1}
}

# request of stock replenishment at lower distribution level
REPLENISHMENT_TIME = time(22, 0, 0)

# _________________________________________________________________________________________________________________________________________________

# VRP

# local search
PS_88_MAX_ITER_LOC_SEARCH = 40



