#create table orderlines (WITHOUT PRIMARY OR FOREGIN KEY)
CREATE TABLE masterarbeit.orderlines(
	transaction_id INT NOT NULL,
    customer_id INT NOT NULL,
    its_date DATE,
    its_time TIME,
    article_id INT NOT NULL,
    quantity SMALLINT NOT NULL
);

#import data
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/orderlines.csv'
INTO TABLE masterarbeit.orderlines
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
	IGNORE 1 ROWS;
    
#create table orders from orderlines
USE masterarbeit;
CREATE TABLE orders AS
SELECT ol.transaction_id as id, ol.customer_id, ol.its_date, ol.its_time,
		sum(a.price * ol.quantity) as price, sum(a.volume * ol.quantity) as volume, sum(a.weight * ol.quantity) as weight
		FROM orderlines as ol, articles as a
		WHERE ol.article_id = a.id
		GROUP BY ol.transaction_id;

#add primary keys to orders
ALTER TABLE masterarbeit.orders
	  ADD PRIMARY KEY (id);

#add foreign keys to orderlines
ALTER TABLE masterarbeit.orderlines
	  ADD FOREIGN KEY (transaction_id) REFERENCES orders(id),
	  ADD FOREIGN KEY (article_id) REFERENCES articles(id);

#drop redundant columns in orderlines
ALTER TABLE masterarbeit.orderlines
	  DROP COLUMN customer_id,
      DROP COLUMN its_date,
      DROP COLUMN its_time;
