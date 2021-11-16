# testing timeit()
 
import timeit
import random
 
def test(): 
    return random.randint(10, 100)
 
starttime = timeit.default_timer()
print("The start time is :",starttime)
test()

for n in range(100):
    print("t: ", timeit.default_timer())