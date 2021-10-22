#all views regarding nodes

USE masterarbeit;

#select all nodes
CREATE OR REPLACE VIEW masterarbeit.table_with_all_nodes AS
SELECT * FROM nodes as n
		 ORDER BY n.id ASC;
         
#select all nodes (stores and fcs) in fc region
CREATE OR REPLACE VIEW masterarbeit.table_with_all_nodes_in_fc_region AS
SELECT * FROM nodes as n
		 WHERE n.fc = fc_id()
		 ORDER BY n.id ASC;
         
#select all stores
CREATE OR REPLACE VIEW masterarbeit.table_with_all_stores AS
SELECT * FROM nodes as n
		 WHERE n.node_type = 0 or n.node_type = 1  #store with or without delivery capacities
		 ORDER BY n.id ASC;
		
#filter stores supplied by fc
CREATE OR REPLACE VIEW masterarbeit.table_with_all_stores_supplied_by_fc AS
SELECT * FROM nodes as n
		 WHERE n.node_type = 0 or n.node_type = 1  #store with or without delivery capacities
         AND n.fc = fc_id() #supplied by fc with fc_id
		 ORDER BY n.id ASC;        
         
#select all fcs
CREATE OR REPLACE VIEW masterarbeit.table_with_all_fcs AS
SELECT * FROM nodes as n
		 WHERE n.node_type = 2 #fc
		 ORDER BY n.id ASC;
    
#select all nodes from node_tpye in zip_region
CREATE OR REPLACE VIEW masterarbeit.table_with_nodes_of_type_in_zip_region AS
SELECT * FROM masterarbeit.nodes as n
	WHERE n.node_type = node_type() AND get_zip_region(n.zip) = zip_region();
    
    