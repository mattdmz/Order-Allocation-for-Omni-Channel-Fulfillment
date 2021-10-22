
###############################################################################################

'''This script merges addresses with zip-code and city 
    based on SKZ (Strassenkennzeichen) and GKZ (Gebietskennzeichen).'''

###############################################################################################

def create_address(addresses_path, streets_path, output_path):

    #read input file adresses
    with open(streets_path, "r") as input_streets:
        streetdata = input_streets.readlines()[1:]

        #initialize dict
        streets_dict = {}
        city_dict = {}

        for row in streetdata:
            
            #split row
            row_fields = row.split(";")

            #add SKZ and street name to dict
            streets_dict.update({row_fields[0]: row_fields[1][1:-1]}) 
            
            #add GKZ and street name to dict
            city_dict.update({row_fields[4]: row_fields[5][1:-2]}) 


    #read input file addresses
    with open(addresses_path, "r") as input_adresses:
        adressdata = input_adresses.readlines()[1:]

    #create output file
    with open(output_path, "w+") as output_file:
        
        #write headers
        output_file.write("GKZ;Adresse;PLZ;Ort;"+"\n")

        #write all lines
        for row in adressdata:
        
            #split txt
            row_fields = row.split(";")

            #output data
            gkz = row_fields[1][1:-1]
            address = streets_dict[row_fields[4]] + " " + row_fields[7] + row_fields[8][1:-1]
            zip_code = row_fields[3][1:-1]
            city = city_dict[row_fields[1]]

            #write address
            output_file.write(gkz + ";" + address + ";" + zip_code + ";" + city + "\n")


if __name__ == "__main__":

    #parameters

    directory = "C:/Users/demetz/Documents/Masterarbeit/MA_Daten/MA_Daten_Original/"
    streets_file_name = "Strassen"
    addresses_file_name = "Adressen" 
    output_file_name = "addresses"
    file_type = ".csv"

    addresses_path = directory + addresses_file_name + file_type
    streets_path = directory + streets_file_name + file_type
    output_path = directory + output_file_name + file_type

    create_address(addresses_path, streets_path, output_path)
