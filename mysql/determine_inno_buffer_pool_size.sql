
SHOW VARIABLES LIKE 'innodb%';

SELECT CEILING(Total_InnoDB_Bytes*1.6/POWER(1024,3)) RIBPS FROM
(SELECT SUM(data_length+index_length) Total_InnoDB_Bytes
FROM information_schema.tables WHERE engine='InnoDB') A;

SET GLOBAL innodb_buffer_pool_size=5368709120;
SHOW STATUS WHERE Variable_name='InnoDB_buffer_pool_resize_status';

