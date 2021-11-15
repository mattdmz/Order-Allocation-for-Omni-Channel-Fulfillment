
###############################################################################################

''' This script returns a files (based on a date-range) 
    with saleslines containing articles solf online.'''

###############################################################################################


def get_articles_sold_online(input_path):

    #open data of articles sold online and append ids to a list
    with open(input_path, "r") as input_file:

        article_data = input_file.readlines()[1:]
        
        articles = []

        #append all articles sold online to a list
        for row in article_data:

            row = row.split(";")

            articles.append(row[0])

    return articles

def check_for_transctions_with_articles_sold_online(articles, input_path, output_path):

    #put articles set online into a set
    online_sold_articels = set(articles)
    
    #open sales transactions
    with open(input_path, "r") as input_file:

        transactions_data = input_file.readlines()[1:]

        #open output file and write down only transactions that contained online-sold articles
        with open(output_path, "a") as output_file:

            for row in transactions_data:

                article = row.split(";")

                if article[4] in online_sold_articels:

                    output_file.write(row)

def main():

    '''Check for transactions with articles sold online.'''

    directory = "C:/Users/demetz/Documents/Masterarbeit/MA_Daten/MA_Daten_Verarbeitet/"
    articles_file_name = "Articles.csv"
    input_file_name = "Abverkaufsdaten_bis_"
    file_dates = ["20190316", "20190331", "20190415", "20190430", "20190516", "20190531"]
    file_type = ".txt"
    output_file = "Abverkaufsdaten_03-06_online_gekaufte_Artikel.csv"

    #get articles sold online
    articles = []
    articles = get_articles_sold_online(directory + articles_file_name)

    for file_date in file_dates:

        check_for_transctions_with_articles_sold_online(articles, directory + input_file_name + file_dates + file_type, directory + output_file)


if __name__ == "__main__":

    main()

