#create table
CREATE TABLE masterarbeit.nodes(
	id INT NOT NULL,
    node_type SMALLINT NOT NULL,
    address VARCHAR(255),
    zip INT NOT NULL,
    city VARCHAR(50),
    gkz INT NOT NULL,
    latitude_str VARCHAR(15),
    longitude_str VARCHAR(15),
    fc INT NOT NULL,
    supply_distance INT NOT NULL,
    PRIMARY KEY (id)
);

#import data
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/stores.csv'
INTO TABLE masterarbeit.nodes
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS; 

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/fulfillment_centers.csv'
INTO TABLE masterarbeit.nodes
	FIELDS TERMINATED BY ';'
		   OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

#add column
ALTER TABLE masterarbeit.nodes
	ADD COLUMN latitude DECIMAL(9,7) AFTER latitude_str,
    ADD COLUMN longitude DECIMAL(9,7) AFTER longitude_str;

#convert string values to float values in new columns    
UPDATE masterarbeit.nodes
	SET latitude = replace(latitude_str, ",", ".") + 0.0,
        longitude = replace(longitude_str, ",", ".") + 0.0;

#drop string columns
ALTER TABLE masterarbeit.nodes 
	DROP COLUMN latitude_str,
    DROP COLUMN longitude_str;
    
ALTER TABLE masterarbeit.nodes
	ADD COLUMN zip_region SMALLINT 
    GENERATED ALWAYS AS (floor(nodes.zip / 100)) STORED
    AFTER zip;