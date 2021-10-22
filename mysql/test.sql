Use masterarbeit;

SELECT ol.transaction_id as id, ol.customer_id, ol.its_date, ol.its_time,
		sum(a.price * ol.quantity) as price, sum(a.volume * ol.quantity) as volume, sum(a.weight * ol.quantity) as weight
		FROM orderlines as ol, articles as a
		WHERE ol.article_id = a.id
		GROUP BY ol.transaction_id;

SET @start_date = "2019-05-30", @end_date = "2019-05-31";

SELECT ol.article_id, sum(ol.quantity) as quantity_sold
FROM orderlines as ol, orders as o
WHERE o.id = ol.transaction_id AND o.its_date BETWEEN start_date() AND end_date()
GROUP BY ol.article_id
ORDER BY ol.article_id;

SET  @start_date = "2019-05-30", @end_date = "2019-05-31", @zip_region = 11;
SELECT ol.article_id, sum(ol.quantity) as quantity_sold 
		FROM orderlines as ol, orders as o, customers as c
		WHERE o.id = ol.transaction_id AND o.customer_id = c.id AND c.zip_region = zip_region() AND o.its_date BETWEEN start_date() AND end_date()
		GROUP BY ol.article_id
        ORDER BY ol.article_id;

SET  @start_date = "2019-03-01", @end_date = "2019-05-29", @specific_id = 4793, @zip_region = 1;
SELECT sl.article_id, sum(sl.quantity) as quantity_sold FROM salelines as sl, sales as s
WHERE s.id = sl.transaction_id AND sl.article_id = specific_id() AND s.node_id = zip_region() AND s.its_date BETWEEN start_date() AND end_date()
		GROUP BY sl.article_id
        ORDER BY sl.article_id;
        
SET  @start_date = "2019-03-01", @end_date = "2019-05-29", @specific_id = 4793, @zip_region = 10;
SELECT ol.article_id, sum(ol.quantity) as quantity_sold FROM orderlines as ol, orders as o, customers as c
WHERE o.id = ol.transaction_id AND o.customer_id = c.id AND c.zip_region = zip_region() AND o.its_date BETWEEN start_date() AND end_date()
		GROUP BY ol.article_id
        ORDER BY ol.article_id;
        
        
SET  @start_date = "2019-03-01", @end_date = "2019-05-29", @specific_id = 1;
SELECT sl.article_id, variance(sl.quantity) as var FROM salelines as sl, sales as s
WHERE s.id = sl.transaction_id AND s.its_date BETWEEN start_date() AND end_date() AND s.node_id = specific_id()
        GROUP BY sl.article_id
        ORDER BY sl.article_id;      

SET  @start_date = "2019-03-01", @end_date = "2019-05-31", @zip_region = 11;
SELECT ol.article_id, variance(ol.quantity) as var FROM orderlines as ol, orders as o, customers as c
WHERE o.id = ol.transaction_id AND o.customer_id = c.id AND c.zip_region = zip_region() AND o.its_date BETWEEN start_date() AND end_date()
		GROUP BY ol.article_id
        ORDER BY ol.article_id;        

SET  @start_date = "2019-03-01", @end_date = "2019-05-29", @specific_id = 1;
SELECT sl.article_id, sum(sl.quantity) as quantity_sold FROM salelines as sl, sales as s
WHERE s.id = sl.transaction_id AND s.its_date BETWEEN start_date() AND end_date() AND s.node_id = specific_id()
        GROUP BY sl.article_id
        ORDER BY sl.article_id;    

SET  @start_date = "2019-03-01", @end_date = "2019-05-31", @specific_id = 1001;
SELECT ol.article_id, variance(ol.quantity) as var FROM customers as c, orders as o, orderlines as ol
WHERE c.id = o.customer_id  AND o.id = ol.transaction_id AND c.fc = @specific_id AND o.its_date BETWEEN start_date() AND end_date()
GROUP BY ol.article_id
ORDER BY ol.article_id;






