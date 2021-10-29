
###############################################################################################

'''This file contains time simulation related functions.'''

###############################################################################################

from datetime import date, datetime, timedelta, time

from allocmethod import ALLOC_METHOD, ALLOC_OPERATOR
from dstrbntw.dstrbntw import Distribution_Network
from dstrbntw.region import Region
from parameters import ALLOC_END_TIME, ALLOC_PERIOD, ALLOC_START_TIME, NUMBER_OF_WORKDAYS, ORDER_PROCESSING_START, \
                        ORDER_PROCESSING_END, CUT_OFF_TIME
from protocols.results import Result_Protocols
from utilities.datetime import daterange, timerange

class Simulation:

    def __init__(self, dstrb_ntw:Distribution_Network, results:Result_Protocols) -> None:
        
        # store objects
        self.dstrb_ntw = dstrb_ntw
        self.results = results

        # create an order allocation schedule for the simulation
        self.allocation_schedule = self.create_allocation_schedule()

        # init counter of allocations
        self.allocation_counter = 0

    def create_allocation_schedule(self) -> list:

        '''Creates an allocation schedule (list) based on the parameter ALLOC_PERIOD.'''

        #init optimization schedule
        allocation_schedule = []

        for this_date in daterange(ORDER_PROCESSING_START, ORDER_PROCESSING_END):
            this_date:date

            # check if day is a workingday
            if this_date.isoweekday() <= NUMBER_OF_WORKDAYS:

                this_time = datetime.combine(this_date, ALLOC_START_TIME)
                end_time = datetime.combine(this_date, ALLOC_END_TIME)

                #construct optimization schedule
                while this_time <= end_time:         

                    #add time to schedule
                    allocation_schedule.append(this_time)

                    #determine next cut-off for optimization
                    this_time += ALLOC_PERIOD

        return allocation_schedule

    def check_for_processings(self, region:Region, current_time:datetime, cut_off_time:datetime) -> None:

        '''Processes order batches if there are any scheduled for current_time.'''

        # collect profit generated from processing orders and closing sales
        processing_evaluation = region.process_orders(current_time, cut_off_time)

        if processing_evaluation is not None:

            self.results.store_orders_evaluation(processing_evaluation, region.id)
            self.results.export_orders_evaluation(processing_evaluation)

    def allocate(self, region:Region, current_time:datetime, cut_off_time:datetime) -> None:

        '''Allocates orders and processes sales.'''

        # import transactions (sales and orders) to allocate/handle
        region.imp_new_transactions(current_time - ALLOC_PERIOD, current_time)
        
        # allocate orders and check processability of sales
        allocation = region.start_allocation(ALLOC_METHOD, current_time, cut_off_time, ALLOC_OPERATOR)

        # evaluate orders that could not be allocated
        evaluation_of_not_allocated_orders = region.determine_not_allocated_orders(allocation)

        if evaluation_of_not_allocated_orders is not None:
                        
            # store and export not allocated orders
            self.results.store_orders_evaluation(evaluation_of_not_allocated_orders, region.id)
            self.results.export_orders_evaluation(evaluation_of_not_allocated_orders)
        
        # export allocation 
        self.results.export_allocation(region.transform_allocation_array(allocation))

        # evaluate set processability of sales
        sales_evaluation = region.process_sales(current_time, region.id)

        if sales_evaluation is not None:
            
            self.results.store_sales_evaluation(sales_evaluation, region.id)
            self.results.export_sales_evaluation(sales_evaluation)

        region.terminate_allocation(ALLOC_METHOD.__type__)

    def close_day(self, region:Region) -> None:

        '''Carries out operations of the end of the day.'''
                
        self.results.store_stock_holding_costs(region.calc_stock_holding_costs(), region.id)
        self.results.store_number_of_replenishments(region.check_for_replenishments(), region.id)
        region.reschedule_allocation_of_unallocated_orders()
        region.change_order_acceptance_status(True)

        self.results.export_daily_results(region.id)
        self.results.transfer_daily_results_to_overall_results(region.id)

    def check_operations(self, current_time:datetime, cut_off_time:datetime) -> None:

        '''Check which actions need to be carried out during the time simulation.'''

        # determine actions to be carried out at current_time
        for region in self.dstrb_ntw.regions.values():
            region:Region

            self.check_for_processings(region, current_time, cut_off_time)                

            if current_time == self.allocation_schedule[self.allocation_counter]:

                self.allocate(region, current_time, cut_off_time)

            if current_time.time() == ALLOC_END_TIME:

                self.close_day(region)

        if current_time == self.allocation_schedule[self.allocation_counter]:

            # increase counter for the allocation schedule
            self.allocation_counter += 1 if self.allocation_counter < len(self.allocation_schedule) - 1 else 0

    def start(self) -> None:

        ''' Iterates through time between order_processing_start and order_processing_end 
            and carries out actions at predefined timestamps.'''

        # days
        for this_date in daterange(ORDER_PROCESSING_START, ORDER_PROCESSING_END):
            this_date:date

            # check if day is a workingday
            if this_date.isoweekday() <= NUMBER_OF_WORKDAYS:

                # set new cut off time for order processing
                cut_off_time = datetime.combine(this_date, CUT_OFF_TIME)

                start_date_time = datetime.combine(this_date, ALLOC_START_TIME)
                end_date_time = datetime.combine(this_date, ALLOC_END_TIME)

                # hours
                for hour in timerange(start_date_time, end_date_time, "hours"):

                    start_date_time_2 = datetime.combine(start_date_time, time(hour.hour, 0, 1))
                    end_date_time_2 = datetime.combine(end_date_time, time(hour.hour, 0, 0))

                    # minutes
                    for minute in timerange(start_date_time_2, end_date_time_2 + timedelta(hours=1, minutes=1), "minutes"):
                        
                        # define current time
                        current_time = datetime.combine(start_date_time_2, time(hour.hour, minute.minute, 0))

                        # check if operations need to be carried out at current_time
                        self.check_operations(current_time, cut_off_time) 

    def export_overall_results(self) ->None :

        ''' Exports overall results form simualtion.
            Stores a copy of the parameters in the output dir.'''

        self.results.export_overall_results()
        self.results.export_parameters_used()
