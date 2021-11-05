
###############################################################################################

'''This file contains the main logic.'''

###############################################################################################

from datetime import date
from parameters import NUMBER_OF_TEST_PERIODS, ORDER_PROCESSING_START, ORDER_PROCESSING_END, TEST_DAYS

def main(start:date=ORDER_PROCESSING_START, end:date=ORDER_PROCESSING_END) -> None:

    ''' Initializes a distribution network mode with imported data.
        Tries to allocate orders and close sales for each day between start and end
        between OP_START_TIME and OP_END_TIME.
        Protocols restuls.'''
    
    from dstrbntw.abcanalysis import AbcAnalysisError
    from dstrbntw.dstrbntw import Distribution_Network
    from dstrbntw.errors import ImportModelDataError, InitStockError
    from dstrbntw.simulation import Simulation
    from protocols.results import Result_Protocols

    try:
        result_protocols = Result_Protocols()
    
    except OSError as err:
        print(err)       

    else:
        
        distribution_network = Distribution_Network(start, end)

        try:
            distribution_network.imp_regional_data()

        except ImportModelDataError as err:
            print(err)

        else:

            try: 
                distribution_network.determine_demand()
                distribution_network.init_stock()

            except InitStockError as err:
                print(err)

            except AbcAnalysisError as err:
                print(err)
            
            else:

                result_protocols.init_results_dict(distribution_network.regions.keys())
                
                simulation = Simulation(distribution_network, result_protocols)
                simulation.create_allocation_schedule()
                simulation.start()
                simulation.export_overall_results()

if __name__ == "__main__":

    if NUMBER_OF_TEST_PERIODS == None:

        # run program with default ORDER_PROCESSING_START and ORDER_PROCESSING_END dates set in parameters
        main()
    
    else:

        # set list of day tuples (start date, end date) to run the program with
        days_to_test = [(date(2019, 3, day), date(2019, 3, day-1+TEST_DAYS)) for day in range(1, NUMBER_OF_TEST_PERIODS, TEST_DAYS)]

        # run program for all 
        for day in days_to_test:
            main(day[0], day[1])

