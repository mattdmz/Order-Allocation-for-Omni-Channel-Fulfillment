#create table salelines (WITHOUT primary or secondary key)
CREATE TABLE masterarbeit.salelines(
	transaction_id BIGINT NOT NULL,
    node_id INT NOT NULL,
	its_date date,
	its_time time,
    article_id INT NOT NULL,
    quantity SMALLINT NOT NULL
    );

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/salelines_up_to_20190316.csv'
INTO TABLE masterarbeit.salelines
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
    IGNORE 1 LINES;
    
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/salelines_up_to_20190331.csv'
INTO TABLE masterarbeit.salelines
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
    IGNORE 1 LINES;
    
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/salelines_up_to_20190415.csv'
INTO TABLE masterarbeit.salelines
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
    IGNORE 1 LINES;
  
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/salelines_up_to_20190430.csv'
INTO TABLE masterarbeit.salelines
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
    IGNORE 1 LINES;
 
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/salelines_up_to_20190516.csv'
INTO TABLE masterarbeit.salelines
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
    IGNORE 1 LINES;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/salelines_up_to_20190531.csv'
INTO TABLE masterarbeit.salelines
	FIELDS TERMINATED BY ';'
           OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY'\n'
    IGNORE 1 LINES;
    
#create table sales from salelines
CREATE TABLE masterarbeit.sales
SELECT sl.transaction_id as id, sl.node_id, sl.its_date, sl.its_time,
		sum(a.price * sl.quantity) as price, sum(a.volume * sl.quantity) as volume, sum(a.weight * sl.quantity) as weight
		FROM salelines as sl, articles as a
		WHERE sl.article_id = a.id
		GROUP BY sl.transaction_id;
        
#insert new saleslines into table sales
#INSERT INTO masterarbeit.sales
#SELECT sl.transaction_id as id, sl.node_id, sl.its_date, sl.its_time,
		#sum(a.price * sl.quantity) as price, sum(a.volume * sl.quantity) as volume, sum(a.weight * sl.quantity) as weight
		#FROM salelines as sl, articles as a
		#WHERE sl.article_id = a.id
		#GROUP BY sl.transaction_id;

#add primary keys to sales
ALTER TABLE masterarbeit.sales
	  ADD PRIMARY KEY (id);
      
#drop redundant columns in salelines
ALTER TABLE masterarbeit.salelines
	  DROP COLUMN node_id,
      DROP COLUMN its_date,
      DROP COLUMN its_time;
      
#add foreign keys to salelines
ALTER TABLE masterarbeit.salelines
	  ADD FOREIGN KEY (transaction_id) REFERENCES sales(id),
	  ADD FOREIGN KEY (article_id) REFERENCES articles(id);





    

    
