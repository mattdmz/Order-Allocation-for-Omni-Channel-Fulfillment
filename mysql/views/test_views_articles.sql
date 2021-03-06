#all views regarding articles

#articles_sold_online
#SET  @start_date = "2019-03-01", @end_date = "2019-06-30", @zip_region = 11;
CREATE OR REPLACE VIEW masterarbeit.articles_sold_online AS
SELECT * FROM articles as a
		 WHERE a.id IN (SELECT article_id FROM orders as o, orderlines as ol, customers as c
						WHERE o.id = ol.transaction_id AND c.zip_region = zip_region() AND o.its_date BETWEEN start_date() AND end_date() 
						GROUP BY ol.article_id
						ORDER BY ol.article_id ASC);
                        
#quantity_of_article_sold_online_in_zip_region
#SET  @start_date = "2019-05-30", @end_date = "2019-05-31", @zip_region = 11, @specific_id = 4;
CREATE OR REPLACE VIEW masterarbeit.quantity_of_article_sold_online_in_zip_region AS
SELECT ol.article_id, sum(ol.quantity) as quantity_sold 
		FROM orderlines as ol, orders as o, customers as c
		WHERE o.id = ol.transaction_id AND ol.article_id = specific_id() AND o.customer_id = c.id AND c.zip_region = zip_region() AND o.its_date BETWEEN start_date() AND end_date()
		GROUP BY ol.article_id
        ORDER BY ol.article_id;
        
#quantity_of_article_sold_online_in_fc_region
#SET  @start_date = "2019-03-01", @end_date = "2019-05-31", @fc_id = 1001, @specific_id = 4;
CREATE OR REPLACE VIEW masterarbeit.quantity_of_article_sold_online_in_fc_region AS
SELECT ol.article_id, sum(ol.quantity) as quantity_sold 
		FROM orderlines as ol, orders as o, customers as c
		WHERE o.id = ol.transaction_id AND ol.article_id = specific_id() AND o.customer_id = c.id AND c.fc = fc_id() AND o.its_date BETWEEN start_date() AND end_date()
		GROUP BY ol.article_id
        ORDER BY ol.article_id;
        
#quantity_of_article_sold_offline_in_zip_region
#SET  @start_date = "2019-03-01", @end_date = "2019-05-31", @zip_region = 11, @specific_id = 4;
CREATE OR REPLACE VIEW masterarbeit.quantity_of_article_sold_offline_in_zip_region AS
SELECT sl.article_id, sum(sl.quantity) as quantity_sold 
		FROM salelines as sl, sales as s, nodes as n
		WHERE s.id = sl.transaction_id AND sl.article_id = specific_id() AND s.node_id = n.id AND n.zip_region = zip_region() AND s.its_date BETWEEN start_date() AND end_date()
		GROUP BY sl.article_id
        ORDER BY sl.article_id;
        
#quantity_of_article_sold_offline_in_fc_region
#SET  @start_date = "2019-03-01", @end_date = "2019-05-31", @fc_id = 1001, @specific_id = 4;
CREATE OR REPLACE VIEW masterarbeit.quantity_of_article_sold_offline_in_fc_region AS
SELECT sl.article_id, sum(sl.quantity) as quantity_sold 
		FROM salelines as sl, sales as s, nodes as n
		WHERE s.id = sl.transaction_id AND sl.article_id = specific_id() AND s.node_id = n.id AND n.fc = fc_id() AND s.its_date BETWEEN start_date() AND end_date()
		GROUP BY sl.article_id
        ORDER BY sl.article_id;

#articles sold (online and offline)
#SET  @start_date = "2019-05-30", @end_date = "2019-05-31", @fc_id = 11;        
SELECT * FROM articles as a
WHERE a.id in ( SELECT ol.article_id 
				FROM orders as o, orderlines as ol, customers as c
                WHERE o.id = ol.transaction_id
					AND o.its_date BETWEEN start_date() AND end_date()
					AND o.customer_id = c.id
					AND c.fc = fc_id()
                GROUP BY ol.article_id)
OR a.id in (	SELECT sl.article_id 
				FROM sales as s, salelines as sl, nodes as n
                WHERE s.id = sl.transaction_id
					AND s.its_date BETWEEN start_date() AND end_date()
					AND s.node_id = n.id
					AND n.fc = fc_id()
                GROUP BY sl.article_id
);



