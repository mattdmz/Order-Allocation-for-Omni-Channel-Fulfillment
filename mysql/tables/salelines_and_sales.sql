#create table salelines (WITHOUT primary or secondary key)
CREATE TABLE masterarbeit.salelines2(
	transaction_id BIGINT NOT NULL,
    node_id INT NOT NULL,
	its_date date,
	its_time time,
    article_id INT NOT NULL,
    quantity SMALLINT NOT NULL
    );

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/salelines_up_to_20190316.csv'
INTO TABLE masterarbeit.salelines2
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
    IGNORE 1 LINES;
    
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/salelines_up_to_20190331.csv'
INTO TABLE masterarbeit.salelines2
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
    IGNORE 1 LINES;
    
#create table sales
CREATE TABLE masterarbeit.sales2(
	id BIGINT,
    node_id INT,
	its_date date,
	its_time time,
    price decimal(34,2),
    volume decimal(37,0),
    weight decimal(37,0)
    );

#insert new saleslines into table sales
INSERT INTO masterarbeit.sales2
SELECT sl.transaction_id as id, sl.node_id, sl.its_date, sl.its_time,
		sum(a.price * sl.quantity) as price, sum(a.volume * sl.quantity) as volume, sum(a.weight * sl.quantity) as weight
		FROM masterarbeit.salelines2 as sl, masterarbeit.articles as a
		WHERE sl.article_id = a.id
        AND sl.its_date <= "2019-03-10"
		GROUP BY sl.transaction_id;
        
INSERT INTO masterarbeit.sales2
SELECT sl.transaction_id as id, sl.node_id, sl.its_date, sl.its_time,
		sum(a.price * sl.quantity) as price, sum(a.volume * sl.quantity) as volume, sum(a.weight * sl.quantity) as weight
		FROM masterarbeit.salelines2 as sl, masterarbeit.articles as a
		WHERE sl.article_id = a.id
        AND sl.its_date > "2019-03-10"
        AND sl.its_date <= "2019-03-20"
		GROUP BY sl.transaction_id;
        
INSERT INTO masterarbeit.sales2
SELECT sl.transaction_id as id, sl.node_id, sl.its_date, sl.its_time,
		sum(a.price * sl.quantity) as price, sum(a.volume * sl.quantity) as volume, sum(a.weight * sl.quantity) as weight
		FROM masterarbeit.salelines2 as sl, masterarbeit.articles as a
		WHERE sl.article_id = a.id
        AND sl.its_date > "2019-03-20"
        AND sl.its_date <= "2019-03-31"
		GROUP BY sl.transaction_id;

#add primary keys to sales
ALTER TABLE masterarbeit.sales2
	  ADD PRIMARY KEY (id);

# drop unnecessary salelines
DELETE FROM masterarbeit.salelines2 WHERE its_date > '2019-03-31';
      
#drop redundant columns in salelines
ALTER TABLE masterarbeit.salelines2
      DROP COLUMN its_date;
ALTER TABLE masterarbeit.salelines2
      DROP COLUMN its_time;
ALTER TABLE masterarbeit.salelines2
	  DROP COLUMN node_id;
      
#add foreign keys to salelines
ALTER TABLE masterarbeit.salelines2
	  ADD FOREIGN KEY (transaction_id) REFERENCES sales2(id),
	  ADD FOREIGN KEY (article_id) REFERENCES articles(id);
      
ALTER TABLE masterarbeit.sales2
	ADD COLUMN its_datetime datetime;
    
UPDATE masterarbeit.sales2
	SET its_datetime = cast(its_date as datetime) + cast(its_time as time);


    

    
