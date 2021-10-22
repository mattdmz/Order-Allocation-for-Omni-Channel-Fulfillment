#all views regarding orderlines

#filter orderlines by id
CREATE OR REPLACE VIEW masterarbeit.lines_of_transaction AS
SELECT * FROM orderlines as ol
		 WHERE ol.transaction_id = specific_id()
         ORDER BY ol.transaction_id ASC;

#filter orderlines by period
CREATE OR REPLACE VIEW masterarbeit.lines_in_period AS
SELECT * FROM orderlines as ol  #works also with salelines as sl
		 WHERE ol.transaction_id IN (SELECT ol.transaction_id 
							   FROM orderlines as ol, orders as o
							   WHERE o.id = ol.transaction_id AND o.its_date BETWEEN start_date() AND end_date() 
							   ORDER BY ol.transaction_id ASC);
