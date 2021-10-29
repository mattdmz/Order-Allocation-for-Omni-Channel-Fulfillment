# from numpy import array, sum

# current_stock = array([ [100, 100, 100, 100, 100], 
#                         [100, 100, 100, 100, 100], 
#                         [100, 100, 100, 100, 100]] )

# reserved_stock = array([ [10, 10, 10, 10, 10], 
#                          [10, 0, 0, 10, 0], 
#                          [10, 10, 10, 0, 10]])

# demanded_stock = array([0, 10, 0, 0, 0])

# holding_rates = [1, 1, 1, 1, 1]



# x  = sum((sum((current_stock- reserved_stock) * (demanded_stock > 0)  - demanded_stock, axis=0) * holding_rates))

# print(sum((current_stock- reserved_stock) * (demanded_stock > 0)  - demanded_stock, axis=0))
# print(x)

# from numpy import array, zeros

# current_stock = array([ [100, 100, 100, 100, 100], 
#                         [100, 100, 100, 100, 100], 
#                         [100, 100, 100, 100, 100]] )

# lines = [0, 1, 2]

# stock_held_for_order = zeros(shape=(len(current_stock[1])))

# for line_index in lines:

#     for node_index in range(0, current_stock.shape[1]):
#         node_index:int

#         stock_held_for_order[node_index] += current_stock[line_index, node_index]

# print(stock_held_for_order)


# x = {"p":True}

# x["p"] += True
# x["p"] += False
# x["p"] += True
# x["p"] += False

# print(x["p"])




# Attempt 2 (this one seems to work, but on closer inspection it duplicates 
#the last item in the dictionary, because another reference is created to it):

from numpy import array

avg_speed = 0.2
distances = array([0.124578, 1.124587, 4.21547, 1.12457])
loading_time_per_order = 0.5
service_time_per_order = 4

x = (distances/avg_speed) + (loading_time_per_order + service_time_per_order)

print(x)