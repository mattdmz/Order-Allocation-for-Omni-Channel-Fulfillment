
###############################################################################################

'''This script is used to run experiments using the main logic.'''

###############################################################################################


def main() -> None:

    '''Runs an experiment using the main logic.'''

    from datetime import timedelta

    from allocation.optimizers import Tabu_Search
    from allocation.rules import Allocation_Of_Nearest_Order, Chepest_Direct_Delivery, Cheapest_Delivery, Dynamic_1, \
                                Longest_Stock_Duration, Modified_Dynamic_1, Nearest_Already_Allocated_Nodes, Nearest_Nodes, Operational_Costs
    from utilities.concatcsvs import concat_results
    from utilities.experiment import Experiment, Experiment_Runner
    

    # period of time used to execute orders
    allocation_period = timedelta(hours=3, minutes=0, seconds=0)
 
    # [LIST] of regions to allocated orders in, e.g. [1005]. All all regions should be considered tpye "all"                         
    allocation_regions = [1006] #[1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]

    # choose from allocator.constants, relevant for Longest_Stock_Duration
    
    experiment = Experiment(allocation_period, allocation_regions)

    # define number of days to test and number of times (periods) to run the test on consecutive days
    test_days = 2
    test_periods = 1

    # set allocation methods to run program with (choices from allocation.rules)
    allocation_methods = [Nearest_Nodes] #[Allocation_Of_Nearest_Order, Chepest_Direct_Delivery, Cheapest_Delivery, Dynamic_1, \
                                #Longest_Stock_Duration, Modified_Dynamic_1, Nearest_Already_Allocated_Nodes, Nearest_Nodes, Operational_Costs]

    # run experiment with defined parameters
    exp_runner = Experiment_Runner(test_days, test_periods, allocation_methods)
    exp_runner.run(experiment)

    # concat result csvs
    # concat_results()

if __name__ == "__main__":

    main()