
###############################################################################################

'''This file contains the class Abc_Analysis.'''

###############################################################################################

from numpy import array, cumsum, sort, sum

from dstrbntw.constants import A, B, C
from parameters import STOCK_A_B_LIMIT, STOCK_B_C_LIMIT


class AbcAnalysisError(Exception):
    
    #Raised when abc analysis fails
    
    def __init__(self, err:Exception, index:int):
        
        self.name = AbcAnalysisError.__name__
        self.mid_level_error = f": An error occured while the abc-analysis was carried out for id {index}. \n"
        self.low_level_error = err.args[0] if isinstance(err.args[0], str) else str(err.args[0])
        self.msg = self.name + self.mid_level_error + self.low_level_error
        super().__init__(self.msg)


class Abc_Analysis:
    
    def __init__(self, index:int, row_headers:array, values:array, multidimensional:bool=None) -> None:

        '''Carries out abc-analysis and stores result as dict.'''

        #calculate abc analysis for multidimensional array
        self.result = self.analyse(index, row_headers, values, multidimensional=multidimensional)

    def analyse(self, index:int, row_headers:array, values:array, multidimensional:bool=None) -> dict:

        '''Caries out abc-analysi and returns results of as a dict
            with id as key and cumulated relative sum as value.
            Multidimensional np_arrays are reduces to 1 column.'''

        #Other sources:
        #https://practicaldatascience.co.uk/data-science/how-to-create-an-abc-inventory-classification-model
        #https://github.com/viessmann/abc_analysis/blob/master/abc_analysis/abc_analysis.py

        try:
            #sum all absolute values
            total = sum(values)

            #if input is multidimensional, sum rows to have a single dimensional array
            if multidimensional:
                #sum all rows (returns array of sums for each row)
                abs_row_values =  sum(values, axis=1)
            else:
                abs_row_values = values

            #free resources
            del values

            #sort values desc
            sorted_abs_row_values = sort(abs_row_values)[::-1]

            #Perform an indirect sort. It returns an array of indices of the same shape as a that index data along the given axis in sorted order.
            # (https://stackoverflow.com/questions/16486252/is-it-possible-to-use-argsort-in-descending-order/16486305)
            permutation = abs_row_values.argsort()[::-1]   
            
            #apply permutation to headers
            sorted_row_headers = row_headers[permutation]

            del row_headers, abs_row_values
            
            #compute relative values
            sorted_rel_row_values = sorted_abs_row_values / total

            #create cumulated sum https://numpy.org/doc/stable/reference/generated/numpy.cumsum.html
            cumulated_sorted_rel_row_values = cumsum(sorted_rel_row_values)

            #return a Dict with the frist column as keys and the second column as values sorted
            return dict(zip(sorted_row_headers, cumulated_sorted_rel_row_values))
        
        except IndexError as err:
            #report error
            print(f"{IndexError.__name__}: {err}")

        except Exception as err:
            raise AbcAnalysisError(err, index)

    def categorize(self, article_index:int) -> str:

        '''Returns the A/B/C category of an article at a certain node 
            based on the cumulated relative demand calculated during abc-analysis.'''

        cum_rel_demand = self.result[article_index]
        
        if cum_rel_demand > 0 and cum_rel_demand <= STOCK_A_B_LIMIT:
            return A
        elif cum_rel_demand > STOCK_A_B_LIMIT and cum_rel_demand <= STOCK_B_C_LIMIT:
            return B
        else: #cum_rel_demand > p.Assortment.STOCK_B_C_LIMIT:
            return C

    def plot():
        
        '''CURRENTLY NOT IMPLEMENTED!
        
            TO DO:
            plot results of abc_analysis. Source:
            https://practicaldatascience.co.uk/data-science/how-to-create-an-abc-inventory-classification-model'''
        

        pass
    