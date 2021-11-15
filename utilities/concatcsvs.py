

#######################################################################################################

"""This functions are used to concatenate the daily and overall results of all experiments in one file."""

#######################################################################################################

from datetime import datetime
from fnmatch import fnmatch
from glob import glob
from os import chdir, listdir, mkdir, path
from pandas import concat, DataFrame, read_csv
from shutil import copy, rmtree
from time import sleep

from configs import ENCODING, EXPERIMENT_DIR, FILE_TYPE, OUTPUT_DIR, SEP_FORMAT
from protocols.constants import ALGORITHM_USED, DAILY_RESULTS_FILE_NAME, DAILY_SUMMARY, OVERALL_RESULTS_FILE_NAME, OVERALL_SUMMARY, PROC_DATETIME
from protocols.results import init_results_evaluation


def create_dirs(concatenated_dir:str, type_of_result:str):

    '''Creates helping subdirs for each day.'''
    
    for file in listdir(OUTPUT_DIR):
        d = path.join(OUTPUT_DIR, file)
        
        if path.isdir(d):
            #get last 9 characters, of the folder name (time of the test)
            file_time = d[-9:]
            #check if a directory for this time has been already created
            path_already_created = path.exists(path.join(concatenated_dir, type_of_result + file_time))
            
            if(path_already_created):
                continue
            else:
            # Path
                file_path = path.join(concatenated_dir, type_of_result + file_time)
                mkdir(file_path)
                #print("Directory "% s" created" % file_time)    	

def copy_from_to(from_dir:str, to_dir:str, base_dir:str, type_of_result:str):
    
    '''Copies the results of a day to each day dir.'''

    for file in listdir(from_dir):
        d = path.join(from_dir, file)
        
        if path.isdir(d):
            # get last 9 characters, of the folder name (time of the test)
            file_time_from = d[-9:]
            file_time_to = to_dir[-9:]
            
            if (file_time_from == file_time_to):
                
                for file2 in listdir(d):
                    
                    if fnmatch(file2, type_of_result):
                        new_name = path.join(base_dir,to_dir,file[16:len(file)] + FILE_TYPE)
                        old_name = path.join(d,file2)
                        
                        if not path.exists(new_name):
                           copy(old_name, new_name)
            else:
                continue

def concat_results():

    '''Concatenates the daily and overall results of all experiments in one file.'''

    # Define the directory where the files are and where they have to be concatenate
    concatenated_dir = path.join(EXPERIMENT_DIR, "experiment_" + datetime.now().strftime("%Y%m%d_%H%M%S"))

    # First delete all file in concatenated_results to avoid old data
    rmtree(concatenated_dir, ignore_errors=True)
    sleep(1)

    # create the concatenate dir
    mkdir(concatenated_dir)

    # create subdirs for each day
    create_dirs(concatenated_dir, OVERALL_SUMMARY)
    create_dirs(concatenated_dir, DAILY_SUMMARY)

    # copy the day results to each day dir
    for file in listdir(concatenated_dir):
        d = path.join(concatenated_dir, file)
        
        if path.isdir(d):
            if OVERALL_SUMMARY in d:
                copy_from_to(OUTPUT_DIR, file, concatenated_dir, "*" + OVERALL_RESULTS_FILE_NAME + FILE_TYPE)
            if DAILY_SUMMARY in d:
                copy_from_to(OUTPUT_DIR, file, concatenated_dir, "*" + DAILY_RESULTS_FILE_NAME + FILE_TYPE)

    # create summary file
    overall_summary = DataFrame(columns=init_results_evaluation("").keys())
    daily_summary = DataFrame(columns=init_results_evaluation("").keys())

    # concatenate results per day
    for file in listdir(concatenated_dir):
        d = path.join(concatenated_dir, file)
        
        if path.isdir(d):
            # add a column with the algorithm name to the file
            chdir(d)
            
            for csv_file in listdir(d):
                df = read_csv(csv_file, delimiter=SEP_FORMAT)
                
                # insert algorithm name
                algo_used = csv_file[:-14]
                df.insert(0, ALGORITHM_USED, algo_used)

                # insert processing_period
                period = d[-9:]
                df[PROC_DATETIME] = [period for row in df.index]
                
                # reexport data to csv
                df.to_csv(csv_file, index=False, sep=SEP_FORMAT, encoding=ENCODING)
            
            # combine all files in the list
            all_file_names = [i for i in glob("*.{}".format(FILE_TYPE[1:]))]
            concatenated_data = concat([read_csv(f, delimiter=SEP_FORMAT) for f in all_file_names])

        # concat with current summary
        if OVERALL_SUMMARY in d:
            overall_summary = overall_summary.append(concatenated_data, ignore_index=True)
        if DAILY_SUMMARY in d:
            daily_summary = daily_summary.append(concatenated_data, ignore_index=True)

    # export summary of days to csv
    daily_summary.to_csv(DAILY_SUMMARY + FILE_TYPE, index=False, sep=SEP_FORMAT, encoding=ENCODING)
    overall_summary.to_csv(OVERALL_SUMMARY + FILE_TYPE, index=False, sep=SEP_FORMAT, encoding=ENCODING)
    chdir(concatenated_dir)

    # delete unnecessary directories
    # first delete all file in concatenated_results to avoid old data
    for file in listdir(concatenated_dir):
        d = path.join(concatenated_dir, file)
        
        if path.isdir(d):
            rmtree(d, ignore_errors=True)
