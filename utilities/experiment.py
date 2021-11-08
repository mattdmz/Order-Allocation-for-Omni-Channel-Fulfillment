
###############################################################################################

'''This file contains the experiment and experiment runner class.'''

###############################################################################################

from datetime import date, datetime, timedelta
from os import path

from configs import OUTPUT_DIR

class Experiment:

    def __init__(self, allocation_period:timedelta, allocation_regions:list, allocation_operator:str) -> None:
        
        '''Sets parameters for the experiment'''

        self.allocation_period = allocation_period
        self.allocation_regions = allocation_regions
        self.allocation_operator = allocation_operator

    def set_parameters(self, start:date, end:date, allocation_method:object) -> None:
        
        '''Sets start and end dates for period to experiment in as well as allocation method to use.'''

        self.start = start
        self.end = end
        self.allocation_method = allocation_method
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        exp_directory = self.run_id + "_" + allocation_method.__name__ + "_" + start.strftime("%m%d") + "_" + end.strftime("%m%d")
        self.output_dir_path = path.join(OUTPUT_DIR, exp_directory)

class Experiment_Runner:

    def __init__(self, test_days:int, test_periods:int, allocation_methods:list) -> None:

        '''Defines experiment framework.'''

        self.test_days = test_days
        self.test_periods = test_periods
        self.allocation_methods = allocation_methods

    def define_test_periods(self) -> list:

        '''Returns list of day tuples (start date, end date) to run the experiment with.'''

        return [(date(2019, 3, day), date(2019, 3, day-1+ self.test_days)) for day in range(1, self.test_periods*2, self.test_days)]
    
    def run(self, experiment:Experiment) -> None:

        '''Runs the experiment passed on a range of days with the allocation methods set.'''

        from main import main

        for allocation_method in self.allocation_methods:
            allocation_method:object
            
            # run experiments for the defined period of days
            for test_period in self.define_test_periods():
                test_period:tuple
                
                experiment.set_parameters(test_period[0], test_period[1], allocation_method)
                main(experiment)