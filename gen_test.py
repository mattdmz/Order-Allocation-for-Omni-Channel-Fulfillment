

from numpy import array, sum, round


x = array([[10.4512, 0, 0],
        [10, 3.1245, 10.1254],
        [0, 3.1245, 0]])

y = array([[False, True, True],
        [True, True, True],
        [False, True, False]])

z = array([[0., 0., 0.],
        [0., 3., 0.],
        [0., 3., 0.]])

a = sum((z == 0) * y)

print(a)





