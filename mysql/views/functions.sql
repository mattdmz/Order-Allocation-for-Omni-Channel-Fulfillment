
DROP FUNCTION IF EXISTS masterarbeit.start_date;
CREATE FUNCTION masterarbeit.start_date() 
	RETURNS DATE 
    DETERMINISTIC NO SQL 
    RETURN @start_date;

DROP FUNCTION IF EXISTS masterarbeit.end_date;
CREATE FUNCTION masterarbeit.end_date() 
	RETURNS DATE 
    DETERMINISTIC NO SQL 
    RETURN @end_date;

DROP FUNCTION IF EXISTS masterarbeit.start_datetime;
CREATE FUNCTION masterarbeit.start_datetime() 
	RETURNS DATETIME 
    DETERMINISTIC NO SQL 
    RETURN @start_datetime;
    
DROP FUNCTION IF EXISTS masterarbeit.end_datetime;
CREATE FUNCTION masterarbeit.end_datetime() 
	RETURNS DATETIME 
    DETERMINISTIC NO SQL 
    RETURN @end_datetime;

DROP FUNCTION IF EXISTS masterarbeit.specific_date;
CREATE FUNCTION masterarbeit.specific_date() 
	RETURNS DATE 
    DETERMINISTIC NO SQL 
    RETURN @specific_date;

DROP FUNCTION IF EXISTS masterarbeit.specific_id;    
CREATE FUNCTION masterarbeit.specific_id() 
	RETURNS INTEGER 
    DETERMINISTIC NO SQL 
    RETURN @specific_id;
    
DROP FUNCTION IF EXISTS masterarbeit.node_type;    
CREATE FUNCTION masterarbeit.node_type() 
	RETURNS INTEGER 
    DETERMINISTIC NO SQL 
    RETURN @node_type;

DROP FUNCTION IF EXISTS masterarbeit.fc_id;    
CREATE FUNCTION masterarbeit.fc_id() 
	RETURNS INTEGER 
    DETERMINISTIC NO SQL 
    RETURN @fc_id;
    
DROP FUNCTION IF EXISTS masterarbeit.zip_region;
CREATE FUNCTION masterarbeit.zip_region() 
	RETURNS INTEGER
    DETERMINISTIC NO SQL 
    RETURN  @zip_region;



    

