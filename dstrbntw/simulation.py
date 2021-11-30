
###############################################################################################

'''This file contains time simulation related functions.'''

###############################################################################################

from datetime import date, datetime, timedelta, time

from allocation.constants import OPTIMIZER
from dstrbntw.dstrbntw import Distribution_Network
from dstrbntw.region import Region
from parameters import ALLOC_END_TIME, ALLOC_START_TIME, CUT_OFF_TIME, END_OF_TOURS, NUMBER_OF_WORKDAYS                   
from protocols.results import Result_Protocols
from utilities.datetime import daterange, timerange
from utilities.experiment import Experiment

class Simulation:

    def __init__(self, dstrb_ntw:Distribution_Network, experiment:Experiment, results:Result_Protocols) -> None:
        
        # store objects
        self.dstrb_ntw = dstrb_ntw
        self.experiment = experiment
        self.results = results

        # create an order allocation schedule for the simulation
        self.allocation_schedule = self.create_allocation_schedule()

        # init counter of allocations
        self.allocation_counter = 1

    def create_allocation_schedule(self) -> list:

        '''Creates an allocation schedule (list) based on the parameter ALLOC_PERIOD.'''

        # init optimization schedule
        allocation_schedule = [datetime.combine(self.experiment.start, time(0, 0, 0))]

        for this_date in daterange(self.experiment.start, self.experiment.end + timedelta(days=1)):
            this_date:date

            # check if day is a workingday
            if this_date.isoweekday() <= NUMBER_OF_WORKDAYS:

                # this_time = datetime.combine(this_date, time(12,0,0))
                # allocation_schedule.append(this_time)

                this_time = datetime.combine(this_date, ALLOC_START_TIME)

                if this_date == self.experiment.end:
                    end_time = datetime.combine(this_date, CUT_OFF_TIME)
                else:
                    end_time = datetime.combine(this_date, ALLOC_END_TIME)
                # construct optimization schedule
                while this_time <= end_time:         

                    # add time to schedule
                    allocation_schedule.append(this_time)

                    # determine next cut-off for optimization
                    this_time += self.experiment.allocation_period

        return allocation_schedule

    def check_for_processings(self, region:Region, current_time:datetime) -> None:

        '''Processes order batches if there are any scheduled for current_time.'''

        # collect profit generated from processing orders and closing sales
        processing_evaluation = region.process_batches(current_time)

        if processing_evaluation is not None:
            region.clear_allocated_orders()
            self.results.store_orders_evaluation(processing_evaluation, region.id)
            self.results.export_orders_evaluation(processing_evaluation)

    def allocate(self, region:Region, current_time:datetime) -> None:

        '''Allocates orders and processes sales.'''

        # import transactions (sales and orders) to allocate/handle
        imported_trsct_eval  = region.imp_new_transactions(self.allocation_schedule[self.allocation_counter - 1], current_time)
        
        # store evaluation of imported transactions
        self.results.store_imported_trsct_eval(imported_trsct_eval, region.id)

        # allocate orders and check processability of sales
        allocation = region.start_allocation(self.experiment.allocation_method, current_time)

        # export allocation 
        self.results.export_allocation(region.transform_allocation_array(allocation.allocation))

        # export optimization report 
        if self.experiment.allocation_method.__type__ == OPTIMIZER:
            self.results.export_optimization_protocol(allocation.protocol, current_time)

        # evaluate orders that could not be allocated
        evaluation_of_not_allocated_orders = region.determine_not_allocated_orders(allocation.allocation, current_time)

        if evaluation_of_not_allocated_orders is not None:
                        
            # reschedule not allocated orders if they were not already reallocated and export not allocated orders
            self.results.store_orders_evaluation(evaluation_of_not_allocated_orders, region.id)
            self.results.export_orders_evaluation(evaluation_of_not_allocated_orders)

        # evaluate set processability of sales
        sales_evaluation = region.process_sales(current_time, region.id)

        if sales_evaluation is not None:
            
            self.results.store_sales_evaluation(sales_evaluation, region.id, current_time)
            self.results.export_sales_evaluation(sales_evaluation)

        region.terminate_allocation(self.experiment.allocation_method.__type__)

    def process_remaining_orders(self, region:Region, current_time:datetime) -> None:

        '''Processes orders that were scheduled but not processed within OP_END_TIME on self.experiment.end(date).'''

        # evaluate orders that could not be allocated
        self.check_for_processings(region, current_time)

        # evaluate orders that were scheduled but not processed
        evaluation_of_remaining_orders = region.determine_remainig_orders()

        if evaluation_of_remaining_orders is not None:
                        
            # reschedule not allocated orders if they were not already reallocated and export not allocated orders
            self.results.export_orders_evaluation(evaluation_of_remaining_orders)

    def close_day(self, region:Region, current_time:datetime) -> None:

        '''Carries out operations of the end of the day.'''

        if current_time.date() == self.experiment.end:
            self.process_remaining_orders(region, current_time)

        else:
            region.define_delivery_day(current_time)
            region.reschedule_allocation_of_unallocated_orders()

        # protocol results
        self.results.store_out_of_stock_situations(region.determine_out_of_stock_situations(), region.id)
        self.results.store_stock_holding_costs(region.calc_stock_holding_costs(), region.id)
        self.results.store_number_of_replenishments(region.check_for_replenishments(current_time), region.id)
        
        # export daily results
        self.results.export_daily_results(region.id, current_time)

        #add daily results to overall results
        self.results.transfer_daily_results_to_overall_results(region.id)

    def check_operations(self, current_time:datetime) -> None:

        '''Check which actions need to be carried out during the time simulation.'''

        # determine actions to be carried out at current_time
        for region in self.dstrb_ntw.regions.values():
            region:Region

            if current_time.time() == ALLOC_START_TIME:
                region.define_delivery_day(current_time)

            self.check_for_processings(region, current_time)
            
            if current_time.time() == ALLOC_END_TIME:
                # reset all order acceptance booleans to True (in case they were set to False becase capacities were exhausted)
                region.change_order_acceptance_status(True)
                region.define_delivery_day(datetime.combine(current_time + timedelta(days=1), time(0, 1, 0)))          

            if current_time == self.allocation_schedule[self.allocation_counter]:
                self.allocate(region, current_time)                 

            if current_time.time() == END_OF_TOURS:
                self.close_day(region, current_time)

        if current_time == self.allocation_schedule[self.allocation_counter]:

            # increase counter for the allocation schedule
            self.allocation_counter += 1 if self.allocation_counter < len(self.allocation_schedule) - 1 else 0

    def start(self) -> None:

        ''' Iterates through time between self.experimet.start and self.experimet.end 
            and carries out actions at predefined timestamps.'''

        # days
        for this_date in daterange(self.experiment.start, self.experiment.end + timedelta(days=1)):
            this_date:date

            # check if day is a workingday
            if this_date.isoweekday() <= NUMBER_OF_WORKDAYS:

                start_date_time = datetime.combine(this_date, ALLOC_START_TIME)
                end_date_time = datetime.combine(this_date, END_OF_TOURS)

                # hours
                for hour in timerange(start_date_time, end_date_time, "hours"):

                    start_date_time_2 = datetime.combine(start_date_time, time(hour.hour, 0, 1))
                    end_date_time_2 = datetime.combine(end_date_time, time(hour.hour, 0, 0))

                    # minutes
                    for minute in timerange(start_date_time_2, end_date_time_2 + timedelta(hours=1, minutes=1), "minutes"):
                        
                        # define current time
                        current_time = datetime.combine(start_date_time_2, time(hour.hour, minute.minute, 0))

                        # check if operations need to be carried out at current_time
                        self.check_operations(current_time) 

    def export_overall_results(self) ->None :

        ''' Exports overall results form simualtion.
            Stores a copy of the parameters in the output dir.'''

        self.results.export_overall_results(self.experiment.start, self.experiment.end)
        self.results.export_parameters_used()
