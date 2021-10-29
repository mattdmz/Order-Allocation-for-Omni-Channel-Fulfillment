
###############################################################################################

'''This file contains the main logic.'''

###############################################################################################


def main() -> None:

    '''Main logic.'''
    
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
        
        distribution_network = Distribution_Network()

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
    
    main()
