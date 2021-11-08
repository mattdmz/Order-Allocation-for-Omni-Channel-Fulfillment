#select all orders
CREATE OR REPLACE VIEW masterarbeit.all_transactions AS
SELECT * FROM orders       #sales
		 ORDER BY id ASC; 

#all_transactions_in_period
#SET @start_date = "2019-03-01", @end_date = "2019-03-02";
CREATE OR REPLACE VIEW masterarbeit.transactions_in_period AS
SELECT * FROM orders    #sales     
         WHERE its_date BETWEEN start_date() AND end_date()
         ORDER BY id ASC;
         
SET @start_date = "2019-03-01", @end_date = "2019-03-02", @zip_region=1001;
#CREATE OR REPLACE VIEW masterarbeit.orders_in_zip_region AS
SELECT * FROM orders as o
		 WHERE o.customer_id IN (SELECT customer_id 
								 FROM orders as o, customers as c
                                 WHERE o.customer_id = c.id AND o.its_date BETWEEN start_date() AND end_date() AND c.zip_region = zip_region()
								 ORDER BY o.id ASC);


#orders on day btw times in fc Region
SET @start_datetime = "2019-03-01 00:00:00", @end_datetime = "2019-03-02 20:00:00", @fc_id = 1005;
SELECT *
FROM orders as o, customers as c
WHERE cast(o.its_date as datetime) + cast(o.its_time as time) BETWEEN cast(start_datetime() as datetime) AND cast(end_datetime()  as datetime) #start_datetime() and end_datetime()
AND o.customer_id = c.id
AND c.fc = fc_id();

								