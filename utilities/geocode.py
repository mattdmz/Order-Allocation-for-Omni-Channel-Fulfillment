
###############################################################################################

'''This file the class Geolocator, the class Location and funcitons to geocode single addresses
    or to geocode addresses batchwise.'''

###############################################################################################

#geocodes (latitude and longitude) addresses from input file with geopy library

from geopy import geocoders 
from pandas import DataFrame

from utilities.expdata import write_df
from utilities.impdata import from_csv

class Geolocator:

    '''Creates a connection to geopy.geocoders.Nominatim.'''

    def __init__(self) -> None:
        
        pass

    def __enter__(self) -> geocoders.Nominatim:

        '''Returns a geolocator connection.'''
        return geocoders.Nominatim(user_agent='test')

    def __exit__(self, type, value, traceback) -> None:
        
        pass


class Location:

    '''Geocodes single address when passed
         like address = "streetname number, zip [city]". '''

    def __init__(self, address:str) -> None:

        #store address
        self.address = address

        #start connection manager
        with Geolocator() as gl:
            
            #geocode address
            location = gl.geocode(self.address)

            #map result
            self.latitude = location.latitude
            self.longitude = location.longitude

def geocode_batchwise(addresses:list) -> DataFrame:

    '''Geocodes list of address when passed
        like address = "streetname number, zip [city]". '''

    #init dataframe
    df = DataFrame(columns=["address", "latitude", "longitude"])

    #start connection manager
    with Geolocator() as gl:

        for address in addresses:
            
            try:
                #geocode location
                location = gl.geocode(address)
                
                #write address (cut newline) and add location attributes
                df = df.append({"address": address, "latidude": location.latitude, "longitude": location.longitude}, ignore_index=True)
                
            except:
                #if location could not be identified, write input address only
                df = df.append({"address": address}, ignore_index=True)

    return df

def main(input_file_name:str, test_print_df_head:bool=False, output_file_name:str=None):

    '''Main procedure to geocode single or multiple addresses.
        Results can be exported to the default output directory by 
        setting an output_file_name.
        Output can be test-printed by setting test_print_df_head=True.'''

    #read addresses
    addresses = from_csv(input_file_name, read_headers=False)

    #geocode addresses
    df = geocode_batchwise(addresses)

    #test print
    if test_print_df_head:
        print(df.head())
                    
    #write data to output_file
    if output_file_name is not None:
        write_df(df, output_file_name, header=True, index=False)
            

if __name__ == "__main__":

    #test parameters
    input_file_name = "Addresses"
    test_print_df_head = False
    output_file_name = "Geocoded_Addresses"

    main(input_file_name, test_print_df_head, output_file_name)

    #test 
    #location = Location("Via Val 13 39047, S. Cristina Valgardena")
    #print(location.address, location.latitude, location.longitude)




