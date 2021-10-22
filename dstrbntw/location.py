
###############################################################################################

'''This file contains the class Location and related functions.'''

###############################################################################################

from math import cos, sqrt


class Location():

    '''Stores a geographical location with an id and its latitude and longitude.'''

    def __init__(self, id:int, latitude:float, longitude:float):

        #set location
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
    
def distance(loc1:Location, loc2:Location):

    '''computes distance in km between two geocoded locations.'''

    #source: https://www.kompf.de/gps/distcalc.html

    dx = 111.3 * abs((loc1.latitude - loc2.latitude))
    lat = (loc1.latitude + loc2.latitude) / 2 * 0.01745
    dy = 111.3 * cos(lat) * abs(loc1.longitude - loc2.longitude)

    return sqrt(dx * dx + dy * dy)


