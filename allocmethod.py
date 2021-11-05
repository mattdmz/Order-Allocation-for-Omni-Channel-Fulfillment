
###############################################################################################

''' This file contains the allocation method that should be used.
    Please assign it to the parameter ALLOC_METHOD and modify the
    imprt statement accordingly. '''

###############################################################################################

from allocation.rules import Nearest_Nodes, Nearest_Already_Allocated_Nodes, Allocation_Of_Nearest_Order, Longest_Stock_Duration, Dynamic_1
from allocation.constants import MIN, MAX, MEDIAN

# choose from allocator.rules
ALLOC_METHOD = Nearest_Already_Allocated_Nodes

# choose from allocator.constants, relevant for Longest_Stock_Duration
ALLOC_OPERATOR = MEDIAN                                          