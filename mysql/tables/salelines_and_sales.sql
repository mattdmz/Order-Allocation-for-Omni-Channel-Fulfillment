
#create table sales
CREATE TABLE masterarbeit.sales(
	id BIGINT NOT NULL,
	node_id INT NOT NULL,
	sales_date DATE,
	sale_time TIME,
	price_str VARCHAR(7),
	volume INT NOT NULL,
	weight INT NOT NULL,
	its_datetime datetime,
    PRIMARY KEY (id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190301.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190302.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190304.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190305.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190306.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190307.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190308.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;


LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190309.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190311.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_201903012.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190313.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190314.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190315.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190316.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190318.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190319.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190320.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190321.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_201903022.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190323.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190325.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190326.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190327.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190328.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190329.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_20190330.csv'
INTO TABLE masterarbeit.sales
	FIELDS TERMINATED BY ','
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
