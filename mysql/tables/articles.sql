#create table articles
CREATE TABLE masterarbeit.articles(
	id INT not null,
    price_str varchar(7),
    volume INT NOT NULL,
    weight INT NOT NULL,
    min_order_quantity INT NOT NULL,
    sold_online BOOL,
    start_stock_rate_str VARCHAR(15),
    PRIMARY KEY (id)
);

#import data
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/articles_sold_online.csv'
INTO TABLE masterarbeit.articles
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;
    
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/articles_sold_offline.csv'
INTO TABLE masterarbeit.articles
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;

#add column
ALTER TABLE masterarbeit.articles
	ADD COLUMN price DECIMAL(7,2) AFTER price_str,
    ADD COLUMN start_stock_rate DECIMAL(3,2) AFTER start_stock_rate_str;

#convert string values to float values in new columns    
UPDATE masterarbeit.articles
	SET price = replace(price_str, ",", ".") + 0.0,
        start_stock_rate = replace(start_stock_rate_str, ",", ".") + 0.0;

#drop string columns
ALTER TABLE masterarbeit.articles
	DROP COLUMN price_str,
    DROP COLUMN start_stock_rate_str;
    
#create table for articles sold online
CREATE TABLE masterarbeit.articles_sold_online
#insert articles sold online
SELECT a.* from articles as a, orderlines as ol
		WHERE a.id = ol.article_id
        GROUP BY ol.article_id
        ORDER BY ol.article_id;

#create table for articles sold offline        
CREATE TABLE masterarbeit.articles_sold_offline
#insert articles sold offline
SELECT a.* from articles as a, salelines as sl
		WHERE a.id = sl.article_id
        GROUP BY sl.article_id
        ORDER BY sl.article_id;
        
#drop original table articles
DELETE FROM masterarbeit.articles as a
WHERE a.id NOT IN (SELECT id FROM masterarbeit.articles_sold_online) OR a.id NOT IN(SELECT id FROM masterarbeit.articles_sold_offline);

#drop table with articles sold
DROP TABLE masterarbeit.articles_sold_online;
DROP TABLE masterarbeit.articles_sold_offline;
        
