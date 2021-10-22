#all views regarding customers



#filter customers by period
#SET  @start_date = "2019-03-01", @end_date = "2019-03-02", @zip_region = 44;
CREATE OR REPLACE VIEW masterarbeit.customers_buying_online AS                                    
SELECT * FROM customers as c
		 WHERE c.id IN (SELECT customer_id FROM orders as o
						WHERE o.its_date BETWEEN start_date() AND end_date() AND c.zip_region = zip_region()
						GROUP BY c.id
						ORDER BY c.id ASC);