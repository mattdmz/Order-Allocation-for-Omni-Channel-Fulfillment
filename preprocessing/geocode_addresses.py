
###############################################################################################

''' This script geocodes (latitude and longitude) addresses 
    from input file with geopy library.'''

###############################################################################################    

def geocode_addresses(directory, input_file_name, output_file_name):

    from geopy import geocoders as gc

    #active geocoder
    geolocator = gc.Nominatim(user_agent='test')

    #read addresses to geocode
    with open(directory + input_file_name, 'r') as input_file:
        
        #read and skip headers
        addresses = input_file.readlines()[1:]

    #write results
    with open(directory + output_file_name, 'w') as output_file:
        
        #write headings
        output_file.write("Address, Latitude, Longitude\n")

        for address in addresses:
            
            try:
                #geocode location
                location = geolocator.geocode(address)
                
                #write address (cut newline) and add location attributes
                location_str = str(address[:-1]) + ";" +  str(location.latitude) + ";" + str(location.longitude)
                
            except:
                #if location could not be identified, write address only
                location_str = address[0] + ";" + address[1]
                    
            #write adress, longitude and latitude
            output_file.write(location_str + "\n")
            
            #test print
            #print(location_str)

def main():

    '''Geocode set of adderesses.'''

    #parameters

    directory = "C:/Users/demetz/Documents/Masterarbeit/MA_Daten/MA_Daten_Verarbeitet/"
    input_file_name = "Addresses.csv"
    output_file_name = "Geocoded_Addresses.csv"

    geocode_addresses(directory, input_file_name, output_file_name)

if __name__ == "__main__":

    main()




