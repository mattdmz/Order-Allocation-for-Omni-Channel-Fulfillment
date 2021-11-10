
###############################################################################################

'''This file contains time simulation related functions.'''

###############################################################################################

from datetime import date, datetime, timedelta, time

from parameters import CUT_OFF_TIME, NUMBER_OF_WORKDAYS, OP_END_TIME
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

    return 0 if t1 == t2 else int(abs(t1 - t2).total_seconds() / 60)

def cut_off_time(current_day:date) -> datetime:

    '''Returns the cut_off_time of the current day in datetime format.'''

    return datetime.combine(current_day, CUT_OFF_TIME)

def delivered_on(current_time:datetime, node_type:int) -> date:

    ''' Returns the day the order is delivered given current_datetime. If cut off time is not reached yet, 
        the current date is returned, else current date + 1 day is returned.'''

    if current_time <= datetime.combine(current_time.date(), OP_END_TIME[node_type]) and current_time.date().isoweekday() <= NUMBER_OF_WORKDAYS:
        return current_time.date()

    elif current_time > datetime.combine(current_time.date(), OP_END_TIME[node_type]) and current_time.date().isoweekday() < NUMBER_OF_WORKDAYS: 
        return (current_time + timedelta(days=1)).date()
    
    elif current_time > datetime.combine(current_time.date(), OP_END_TIME[node_type]) and current_time.date().isoweekday() == NUMBER_OF_WORKDAYS: 
        return (current_time + timedelta(days=7 - NUMBER_OF_WORKDAYS + 1)).date()
    
    else: #current_time.date().isoweekday() > NUMBER_OF_WORKDAYS
        return (current_time + timedelta(days=7 - NUMBER_OF_WORKDAYS)).date()

