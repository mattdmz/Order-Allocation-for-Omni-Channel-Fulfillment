
###############################################################################################

'''This file contains the class Region and its subclass Regions.'''

###############################################################################################


from datetime import date, datetime, time, timedelta
from mysql.connector.errors import DatabaseError
from numpy import array, zeros
from pandas import DataFrame

from allocation.constants import RULE_BASED
from database.connector import Database
from database.constants import FC, ID, ORDERS, ORDERLINES, SALES, SALELINES
from database.views import Transactions_on_Day, Lines_of_Transaction
from dstrbntw.abcanalysis import Abc_Analysis
from dstrbntw.articles import Article, Articles
from dstrbntw.constants import *
from dstrbntw.customers import Customers
from dstrbntw.demand import Demand
from dstrbntw.errors import InitStockError, ImportTransactionsError
from dstrbntw.nodes import Node, Nodes
from dstrbntw.stock import Stock
from parameters import FIX_LEVEL, LISTING_LIMIT, STOCK_SEED
from protocols.constants import ALLOC_ARR, ALLOCATION_DATETIME
from protocols.results import init_order_evaluation
from transactions.orders import Order, Orders
from transactions.sales import Sale, Sales
from utilities.datetime import processing_day
from utilities.general import create_obj_list


class Region:

    def __init__(self) -> None:
        
        ''' Inits region's articles, customers, nodes, orders, sales and demand objects.
            Data'''

        self.articles = Articles()
        self.customers = Customers()
        self.nodes = Nodes()
        self.orders = Orders()
        self.sales = Sales()
        self.demand = Demand()
    
    @property
    def number_of_orders_to_process(self) -> int:

        '''Returns the number of orders which are to be processed in the region.'''

        return len(self.orders.list)

    def imp(self, db:Database, region_id:int, start:date=None, end:date=None) -> None:
        
        ''' Imports article, customer and node data to feed the region model.'''

        # assign id
        self.id = region_id

        # import data to model region's elements
        self.articles.imp(db, start=start, end=end, region_id=region_id)
        self.customers.imp(db, region_id, start=start, end=end)
        self.nodes.imp(db, region_column=FC, region_id=region_id)

    def init_twodim_array(self) -> array:

        '''Returns a twodimenional np_array of zeros with the shape array(number_of_articles, number_of_nodes).'''

        return zeros(shape=(len(self.articles.dict), len(self.nodes.dict)))

    def determine_demand(self, df:DataFrame) -> array:

        '''Transforms demand DataFrame to numpy array.'''

        arr = zeros(shape=(len(self.articles.dict), len(self.nodes.dict)))
    
        for node in self.nodes.dict.values():
            node:Node

            for article in self.articles.dict.values():
                article:Article

                # move value to numpy array and index with arrays
                arr[article.index, node.index] = df.loc[article.id, str(node.zip_region)]

        return arr

    def store_demand(self, sum:DataFrame, avg:DataFrame, var:DataFrame) -> None:

        '''Determines and stores demand at all nodes in region for all articles sold in region.'''

        self.demand.store(self.determine_demand(sum), self.determine_demand(avg), self.determine_demand(var))

    def analyse_demand(self) -> None:

        '''Analyses demand for all nodes in region.'''

        indexes = array(list(range(0, len(self.articles.dict.keys()))))

        for node in self.nodes.dict.values():
            node:Node

            abc_analysis_demand = Abc_Analysis(node.index, indexes, self.demand.sum[:, node.index], multidimensional=False)
            node.store_demand_analysis(abc_analysis_demand)

    def init_stock(self) -> None:

        ''' Inits stock.
            Calculates and sets reorder and start level stock of each each article to be listed at each node.
            Determines and sets also start level of stock. '''
        
        try:

            self.stock = Stock(self.init_twodim_array(), self.nodes.stock_holding_rates, self.demand)

            for node in self.nodes.dict.values():
                node:Node

                for article in self.articles.dict.values():
                    article:Article

                    # check if article should be added to the assortment of this particular node
                    if node.abc_analysis_demand.result[article.index] <= LISTING_LIMIT[node.node_type]:
                        
                        # calculate and set reorder and target level
                        self.stock.set_calculated_dispo_levels(article.index, node.index, node.abc_analysis_demand.categorize(article.index))

            self.stock.current_level = self.stock.set_start_level()

            if STOCK_SEED == FIX_LEVEL:

                self.stock.target_level = self.stock.set_fix_stock_level()

        except Exception as err:

            # raise customized error message as mid level error and include err as lower level
            raise InitStockError(err.__class__.__name__, err)

    def imp_orders(self, start:datetime, end:datetime) -> list:

        '''Imports input data of orders from database.'''

        #create list of orders
        orders = []

        try:
            #connect to db and get cursor
            with Database() as db:

                # if day is a monday import also sunday's orders
                if start.isoweekday() == 1:
                    
                    #fetch data and return as list of objects (database to fetch from, view to use, (parameters to apply on view), object to store selected rows in)
                    data = Transactions_on_Day(db, ORDERS, start.date() - timedelta(days=1), columns="*", start_time=time(0, 0, 1), end_time=time(23, 59, 59), fc=self.id).data
                    orders = create_obj_list(data, Order, self.customers)

                #fetch data and return as list of objects (database to fetch from, view to use, (parameters to apply on view), object to store selected rows in)
                data = Transactions_on_Day(db, ORDERS, start.date(), columns="*", start_time=start.time(), end_time=end.time(), fc=self.id).data
                orders.extend(create_obj_list(data, Order, self.customers))
                del data

                if orders is None:
                    raise ImportTransactionsError(ORDERS, start, end)

                #for each transaction, import its lines
                for order in orders:
                    order:Order

                    data = Lines_of_Transaction(db, columns="*", table=ORDERLINES, id=order.id).data
                    order.lines = create_obj_list(data, Order.Line, self.articles)

                    if order.lines == []:
                        raise ImportTransactionsError(ORDERLINES, start, end)

            return orders

        except ConnectionError as err:
            raise ImportTransactionsError(ORDERS, start, end, err_name=ConnectionError.__name__, err=err)
        
        except DatabaseError as err:     
            raise ImportTransactionsError(ORDERS, start, end, err_name=ConnectionError.__name__, err=err)

    def imp_sales(self, start:datetime, end:datetime) -> list:

        '''Imports input data of sales from database.'''

        #create list of sales
        sales = []

        try:
            #connect to db and get cursor
            with Database() as db:

                # if day is a monday import also sunday's orders
                if start.isoweekday() == 1:
                    
                    #fetch data and return as list of objects (database to fetch from, view to use, (parameters to apply on view), object to store selected rows in)
                    data = Transactions_on_Day(db, SALES, start.date() - timedelta(days=1), columns="*", start_time=time(0, 0, 1), end_time=time(23, 59, 59), fc=self.id).data
                    sales = create_obj_list(data, Sale, self.nodes)
            
                #fetch data and return as list of objects (database to fetch from, view to use, (parameters to apply on view), object to store selected rows in)
                data = Transactions_on_Day(db, SALES, start.date(), columns="*", start_time=start.time(), end_time=end.time(), fc=self.id).data
                sales.extend(create_obj_list(data, Sale, self.nodes))
                del data

                if sales is None:
                    raise ImportTransactionsError(SALES, start, end)

                #for each transaction, import its lines
                for sale in sales:
                    sale:Sale

                    data = Lines_of_Transaction(db, columns="*", table=SALELINES, id=sale.id).data
                    sale.lines = create_obj_list(data, Sale.Line, self.articles)

                    if sale.lines == []:
                        raise ImportTransactionsError(SALELINES, start, end)

            return sales

        except ConnectionError as err:
            raise ImportTransactionsError(SALES, start, end, err_name=ConnectionError.__name__, err=err)
        
        except DatabaseError as err:     
            raise ImportTransactionsError(SALES, start, end, end=end, err_name=ConnectionError.__name__, err=err)

    def imp_new_transactions(self, start:datetime, end:datetime) -> None:

        '''Imports sales and orders of the last allocation period.'''

        self.orders.list.extend(self.imp_orders(start, end))
        self.sales.list.extend(self.imp_sales(start, end))

    def start_allocation(self, allocator, current_time:datetime, cut_off_time:datetime, alloc_func) -> dict:

        ''' Returns an allocation made with the allocator passed (rule-based allocator or an optimizer).'''
        
        # start allocation with the allocator passed (rule-based allocator or an optimizer)
        return allocator(self, current_time, cut_off_time, alloc_func).allocation

    def determine_not_allocated_orders(self, allocation:dict) -> DataFrame:

        ''' Returns a DataFrame containing the evaluation of not allocated orders.
            Schedules the allocation retry if the current allocation attempt failed.'''

        not_allocated_orders_evaluation = DataFrame(columns=init_order_evaluation(0).keys())

        for node_index, order in zip(allocation[ALLOC_ARR], self.orders.list):
            node_index:int
            order:Order

            #check if allocation failed
            if node_index < 0:
                
                order_evaluation = order.protocol(self.id, allocation[ALLOCATION_DATETIME], failure=node_index)
                not_allocated_orders_evaluation = not_allocated_orders_evaluation.append(order_evaluation, ignore_index=True)
                                                                                         
                self.orders.allocation_retry(order)

        return not_allocated_orders_evaluation if len(not_allocated_orders_evaluation) > 0 else None

    def batches_to_process(self, current_time:datetime) -> dict:

        ''' Checks if there are order-batches to process and returns them.
            Sets order acceptance status to false if its order execution capacities are exhausted or cut_off_time is reached.'''

        batches_to_process = {}

        for node in self.nodes.dict.values():
            node:Node

            #check if starting time for order processing and delivery for all allocated orders and nodes was reached.
            if current_time >= node.delivery.processing_start():
                batches_to_process[node] = node.delivery.batch_to_process()

        return batches_to_process if batches_to_process != {} else None

    def check_processability(self, batches:dict, processing_day:date) -> None:

        ''' Stores True or False as order attribute if order is processable or not. 
            Removes order form delivery tour if not processable and reschedule tour
            without the delivery of the none processable order.'''

        for batch in batches.values():

            for order in batch.orders:
                order:Order

                # check if stock is available to process all orders
                for line in order.lines:
                    line:Order.Line

                    processable = self.stock.processability(line.article.index, order.allocated_node.index, line.quantity)

                    if not processable:

                        # Order can not be processed and delivered as there is not enough stock available.
                        # Order remains in the list of orders to be allocated and is allocated at a different node during the
                        # next allocation cycle.

                        # remove order from delivery tour
                        order.allocated_node.delivery.remove_order(order)

                        # reschedule delivery to get the correct delivery times of the new route without the order that could not be processed
                        order.allocated_node.delivery.schedule_batches(processing_day)

                        # reset allocation
                        order.allocated_node = None
                        order.allocation_time = None

                        break
                
                order.processable = processable

    def process_batches(self, batches:dict, current_time:datetime, cut_off_time:datetime) -> DataFrame:

        '''Processes batches of orders and returns evaluation.'''

        #init DataFrame to store results
        processing_evaluation = DataFrame(columns=init_order_evaluation(0).keys())

        for batch in batches.values():
            
            # compute delivery costs of tour and divide by number of orders to deliver
            delivery_costs = batch.delivery_costs / len(batch.orders)

            # process orders marked as processable
            for order in batch.orders:
                order:Order

                if order.processable:

                    # consume stock            
                    for line in order.lines:
                        line:Order.Line

                        stock_holding_costs = sum(self.stock.held_for_order(order) * self.nodes.stock_holding_rates)
                        self.stock.cancel_reservation(line.article.index, order.allocated_node.index, line.quantity)
                        self.stock.consume(line.article.index, order.allocated_node.index, line.quantity)
                    
                    processing_evaluation = processing_evaluation.append(order.protocol(self.id, current_time, cut_off_time=cut_off_time, \
                                                                            delivery_costs=delivery_costs, stock_holding_costs=stock_holding_costs), ignore_index=True)
                                                                            

        return processing_evaluation

    def process_orders(self, current_time:datetime, cut_off_time:datetime) -> DataFrame:

        #check if order processing and delivery must be executed
        batches_to_process = self.batches_to_process(current_time)

        if batches_to_process is not None:
            
            # check if stock reserved is still available
            self.check_processability(batches_to_process, processing_day(current_time, cut_off_time))

            # calculate revenue generated from orders and subtract order processing costs
            return self.process_batches(batches_to_process, current_time, cut_off_time)

        return None

    def process_sales(self, current_time:datetime, region_id:int) -> DataFrame:

        ''' Returns a DataFrame with how many salelines could be closed and how much revenue was generated.'''

        return self.sales.process(current_time, region_id)

    def transform_allocation_array(self, allocation:dict) -> dict:

        ''' Returns the allocation dict with the allocation array filled with the interpretable 
            allocated node ids instead of unreadable indexes for export purposses.'''

        alloc_arr_of_ids = []

        for node_index in allocation[ALLOC_ARR]:

            try:
                # get the node id if the order's allocation was successful
                alloc_arr_of_ids.append(self.nodes.__getattr__(ID, index=node_index))
            
            except KeyError:
                # set the feedback (negative node_index) the order's allocation was successful
                alloc_arr_of_ids.append(node_index)

        allocation[ALLOC_ARR] = alloc_arr_of_ids

        return allocation

    def change_order_acceptance_status(self, status:bool)-> None:
            
            # stop accepting orders at nodes for this day
            self.nodes.change_order_acceptance_status(status)
            
    def calc_stock_holding_costs(self) -> None:
        
        ''' Returns stock holding costs for this day.'''
        
        return self.stock.holding_costs

    def check_for_replenishments(self) -> int:

        '''Returns the number of replenishments carried out.'''
        
        return self.stock.replenish()

    def reschedule_allocation_of_unallocated_orders(self) -> None:

        '''Reschedules allocation for unallocated orders.'''
        
        self.orders.reschedule_unallocated()

    def terminate_allocation(self, allocation_type:str) -> None:

        ''' Clears list of orders if rulebased allocation is active and clears sales 
            which were imported for this allocation.
            Orders which could not be processed must previously be transfered to 
            self.orders.allocation_retry_needed in order to not get lost.'''

        if allocation_type == RULE_BASED:
            self.orders.clear()

        self.sales.clear()
