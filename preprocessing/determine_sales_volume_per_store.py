
###############################################################################################

'''This script creates a file with a columns store id 
    and a column avg. monthly sales volume in m3 based on input data from saleline files.'''

###############################################################################################

def import_articles(input_path):

    #get a dict with article data
    with open(input_path, "r") as input_file:
        article_data = input_file.readlines()[1:]
        articles_dict = {}

        for row in article_data:
            row_fields = row.split(";")
            articles_dict.update({row_fields[0]: int(row_fields[2])})

    return articles_dict

def import_stores(input_path):

    #get a dict of store data
    stores_dict = {}
    with open(input_path, "r") as input_file:
        store_data = input_file.readlines()[1:]
        
        for row in store_data:
            row_fields = row.split(";")
            stores_dict.update({row_fields[0]: 0})

    return stores_dict

def calculate_sales_volume_per_store(input_path, articles_dict, stores_dict):

    #open sales transactions
    with open(input_path, "r") as input_file:
        sales_transactions = input_file.readlines()[1:]

        #for each sales transaction 
        for transact in sales_transactions:
            
            #split imported data row in fields
            transact_fields = transact.split(";")

            try:
                #get current volume of store
                current_volume = stores_dict[transact_fields[1]] 
            
            except KeyError:

                #if store was not listed, add it to the list
                stores_dict.update({transact_fields[1]: 0})
                current_volume = 0
            
            try:
                #get volume transaction ba calculating volumne of article * quantity bought
                volume =  articles_dict[transact_fields[4]] * int(transact_fields[5])
            
            except KeyError:
                
                #if article is not found, calcualte 10 cm3 for the article
                volume = 10 * int(transact_fields[5])
   
            #update volume of store
            stores_dict.update({transact_fields[1]: current_volume + volume})
    
    return stores_dict

def write_sales_volume_per_store(output_path, stores_dict, months):

    #create output file
    with open(output_path, "w") as output_file:

        #write headers
        output_file.write("store_id;avg_monthly_sales_volume_in_m3\n")

        #write results stored in dict
        for store_id, sales_volume in stores_dict.items():
            
            #write average
            output_file.write(store_id + ";" + str(sales_volume/1000000/4) + "\n")


if __name__ == "__main__":

    directory = "C:/Users/demetz/Documents/Masterarbeit/MA_Daten/MA_Daten_Verarbeitet/"
    articles_file_name = "Articles_all"
    stores_file_name = "Filialen_Bundesland_Zuordnung"
    salelines_file_name = "salelines_up_to_"
    file_dates = ["20190316", "20190331", "20190415", "20190430", "20190516", "20190531"]
    output_file_name = "sales_volume_per_store"
    file_type = ".csv"

    #get article data
    articles_dict = {}
    articles_dict = import_articles(directory + articles_file_name + file_type)

    #get store data
    stores_dict = {}
    stores_dict = import_stores(directory + stores_file_name + file_type)

    for file_date in file_dates:

        input_file = directory + salelines_file_name + file_date + file_type
        stores_dict = calculate_sales_volume_per_store(input_file, articles_dict, stores_dict)

    output_file = directory + output_file_name + file_type
    write_sales_volume_per_store(output_file, stores_dict, 3)