Project connected to Masterthesis "Omni-Channel Fulfillment in multilevel distribution networks - a holistic optimization approach"

Contains a main logic to allocate orders in a virtual distribution network with a varaible number of fulfillment regions.
Differnet order allocation rules were developed to allocate a set of orders to nodes of the distribution network for same day delivery.
A Tabu Search Algorithm was implemented to optimize a initial allocation.

Files:
  - experiment.py contains a configurable script for the experiments.
                  Experiments for order alloaction over a variable period of time can be created. 
                  Differnet fulfillment regions can be selected.
                  Different order allocation rules or optimizers can be compared in the experiments.
  - main.py contains the main program logic.
  - parameters.py contains all variable parameters (costs, perfromances, capacities, times) used.
  - configs.py contains input and output directory paths as well as encoding variables.

Connection to local database "masterarbeit" required.
