

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

from configs import EXPERIMENT_DIR, FILE_TYPE, OUTPUT_DIR, SEP_FORMAT
from protocols.constants import DAILY_RESULTS_FILE_NAME, DAILY_SUMMARY, EXPERIMENT_FILE_NAME, OVERALL_RESULTS_FILE_NAME, OVERALL_SUMMARY
from protocols.results import init_results_evaluation
from utilities.expdata import write_df

def create_dirs(experiment_dir:str, type_of_result:str):

    '''Creates helping subdirs for each day.'''
    
    for file in listdir(OUTPUT_DIR):
        d = path.join(OUTPUT_DIR, file)
        
        if path.isdir(d):
            #get last 9 characters, of the folder name (time of the test)
            file_time = d[-9:]
            #check if a directory for this time has been already created
            path_already_created = path.exists(path.join(experiment_dir, type_of_result + file_time))
            
            if(path_already_created):
                continue
            else:
            # Path
                file_path = path.join(experiment_dir, type_of_result + file_time)
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

    ''' Concatenates the daily and overall results of all experiments 
        inside the defualt OUTPUT_DIR in one file.'''

    # Define the directory where the files are and where they have to be concatenate
    experiment_name = EXPERIMENT_FILE_NAME + datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = path.join(EXPERIMENT_DIR, experiment_name)

    # First delete all file in concatenated_results to avoid old data
    rmtree(experiment_dir, ignore_errors=True)
    sleep(1)

    # create the concatenate dir
    mkdir(experiment_dir)

    # create subdirs for each day
    create_dirs(experiment_dir, OVERALL_SUMMARY)
    create_dirs(experiment_dir, DAILY_SUMMARY)

    # copy the day results to each day dir
    for file in listdir(experiment_dir):
        d = path.join(experiment_dir, file)
        
        if path.isdir(d):
            if OVERALL_SUMMARY in d:
                copy_from_to(OUTPUT_DIR, file, experiment_dir, "*" + OVERALL_RESULTS_FILE_NAME + FILE_TYPE)
            if DAILY_SUMMARY in d:
                copy_from_to(OUTPUT_DIR, file, experiment_dir, "*" + DAILY_RESULTS_FILE_NAME + FILE_TYPE)

    # create summary file
    overall_summary = DataFrame(columns=init_results_evaluation("").keys())
    daily_summary = DataFrame(columns=init_results_evaluation("").keys())

    # concatenate results per day
    for file in listdir(experiment_dir):
        d = path.join(experiment_dir, file)
        
        if path.isdir(d):
            # add a column with the algorithm name to the file
            chdir(d)
            
            # combine all files in the list
            all_file_names = [i for i in glob("*.{}".format(FILE_TYPE[1:]))]
            concatenated_data = concat([read_csv(f, delimiter=SEP_FORMAT) for f in all_file_names])

        # concat with current summary
        if OVERALL_SUMMARY in d:
            overall_summary = overall_summary.append(concatenated_data, ignore_index=True)
        if DAILY_SUMMARY in d:
            daily_summary = daily_summary.append(concatenated_data, ignore_index=True)

    # export summary of days to csv
    write_df(daily_summary, experiment_name + DAILY_SUMMARY, experiment_dir, header=True)
    write_df(overall_summary, experiment_name+ OVERALL_SUMMARY, experiment_dir, header=True)

    chdir(experiment_dir)

    # delete unnecessary directories
    # first delete all file in concatenated_results to avoid old data
    for file in listdir(experiment_dir):
        d = path.join(experiment_dir, file)
        
        if path.isdir(d):
            rmtree(d, ignore_errors=True)
