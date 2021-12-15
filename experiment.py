
###############################################################################################

'''This script is used to run experiments using the main logic.'''

###############################################################################################


def main() -> None:

    '''Runs an experiment using the main logic.'''

    from datetime import timedelta

    from allocation.optimizers import Tabu_Search
    from allocation.rules import Allocation_Of_Nearest_Order, Chepest_Direct_Delivery, Cheapest_Delivery, Dynamic_1, \
                                Longest_Stock_Duration, Mahar_Bretthauer_Venkataramanan, Nearest_Already_Allocated_Nodes, Nearest_Nodes, Operational_Costs
    from utilities.concatcsvs import concat_results
    from utilities.experiment import Experiment, Experiment_Runner

    # -------------------- variable inputs ------------------------------
    
    # period of time between two order allocation sessions
    allocation_period = timedelta(hours=3, minutes=0, seconds=0)
 
    # Input choose region to allocate orders in [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]                       
    allocation_regions = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]

    # create experiment
    experiment = Experiment(allocation_period, allocation_regions)

    # define number of days to test and number of times (periods) to run the test on consecutive days
    test_days = 2
    test_periods = 1
    start_day = 1

    # set allocation methods to run program with (choices from allocation.rules) as iterable (list)
    allocation_methods = [Allocation_Of_Nearest_Order, Chepest_Direct_Delivery, Cheapest_Delivery, Dynamic_1, 
                          Longest_Stock_Duration, Mahar_Bretthauer_Venkataramanan, Nearest_Already_Allocated_Nodes, 
                          Nearest_Nodes, Operational_Costs, Tabu_Search]

    # -------------------- variable inputs ------------------------------

    # run experiment with defined parameters
    exp_runner = Experiment_Runner(start_day, test_days, test_periods, allocation_methods)
    exp_runner.run(experiment)

    # summarized result in daily and overall summary csvs
    concat_results() # (comment out if results shouldld not be summarized for entire test period)

if __name__ == "__main__":

    main()