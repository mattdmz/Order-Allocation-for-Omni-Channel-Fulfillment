
#create table sales
CREATE TABLE masterarbeit.sales(
	id BIGINT NOT NULL,
	node_id INT NOT NULL,
	sales_date DATE,
	sale_time TIME,
	number_of_salelines SMALLINT NOT NULL,
	price_str VARCHAR(7),
	volume INT NOT NULL,
	weight INT NOT NULL,
    PRIMARY KEY (id),
	its_datetime datetime,
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

#add column
ALTER TABLE masterarbeit.sales
	ADD COLUMN price DECIMAL(7,2) AFTER price_str;

#convert string values to float values in new columns    
UPDATE masterarbeit.sales
	SET price = REPLACE(price_str, ",", ".") + 0.0;

#drop string columns
ALTER TABLE masterarbeit.sales 
	DROP COLUMN price_str;

#create table salelines (WITHOUT primary or secondary key)
CREATE TABLE masterarbeit.salelines(
	transaction_id BIGINT NOT NULL,
    node_id INT NOT NULL,
	its_date date,
	its_time time,
    article_id INT NOT NULL,
    quantity SMALLINT NOT NULL
    );
    
#add foreign keys to salelines
ALTER TABLE masterarbeit.salelines
	  ADD FOREIGN KEY (transaction_id) REFERENCES sales(id),
	  ADD FOREIGN KEY (article_id) REFERENCES articles(id);

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/salelines_up_to_20190316.csv'
INTO TABLE masterarbeit.salelines
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
    IGNORE 1 LINES;
    
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/salelines_up_to_20190331.csv'
INTO TABLE masterarbeit.salelines
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
    IGNORE 1 LINES;
    
#drop redundant columns in salelines
ALTER TABLE masterarbeit.salelines
      DROP COLUMN its_date;
ALTER TABLE masterarbeit.salelines
      DROP COLUMN its_time;
ALTER TABLE masterarbeit.salelines
	  DROP COLUMN node_id;
