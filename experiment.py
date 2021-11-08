
###############################################################################################

'''This script is used to run experiments using the main logic.'''

###############################################################################################


def main() -> None:

    '''Runs an experiment using the main logic.'''


    from datetime import timedelta

    from allocation.constants import MAX, MEDIAN, MIN
    from allocation.rules import Nearest_Nodes, Nearest_Already_Allocated_Nodes, Allocation_Of_Nearest_Order, Longest_Stock_Duration, Dynamic_1
    from utilities.experiment import Experiment, Experiment_Runner


    # period of time used to execute orders
    allocation_period = timedelta(hours=3, minutes=0, seconds=0)

    # [LIST] of regions to allocated orders in, e.g. [1005]. All all regions should be considered tpye "all"                         
    allocation_regions = [1005]

    # choose from allocator.constants, relevant for Longest_Stock_Duration
    allocation_operator = MEDIAN
    
    experiment = Experiment(allocation_period, allocation_regions, allocation_operator)

    # define number of days to test and number of times (periods) to run the test on consecutive days
    test_days = 2
    test_periods = 10

    # set allocation methods to run program with
    allocation_methods = [Nearest_Nodes, Longest_Stock_Duration] #Nearest_Already_Allocated_Nodes, Allocation_Of_Nearest_Order 

    # run experiment with defined parameters
    exp_runner = Experiment_Runner(test_days, test_periods, allocation_methods)
    exp_runner.run(experiment)

if __name__ == "__main__":

    main()