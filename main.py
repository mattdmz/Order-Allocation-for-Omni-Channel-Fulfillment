
###############################################################################################

'''This file contains the main logic.'''

###############################################################################################


from utilities.experiment import Experiment


def main(experiment:Experiment) -> None:

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
        result_protocols = Result_Protocols(experiment.output_dir_path, experiment.run_id, experiment.allocation_method)
    
    except OSError as err:
        print(err)       

    else:
        
        distribution_network = Distribution_Network(experiment.start, experiment.end)

        try:
            distribution_network.imp_regional_data(experiment.allocation_regions)

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
                
                simulation = Simulation(distribution_network, experiment, result_protocols)
                simulation.create_allocation_schedule()
                simulation.start()
                simulation.export_overall_results()

