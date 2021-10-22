
###############################################################################################

'''This script cleans saleline_data recieved by dm:
    - formats data
    - ignores rows with missing store_id or article_id 
      as these rows are useless given the missing reference
    - creates several files with data of 15 days each to keep file size reasonable.'''

###############################################################################################

from datetime import datetime as dt

def add_leading_zeros(date_string):

    date_with_leading_zeros = ""
    
    for part in date_string.split("."):
        if len(part) < 2:
            part = "0" + part
        date_with_leading_zeros += part + "."

    return date_with_leading_zeros[:-1]


def clean_and_sumamrize_sales_data(file_path, source_file_name, file_dates, source_file_type, target_file_name, target_file_type):
        
    for file_date in file_dates:

        #create new target file
        with open(file_path + target_file_name + file_date +target_file_type, "w") as target_file:
        
            #Write Headings
            target_file.write("sale_id;node_id;sale_day;sale_time;article_id;quantity\n")

            #open source file
            with open(file_path + source_file_name + file_date + source_file_type, "r") as source_file:
                
                lines = source_file.readlines()[1:]
        
                #write all lines
                for line in lines:
                    
                    #split txt
                    currentline = line.split(";")

                    #clean values
                    id = currentline[0][3:-1]
                    node_id = currentline[1][:-3]
                    date_ = currentline[2][:-9]
                    time_ = currentline[3][-8:]
                    article_id = currentline[4][:-3] 
                    amount = currentline[5][:-4]

                    #write only salelines with a node_id and article_id values (salelines without this information are useless)
                    if node_id != "" and article_id != "":

                        #check if date has to by formated
                        if len(date_) < 10:
                            date_ = add_leading_zeros(date_)

                        #format date
                        formated_date = dt.strptime(date_, "%d.%m.%Y").strftime("%Y-%m-%d")

                        #test print
                        #print(id + ";" + node_id + ";" + formated_date + ";" + time_ + ";" + article_id + ";" + amount + "\n")

                        #write line with clened text
                        target_file.write(id + ";" + node_id + ";" + formated_date + ";" + time_ + ";" + article_id + ";" + amount + "\n")



if __name__ == "__main__":

    #parameters

    file_path = "C:/Users/demetz/Documents/Masterarbeit/MA_Daten/MA_Daten_Original/Abverkaufsdaten/"

    source_file_name = "Abverkaufsdaten_stationär_bis_"
    souce_file_dates = ["20190316", "20190331", "20190415", "20190430", "20190516", "20190531"]
    source_file_type = ".txt"
    target_file_name = "salelines_up_to_"
    target_file_type = ".csv"

    clean_and_sumamrize_sales_data(file_path, source_file_name, souce_file_dates, source_file_type, target_file_name, target_file_type)
