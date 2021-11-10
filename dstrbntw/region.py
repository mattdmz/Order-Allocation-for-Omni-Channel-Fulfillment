
###############################################################################################

'''This file contains the class Region and its subclass Regions.'''

###############################################################################################


from copy import deepcopy
from datetime import date, datetime
from mysql.connector.errors import DatabaseError
from numpy import array, zeros, sum
from pandas import DataFrame

from allocation.constants import RULE_BASED
from database.connector import Database
from database.constants import FC, ID, ORDERS, ORDERLINES, SALES, SALELINES
from database.views import Lines_of_Transaction, Transactions_in_Period
from dstrbntw.abcanalysis import Abc_Analysis
from dstrbntw.articles import Article, Articles
from dstrbntw.constants import *
from dstrbntw.customers import Customers
from dstrbntw.demand import Demand
from dstrbntw.errors import InitStockError, ImportTransactionsError
from dstrbntw.nodes import Node, Nodes
from dstrbntw.stock import Stock
from parameters import EXP_INITIAL_STOCK, FIX_LEVEL, LISTING_LIMIT, ORDER_PROCESSING_END, RPL_CYCLE_DURATION, STOCK_SEED
from protocols.constants import ALLOC_ARR, NUMBER_OF_LINES, NUMBER_OF_ORDERS, \
                                POTENTIAL_OFFLINE_REVENUE, POTENTIAL_ONLINE_REVENUE
from protocols.results import init_order_evaluation
from transactions.orders import Order, Orders
from transactions.sales import Sale, Sales
from utilities.datetime import delivered_on
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

        return zeros(shape=(len(self.articles.dict), len(self.nodes.dict)), dtype=int)

    def determine_demand(self, df:DataFrame) -> array:

        '''Transforms demand DataFrame to numpy array.'''

        arr = zeros(shape=(len(self.articles.dict), len(self.nodes.dict)))
    
        for node in self.nodes.dict.values():
            node:Node

            for article in self.articles.dict.values():
                article:Article

                # move value to numpy array and index with arrays
                arr[article.index, node.index] = df.loc[article.id, str(node.fc)]

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
                    if node.abc_analysis_demand.result[article.index] >= LISTING_LIMIT[node.node_type]:
                        
                        # calculate and set reorder and target level
                        self.stock.set_calculated_dispo_levels(article.index, node.index, node.abc_analysis_demand.categorize(article.index))

            # set start level
            if STOCK_SEED == PREDEFINED_LEVEL:
                self.stock.current_level = self.stock.set_start_level(self.nodes.start_stock_rates, self.articles.start_stock_rates)
            else:
                self.stock.current_level = self.stock.set_start_level()

            if STOCK_SEED == FIX_LEVEL:
                self.stock.target_level = self.stock.set_fix_stock_level()

            # determine which articles are in the assortement
            self.stock.is_listed = self.stock.current_level > 0

            if EXP_INITIAL_STOCK:
                self.stock.export(self.id)

        except Exception as err:

            # raise customized error message as mid level error and include err as lower level
            raise InitStockError(err.__class__.__name__, err)

    def define_delivery_day(self, current_time:datetime) -> None:

        '''Defines the next days orders will be processed and delivered.'''

        for node in self.nodes.dict.values():
            node:Node
            
            node.delivery.day = delivered_on(current_time, node.node_type)

    def imp_orders(self, start:datetime, end:datetime) -> list:

        '''Imports input data of orders from database.'''

        # create list of orders
        orders = []

        try:
            # connect to db and get cursor
            with Database() as db:

                # fetch data and return as list of objects (database to fetch from, view to use, (parameters to apply on view), object to store selected rows in)
                data = Transactions_in_Period(db, ORDERS, columns="*", start=start, end=end, fc=self.id).data
                orders.extend(create_obj_list(data, Order, self.customers))
                del data

                if orders is None:
                    raise ImportTransactionsError(ORDERS, start, end)

                # for each transaction, import its lines
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
                    
                # fetch data and return as list of objects (database to fetch from, view to use, (parameters to apply on view), object to store selected rows in)
                data = Transactions_in_Period(db, SALES, columns="*", start=start, end=end, fc=self.id).data
                sales = create_obj_list(data, Sale, self.nodes)
                del data

                if sales is None:
                    raise ImportTransactionsError(SALES, start, end)

                # for each transaction, import its lines
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

        orders = Orders()
        orders.list = self.imp_orders(start, end)
        
        sales = Sales()
        sales.list = self.imp_sales(start, end)

        self.orders.list.extend(orders.list)
        self.sales.list.extend(sales.list)

        # evaluate imported transactions for results protocol
        imported_trsct_eval = { NUMBER_OF_ORDERS: len(orders.list),
                                POTENTIAL_ONLINE_REVENUE: sum(orders.potential_revenue),
                                NUMBER_OF_LINES: sales.number_of_lines,
                                POTENTIAL_OFFLINE_REVENUE: sales.potential_revenue
        }

        return imported_trsct_eval

    def start_allocation(self, allocator, current_time:datetime) -> dict:

        ''' Returns an allocation made with the allocator passed (rule-based allocator or an optimizer).'''
        
        # start allocation with the allocator passed (rule-based allocator or an optimizer)
        return allocator(self, current_time).allocation

    def determine_not_allocated_orders(self, allocation:dict, current_time:datetime) -> DataFrame:

        ''' Returns a DataFrame containing the evaluation of not allocated orders.
            Schedules the allocation retry if the current allocation attempt failed.'''

        not_allocated_orders_evaluation = DataFrame(columns=init_order_evaluation(0).keys())

        for node_index, order in zip(allocation[ALLOC_ARR], self.orders.list):
            node_index:int
            order:Order

            # check if allocation failed and if there is another day left to retry
            if (node_index < 0 and order.allocation_retried) or (node_index < 0 and current_time.date() == ORDER_PROCESSING_END):

                # protocol allocation failure reason
                order.failure = node_index
                
                # allocation retried and failed, protocol order as not allocated with the failure reason
                order_evaluation = order.protocol(self.id, datetime(2099, 1, 1, 0, 0))
                not_allocated_orders_evaluation = not_allocated_orders_evaluation.append(order_evaluation, ignore_index=True)

            elif node_index < 0 and not order.allocation_retried:                                                                         

                # set order on allocation retry list
                self.orders.allocation_retry(order)

        return not_allocated_orders_evaluation if len(not_allocated_orders_evaluation.index) > 0 else None

    def determine_remainig_orders(self) -> DataFrame:

        ''' Returns a DataFrame containing the evaluation of schueduled orders which were not processed.'''

        remainig_orders_evaluation = DataFrame(columns=init_order_evaluation(0).keys())

        for order in self.orders.list:
            order:Order

            if order.allocated_node == None:
                
                # allocation retried and failed, protocol order as not allocated with the failure reason
                remaining_orders_evaluation = remaining_orders_evaluation.append(order.protocol(self.id, None), ignore_index=True)

        return remainig_orders_evaluation if len(remainig_orders_evaluation.index) > 0 else None

    def nodes_with_batches_to_process(self, current_time:datetime) -> list:

        ''' Checks if there are order-batches to process and returns them.
            Sets order acceptance status to false if its order execution capacities are exhausted or cut_off_time is reached.'''

        nodes_with_batches_to_process = []

        for node in self.nodes.dict.values():
            node:Node

            # check if starting time for order processing and delivery for all allocated orders and nodes was reached.
            if current_time >= node.delivery.processing_start():
                
                # save node where a batch is to process
                nodes_with_batches_to_process.append(node)

                if node.accepting_orders:

                    # declare node as not accepting orders anymore on current day
                    node.delivery_restarts_tomorrow(current_time)
                    node.set_order_acceptance_status(False)

        return nodes_with_batches_to_process if nodes_with_batches_to_process != [] else None

    def check_processability(self, nodes_with_batches_to_process:list, current_time:datetime) -> None:

        ''' Stores True or False as order attribute if order is processable or not. 
            Removes order form delivery tour if not processable and reschedule tour
            without the delivery of the none processable order.'''

        not_processable_orders = []

        for node in nodes_with_batches_to_process:
            node:Node
            
            batch_to_process = node.delivery.batches[len(node.delivery.batches) -1]

            for order in batch_to_process.orders:
                order:Order

                # check if stock is available to process all orders
                for line in order.lines:
                    line:Order.Line

                    processable = self.stock.processability(line.article.index, order.allocated_node.index, line.quantity)

                    if not processable:

                        # Order can not be processed and delivered as there is not enough stock available.
                        not_processable_orders.append(order)
                        break
                
                order.processable = processable

        for order in not_processable_orders:

            # Order remains in the list of orders to be allocated and is allocated at a different node during the next allocation cycle.

            # remove order from delivery tour
            order.allocated_node.delivery.remove_order(order)

            # rebuild delivery routes if there is orders remaining to deliver
            if len(order.allocated_node.delivery.orders_to_deliver) > 1:
                
                # rebuild the routes
                order.allocated_node.delivery.build_routes()

                # reschedule delivery to get the correct delivery times of the new route without the order that could not be processed
                order.allocated_node.delivery.create_batches(current_time)

            # reset allocation
            order.allocated_node = None
            order.allocation_time = None

    def process_orders(self, nodes_with_batches_to_process:list, current_time:datetime) -> DataFrame:

        ''' Processes batches of orders and returns evaluation.
            Resets delivery objet if all batches of node were processed.'''

        #init DataFrame to store results
        processing_evaluation = DataFrame(columns=init_order_evaluation(0).keys())

        for node in nodes_with_batches_to_process:
            node:Node

            batch = node.delivery.batch_to_process()

            if batch is not None:

                # reset delivery objet if all batches of node were processed
                if len(node.delivery.batches) == 0:
                    node.reset_delivery() 
            
                # compute delivery costs of tour and divide by number of orders to deliver
                delivery_costs = batch.delivery_costs / len(batch.orders)
                delivery_duration = batch.delivery_duration / len(batch.orders) 

                # process orders marked as processable
                for order in batch.orders:
                    order:Order

                    if order.processable:

                        # consume stock            
                        for line in order.lines:
                            line:Order.Line

                            self.stock.cancel_reservation(line.article.index, order.allocated_node.index, line.quantity)
                            self.stock.consume(line.article.index, order.allocated_node.index, line.quantity)
                        
                        order_evaluation = order.protocol(self.id, current_time, delivery_costs=delivery_costs, delivery_duration=delivery_duration, \
                                                        diminuished_stock_value=order.pieces * order.allocated_node.stock_holding_rate)
                        processing_evaluation = processing_evaluation.append(order_evaluation, ignore_index=True)                                                            

        return processing_evaluation

    def process_batches(self, current_time:datetime) -> DataFrame:

        '''returns the evaluation of the batches (orders) processed'''

        #check if order processing and delivery must be executed
        nodes_with_batches_to_process = self.nodes_with_batches_to_process(current_time)

        if nodes_with_batches_to_process is not None:
            
            # check if stock reserved is still available
            self.check_processability(nodes_with_batches_to_process, current_time)

            # calculate revenue generated from orders and subtract order processing costs
            return self.process_orders(nodes_with_batches_to_process, current_time)

        return None

    def process_sales(self, current_time:datetime, region_id:int) -> DataFrame:

        ''' Returns a DataFrame with how many salelines could be closed and how much revenue was generated.'''

        return self.sales.process(current_time, region_id)

    def transform_allocation_array(self, allocation:dict) -> dict:

        ''' Returns the allocation dict with the allocation array filled with the interpretable 
            allocated node ids instead of unreadable indexes for export purposses.'''

        alloc_arr_of_ids = []

        for order_index, node_index in enumerate(allocation[ALLOC_ARR]):

            try:
                # get the node id if the order's allocation was successful
                alloc_arr_of_ids.append(f'{self.orders.list[order_index].id}: {self.nodes.__getattr__(ID, index=node_index)}')
            
            except KeyError:
                # set the feedback (negative node_index) the order's allocation was successful
                alloc_arr_of_ids.append(f'{self.orders.list[order_index].id}: {node_index}')

        # prepare exportable dict
        exportable_alloc = deepcopy(allocation)
        exportable_alloc[ALLOC_ARR] = alloc_arr_of_ids

        return exportable_alloc

    def change_order_acceptance_status(self, status:bool) -> None:

        '''Sets the order acceptance status of all nodes to the passed status.'''

        for node in self.nodes.dict.values():
            node:Node
            
            node.set_order_acceptance_status(status)

    def determine_out_of_stock_situations(self) -> int:

        '''Determines the number of articles out of stock in the whole region.'''

        return sum((self.stock.current_level == 0) * self.stock.is_listed)

    def calc_stock_holding_costs(self) -> float:
        
        ''' Returns stock holding costs for this day.'''
        
        return self.stock.holding_costs

    def check_for_replenishments(self,  current_time:datetime) -> int:

        '''Returns the number of replenishments carried out.
            Replenishmes only on replenishment day, which is claculated following the RPL_CYCLE_DURATION.'''

        if current_time.date().isoweekday() % RPL_CYCLE_DURATION  == 0:
            return self.stock.replenish()
        else:
            
            return 0

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
