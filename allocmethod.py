
###############################################################################################

''' This file contains the allocation method that should be used.
    Please assign it to the parameter ALLOC_METHOD and modify the
    imprt statement accordingly. '''

###############################################################################################

from allocation.rules import Nearest_Nodes, Nearest_Already_Allocated_Nodes, Smallest_Demand_Variance, Smallest_Stock_Duration, Dynamic_1
from allocation.constants import MIN, MAX, MEDIAN

ALLOC_METHOD = Nearest_Nodes                # choose from allocator.rules
ALLOC_OPERATOR = MIN                        # choose from allocator.constants