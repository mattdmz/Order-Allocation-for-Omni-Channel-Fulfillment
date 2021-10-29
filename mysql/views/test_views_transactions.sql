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
         
#SET @start_date = "2019-03-01", @end_date = "2019-03-02";
CREATE OR REPLACE VIEW masterarbeit.orders_in_zip_region AS
SELECT * FROM orders as o
		 WHERE o.customer_id IN (SELECT customer_id 
								 FROM orders as o, customers as c
                                 WHERE o.customer_id = c.id AND o.its_date BETWEEN start_date() AND end_date() AND c.zip_region = zip_region()
								 ORDER BY o.id ASC);


#orders on day btw times in fc Region
SET @start_date = "2019-03-01", @end_date = "2019-03-01"; 
SELECT *
FROM orders as o, customers as c
WHERE o.its_date = start_date() 
AND (o.its_time >= '00:00' AND o.its_time <= '03:50')
AND o.customer_id = c.id
AND c.fc = 1001;

								