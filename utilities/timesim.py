
###############################################################################################

'''This file contains time simulation related functions.'''

###############################################################################################

from datetime import date, datetime, timedelta, time

from utilities.constants import ADD


def daterange(start:date, end:date)-> date:

    '''Function to iterate through a range of days.'''

    for day in range(int((end - start).days)):
        yield start + timedelta(day)

def timerange(start:time, end:time, units:str)-> time:

    '''Function to iterate through a range of time (hours or minutes).'''

    if units == "minutes":

        for minute in range(int((end - start).seconds/60)):
            yield (start + timedelta(minutes=minute)).time()
    
    else: #units == "hours":
        for hour in range(int((end - start).seconds/3600) + 1):
            yield (start + timedelta(hours=hour)).time()

def calc_time(t:time, min:int, operation:str) -> time:  

    '''Adds or subtracts min (integer) from a given time t depending on the parameter operation passed.'''
    
    return  ((datetime.combine(datetime.today(), t) + timedelta(minutes=min)).time()) if operation == ADD else \
            ((datetime.combine(datetime.today(), t) - timedelta(minutes=min)).time())

def time_diff(t1:datetime, t2:datetime) -> int:

    '''Returns the difference in minutes between two timestamps.'''

    return int(abs(t1 - t2).total_seconds() / 60)