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