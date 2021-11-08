

# from numpy import array


# x = array([[10, 10, 10],
#         [10, 10, 10],
#         [10, 10, 10]])

# y = array([1, 2, 3])

# z = array([[0], [1], [2]])

# print(x * (y-z))

routes = [2, 4, 3, 1, 5]
orders_to_deliver = [1, 2, 3, 4, 5]
order_to_remove = 1


for index, order in enumerate(orders_to_deliver):
    if index > order_to_remove:
        break

for i in range(index, len(orders_to_deliver)):
    orders_to_deliver[i] -= 1
        
for i, stop in enumerate(routes):
    if i == order:
        break

for i in range(index, len(routes)):
    routes[i] -= 1

print(orders_to_deliver)
print(routes)



