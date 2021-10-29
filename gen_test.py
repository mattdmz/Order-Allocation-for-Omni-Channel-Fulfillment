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

from numpy import array, delete


class deliv:
    def __init__(self) -> None:
        self.duration_matrix = array([[   0, 1, 2, 3, 4, 5],
                                        [   1, 1, 2, 3, 4, 5],
                                        [   2, 1, 2, 3, 4, 5],
                                        [   3, 1, 2, 3, 4, 5],
                                        [   4, 1, 2, 3, 4, 5],
                                        [   5, 1, 2, 3, 4, 5]])
    def test(self, delivery_index):

        self.duration_matrix = delete(self.duration_matrix, delivery_index + 1, axis=0)
        self.duration_matrix = delete(self.duration_matrix, delivery_index + 1, axis=1)

d = deliv()
d.test(0)
print(d.duration_matrix)