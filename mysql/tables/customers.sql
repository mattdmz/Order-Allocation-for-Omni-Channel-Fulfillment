#create table customers
CREATE TABLE masterarbeit.customers(
	id INT NOT NULL,
    node_type SMALLINT NOT NULL,
    address VARCHAR(255),
    zip INT NOT NULL,
    city VARCHAR(50),
    gkz INT NOT NULL,
    latitude_str VARCHAR(25),
    longitude_str VARCHAR(25),
    fc INT NOT NULL,
    PRIMARY KEY (id)
);

#import data
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/customers.csv'
INTO TABLE masterarbeit.customers
	CHARACTER SET utf8mb4
	FIELDS TERMINATED BY ';'
		   OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS; 

#add column
ALTER TABLE masterarbeit.customers
	ADD COLUMN latitude DECIMAL(9,7) AFTER latitude_str,
    ADD COLUMN longitude DECIMAL(9,7) AFTER longitude_str;

#convert string values to float values in new columns    
UPDATE masterarbeit.customers
	SET latitude = replace(latitude_str, ",", ".") + 0.0,
        longitude = replace(longitude_str, ",", ".") + 0.0;

#drop string columns
ALTER TABLE masterarbeit.customers 
	DROP COLUMN latitude_str,
    DROP COLUMN longitude_str;
    
ALTER TABLE masterarbeit.customers
	ADD COLUMN zip_region SMALLINT
    GENERATED ALWAYS AS (floor(customers.zip / 100)) STORED
    AFTER zip;