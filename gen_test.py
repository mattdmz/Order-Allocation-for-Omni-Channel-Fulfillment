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

# from numpy import array, delete


# class deliv:
#     def __init__(self) -> None:
#         self.duration_matrix = array([[   0, 1, 2, 3, 4, 5],
#                                       [   0, 1, 2, 3, 4, 5],
#                                       [   0, 1, 2, 3, 4, 5],
#                                       [   0, 1, 2, 3, 4, 5],
#                                       [   0, 1, 2, 3, 4, 5],
#                                       [   0, 1, 2, 3, 4, 5]])
    
#     def test(self, route:list):

#         y = 0

#         for r in range(len(route) - 1):
#             x = self.duration_matrix[route[r], route[r+1]] 
#             print(route[r], " -> ", route[r+1], x)
#             y += x

#         return int(round(y, 0))

# d = deliv()
# route = [0, 3, 5, 2, 4, 1, 0]

# print(d.test(route))

# from parameters import STOCK_BETA_SERVICE_DEGREE, RPL_CYCLE_DURATION

# from math import ceil, sqrt
# from scipy.stats import norm

# def test(abc_category, avg_daily_demand, variance_demand):

#     ppf = norm.ppf(STOCK_BETA_SERVICE_DEGREE[abc_category], loc=0, scale=1)
#     return int(ceil(10 * avg_daily_demand + ppf * sqrt(RPL_CYCLE_DURATION * variance_demand)))


# abc_category = "c"
# avg_daily_demand = 0.2857 #10.461585
# variance_demand = 1.072664 #1.76729408

# print(test(abc_category, avg_daily_demand, variance_demand))

class X:

    def __init__(self) -> None:
        pass

y = X()

l = [X(), X(), X()]

l.append(y)

if y in l:
    print("true)")

