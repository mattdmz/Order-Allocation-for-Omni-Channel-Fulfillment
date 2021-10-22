
###############################################################################################

'''This file contains the main logic.'''

###############################################################################################


def main() -> None:

    '''Main logic.'''
    
    from dstrbntw.abcanalysis import AbcAnalysisError
    from dstrbntw.dstrbntw import Distribution_Network
    from dstrbntw.errors import ImportModelDataError, InitDistNtwError

    distribution_network = Distribution_Network()

    try:
        distribution_network.imp_data()

    except ImportModelDataError as err:
        print(err)

    else:

        try: 
            distribution_network.determine_demand()
            distribution_network.init_stock()
        
        except InitDistNtwError as err:
            print(err)

        except AbcAnalysisError as err:
            print(err)
        
        else:
            # allocate and process orders and handle sales
            distribution_network.init_evaluation_model()
            distribution_network.init_protocols_and_export_files()
            distribution_network.start_timesim()

            try:
                distribution_network.export_results()
            
            except OSError as err:
                print(err)

if __name__ == "__main__":
    
    main()


        

        

        













