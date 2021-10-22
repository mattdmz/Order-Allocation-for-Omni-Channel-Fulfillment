
###############################################################################################

'''This file contains the class Region and its subclass Regions.'''

###############################################################################################


from datetime import date, datetime, time, timedelta
from mysql.connector.errors import DatabaseError
from numpy import array, zeros
from pandas import DataFrame

from allocation.constants import RULE_BASED
from allocation.evaluation import Evaluation_Model
from database.connector import Database
from database.constants import DATE, ID, FC, ORDERS, ORDERLINES, SALES, SALELINES
from database.views import Transactions_on_Day, Lines_of_Transaction
from dstrbntw.abcanalysis import Abc_Analysis
from dstrbntw.articles import Articles
from dstrbntw.constants import *
from dstrbntw.customers import Customers
from dstrbntw.demand import Demand
from dstrbntw.errors import InitDistNtwError, ImportTransactionsError
from dstrbntw.nodes import Nodes
from dstrbntw.stock import Stock
from parameters import LISTING_LIMIT, MIN_ORDERS_TO_PROCESS, REPLENISHMENT_TIME, STOCK_SEED
from transactions.orders import Order, Orders
from transactions.sales import Sale, Sales
from utilities.general import create_obj_list


class Region:

    def __init__(self) -> None:
        pass
    
    @property
    def number_of_orders_to_process(self) -> int:

        '''Returns the number of orders which are to be processed in the region.'''

        return len(self.orders.list)

    def add(self, db:Database, region_id:int, start:date=None, end:date=None) -> None:
        
        ''' Stores articles-dict.
            Creates Customers object and Imports customers data.
            Creates Nodes object and Imports nodes data.'''

        # assign id
        self.id = region_id
        
        # add region attributes
        self.articles = Articles()
        self.articles.imp(db, start=start, end=end, region_id=region_id)

        self.customers = Customers()
        self.customers.imp(db, region_id, start=start, end=end)

        self.nodes = Nodes()
        self.nodes.imp(db, region_column=FC, region_id=region_id)

        # imported later
        self.orders = Orders()
        self.sales = Sales()
        self.demand = Demand()

        # dcits to store results form timesim
        self.replenishments = {}
        self.stock_holding_costs = {}
        self.profit = {}
    
    def init_array(self, attr:str) -> array:

        '''Retunrs a np_array containing the vaule of an attribute for all nodes.'''

        arr = zeros(len(self.nodes.dict))

        for node in self.nodes.dict.values():
            arr[node.index] = getattr(node, attr)
        
        return arr

    def init_twodim_array(self) -> array:

        '''Returns a twodimenional np_array of zeros with the shape array(number_of_articles, number_of_nodes).'''

        return zeros(shape=(len(self.articles.dict), len(self.nodes.dict)))

    def determine_demand(self, df:DataFrame) -> array:

        '''Transforms demand DataFrame to numpy array.'''

        arr = zeros(shape=(len(self.articles.dict), len(self.nodes.dict)))
    
        for node in self.nodes.dict.values():
            for article in self.articles.dict.values():
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
            abc_analysis_demand = Abc_Analysis(node.index, indexes, self.demand.sum[:, node.index], multidimensional=False)
            node.store_demand_analysis(abc_analysis_demand)

    def init_stock(self) -> None:

        ''' Inits stock.
            Calculates and sets reorder and start level stock of each each article to be listed at each node.
            Determines and sets also start level of stock. '''
        
        try:

            self.stock = Stock(self.init_twodim_array(), self.init_array(STOCK_HOLDING_RATE), self.demand)

            for node in self.nodes.dict.values():
                for article in self.articles.dict.values():

                    # check if article should be added to the assortment of this particular node
                    if node.abc_analysis_demand.result[article.index] <= LISTING_LIMIT[node.node_type]:
                        
                        # calculate and set reorder and target level
                        self.stock.set_calculated_dispo_levels(article.index, node.index, node.abc_analysis_demand.categorize(article.index))

            self.stock.current_level = self.stock.set_start_level()

            if STOCK_SEED == FIX_LEVEL:

                self.stock.target_level = self.stock.set_fix_stock_level()

        except Exception as err:

            # raise customized error message as mid level error and include err as lower level
            raise InitDistNtwError(err.__class__.__name__, err)

    def init_evaluation_model(self) -> None:

        '''Inits a model to evaluate alloactions.'''

        self.evaluation_model = Evaluation_Model(self.stock.current_level, self.stock.reserved, self.stock.holding_rates, \
                                        self.init_array(TOUR_RATE), self.init_array(ROUTE_RATE))

    def imp_orders(self, start:datetime, end:datetime) -> list:

        '''Imports input data of orders from database.'''

        #create list of orders
        orders = []

        try:
            #connect to db and get cursor
            with Database() as db:
            
                #fetch data and return as list of objects (database to fetch from, view to use, (parameters to apply on view), object to store selected rows in)
                data = Transactions_on_Day(db, ORDERS, start.date(), columns="*", start_time=start.time(), end_time=end.time(), fc=self.id).data
                orders = create_obj_list(data, Order, self.customers)
                del data

                if orders is None:
                    raise ImportTransactionsError(ORDERS, start, end)

                #for each transaction, import its lines
                for order in orders:
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
            
                #fetch data and return as list of objects (database to fetch from, view to use, (parameters to apply on view), object to store selected rows in)
                data = Transactions_on_Day(db, SALES, start.date(), columns="*", start_time=start.time(), end_time=end.time(), fc=self.id).data
                sales = create_obj_list(data, Sale, self.nodes)
                del data

                if sales is None:
                    raise ImportTransactionsError(SALES, start, end)

                #for each transaction, import its lines
                for sale in sales:
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

    def prepare_allocation(self) -> None:

        ''' Inits related arrays in the evalualtion model for the upcoming allocaiton.'''

        self.evaluation_model.orders.set_possible_revenue(array(self.orders.possible_revenue))
        self.evaluation_model.supply.set_volumes(array(self.orders.volume_supplied))
        self.evaluation_model.order_processing.set_orderlines(array(self.orders.lines_to_process))

    def start_allocation(self, allocator, current_time:datetime, alloc_period:timedelta, cut_off_time:datetime, alloc_func) -> dict:

        ''' Returns an allocation made with the allocator passed (rule-based allocator or an optimizer).'''

        # prepare order allocation
        self.imp_new_transactions(current_time - alloc_period, current_time)

        if self.number_of_orders_to_process > MIN_ORDERS_TO_PROCESS:
            
            self.prepare_allocation()
        
            # start allocation with the allocator passed (rule-based allocator or an optimizer)
            allocation = allocator(self, current_time, cut_off_time, alloc_func).allocation

            # reschedule allocations for order that could not be allcated and clear list of orders
            self.orders.reschedule_allocation()

            # for rule based allocation, clear orders that were already allocated
            if allocator.__type__ == RULE_BASED:
                self.orders.clear()

            return allocation

    def batches_to_process(self, current_time:datetime) -> dict:

        ''' Checks if there are order-batches to process and returns them.
            Sets order acceptance status to false if its order execution capacities are exhausted or cut_off_time is reached.'''

        batches_to_process = {}

        for node in self.nodes.dict.values():
            #check if starting time for order processing and delivery for all allocated orders and nodes was reached.
            if current_time.time() >= node.tour.execution_start():
                batches_to_process[node] = node.tour.batch_to_process()

        return batches_to_process if batches_to_process != {} else None

    def check_processability(self, batches:dict) -> None:

        ''' Stores True or False as order attribute if order is processable or not. 
            Removes order form delivery tour if not processable and reschedule tour
            without the delivery of the none processable order.'''

        for batch in batches.items():
            for order in batch:

                # check if stock is available to process all orders
                for line in order.lines:
                    processable = self.stock.processability(line.article.index, order.allocation, line.quantity)

                    if not processable:
                        
                        # set processability
                        setattr(order, PROCESSABLE, False)

                        # Order can not be processed and delivered as there is not enough stock available.
                        # Order remains in the list of orders to be allocated and is allocated at a different node during the
                        # next allocation cycle.

                        # remove order from delivery tour
                        order.allocation.tour.remove_order[order]

                        # reset allocation
                        order.allocation = None

                        # reschedule delivery to get the correct delivery times of the new route without the order that could not be processed
                        order.allocation.tour.schedule()

                        break
                
                setattr(order, PROCESSABLE, True)

    def process_batches(self, batches:dict) -> DataFrame:

        '''Processes batches of orders and stores results.'''

        results = self.init_results_array()

        for batch in batches.items():

            delivery_costs = batch.delivery_costs / len(batch.orders)

            for order in batch:
        
                if getattr(order, PROCESSABLE):

                    # consume stock            
                    for line in order.lines:
                        self.stock.cancel_reservation(line.article.index, order.allocation.index, line.quantity)
                        self.stock.consume(line.article.index, order.allocation.index, line.quantity)

                    profit =  order.price - order.supply_costs - order.processing_costs - delivery_costs

                    # calculate revenue generated from order - supply costs - processing costs
                    result = {  ID: order.id,
                                ALLOCATION: order.allocation.id, 
                                PROFIT: profit, 
                                SUPPLY_COSTS:order.supply_costs, 
                                ORDER_PROCESSING_COSTS: order.processing_costs, 
                                DELIVERY_COSTS:delivery_costs}
                    
                    results.append(result, ignore_index=True)

        return results

    def determine_profit(self, processing_results:dict) -> float:

        '''Returns the sum of revenue from offline sales and the profit from the processing of online orders.'''

        return self.sales.collect_revenue() + sum(processing_results[PROFIT])

    def stop_accepting_orders(self) -> None:

        '''Sets order acceptance status for all nodes to False.'''

        self.nodes.deactivate_nodes()

    def actions(self, current_time:datetime, cut_off_time:datetime) -> None:

        #check if order processing and delivery must be executed
        batches_to_process = self.batches_to_process(current_time)

        if batches_to_process is not None:
            
            # check if stock reserved is still available
            self.check_processability(batches_to_process)

            # calculate revenue generated from orders and subtract order processing costs
            processing_results = self.process_batches(batches_to_process)

            # store profit generated from processing orders
            self.orders.store_profit(processing_results)
        
        else:
            processing_results = None

        if current_time == cut_off_time:
            
            # stop accepting orders at nodes for this day
            self.nodes.change_order_acceptance_status(False)

        if current_time.time() == REPLENISHMENT_TIME:
            
            # calulate stock holding costs for this day
            self.stock_holding_costs[current_time.date()] = self.stock.holding_costs

            # replenish stock and count occurrences of replenishment
            self.replenishments[current_time.date()] = self.stock.replenish()
        
        if current_time == time(23, 59, 59):
            
            # reschedule allocation fot orders that need an allocation retry
            self.orders.retry_allocation()

            # reallow nodes to accept orders allocated
            self.nodes.change_order_acceptance_status(True)

            # store profit of the day
            self.profit[current_time.date()] += (self.orders.collect_profit + self.sales.collect_revenue - self.stock_holding_costs[current_time.date()])

        return processing_results

    def summarize_results(self) -> dict:

        ''' Returns a dict of summarized results (profit, number of replenishments, stock holding costs)
            to be  used for a pandas DataFrame.'''

        results = { DATE: list(self.profit.keys()),
                    ID: list(self.id for i in range(0, len(self.profit.values()))),
                    PROFIT: list(self.profit.values()),
                    REPLENISHMENTS: list(self.replenishments.values()),
                    HOLDING_COSTS: list(self.stock_holding_costs.values())
        }

        return results

