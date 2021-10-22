
###############################################################################################

'''This scripts assigns a random address to a customer within a certain GKZ (Gemeindekennzeichen)
    It Creates a output file with the result.'''

###############################################################################################



def assign_random_adress_within_gkz_to_customer(directory, customers_file_name, number_of_customers_file_name, addresses_file_name, output_file_name):

    #load the initial data with addresses
    with open(directory + customers_file_name, "r") as input_file:
        customer_ids = input_file.readlines()[1:] #--> headers = id

    #load the initial data with addresses
    with open(directory + addresses_file_name, "r") as input_file:
        address_data = input_file.readlines()[1:] #--> headers = address;zip;city;gkz;latitude;longitude

        #map data
        addresses = []

        for row in address_data:
            splitted_row = row.split(";")
            addresses.append([splitted_row[0], splitted_row[1], splitted_row[2], splitted_row[3], splitted_row[4], splitted_row[5]])

        del address_data

    #load the initial data with customer Ids
    with open(directory + number_of_customers_file_name, "r") as input_file:
        customers_per_gkz = input_file.readlines()[1:] #--> headers = gkz;number_of_customers

        #determine number_of_customers and map data
        number_of_customers = 0
        gkz_dict = {}

        for row in customers_per_gkz:

            #generate a list from each row and each list has items that were separated with 
            splitted_row = row.split(";")

            #count total number of customers
            number_of_customers += int(splitted_row[1])

            #map data gkz: number_of_customers
            gkz_dict.update({splitted_row[0]: int(splitted_row[1])})

        del customers_per_gkz

    #create output file
    with open(directory + output_file_name, "w") as output_file:

        #write headers
        output_file.write("id;address;zip;cit;gkz;latitude;longitude\n")

        #initialize list
        potential_addresses = []

        #for each GKZ
        for gkz in gkz_dict.keys():
            
            #get potential addresses
            for address in addresses:
                if gkz == address[3]:
                    potential_addresses.append(address)

            #for the number of customers residing in a city
            for customer in range(0, gkz_dict[gkz]):

                #randomly drow a customer's id and an address
                id = customer_ids.pop()
                address = potential_addresses.pop()

                #write output string
                output_str = str(int(id))
                for value in address:
                    output_str += ";" + value

                #test print
                #print(output_str)
                
                #write down assigned address
                output_file.write(output_str)

if __name__ == "__main__":

    #parameters
    
    directory = "C:/Users/demetz/Documents/Masterarbeit/MA_Daten/MA_Daten_Verarbeitet/Zwischenschritte/"
    customers_file_name = "customer_ids.csv"
    number_of_customers_file_name = "number_of_customers_per_gkz.csv"
    addresses_file_name = "addresses.csv"
    output_file_name = "customers.csv"

    assign_random_adress_within_gkz_to_customer(directory, customers_file_name, number_of_customers_file_name, addresses_file_name, output_file_name)
