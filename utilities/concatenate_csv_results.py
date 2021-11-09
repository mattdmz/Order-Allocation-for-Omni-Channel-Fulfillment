import os, glob
import shutil
import time
import fnmatch
import pandas as pd


def createdirs(rootdir, concatenateddir):
    
    for file in os.listdir(rootdir):
        d = os.path.join(rootdir, file)
        if os.path.isdir(d):
            print(d)
            #get last 9 characters, of the folder name (time of the test)
            file_time = d[len(d) - 9 :]
            #check if a directory for this time has been already created
            path_already_created = os.path.exists(os.path.join(concatenateddir, file_time))
            print("Path already created? " '% s' %path_already_created)
            if(path_already_created):
                     continue
            else:
            # Path
                path = os.path.join(concatenateddir, file_time)
                os.mkdir(path)
                print("Directory '% s' created" % file_time)
    	
 
def copyFromTo(fromdir,todir, basedir):
    for file in os.listdir(fromdir):
        d = os.path.join(fromdir, file)
        if os.path.isdir(d):
            #get last 9 characters, of the folder name (time of the test)
            file_time_from = d[len(d) - 9 :]
            file_time_to = todir[len(todir) - 9 :]
            if (file_time_from == file_time_to):
                for file2 in os.listdir(d):
                    if fnmatch.fnmatch(file2, '*_overall_results.csv'):
                        new_name = os.path.join(basedir,todir,file[16:len(file)] + '.csv')
                        old_name = os.path.join(d,file2)
                        if not os.path.exists(new_name):
                            shutil.copy(old_name, new_name)
                            print( "Copied", file, "as", new_name)
            else:
                continue

rootdir = 'I:\\austausch\\demetz\\Test_Experiments'
concatenateddir = 'I:\\austausch\\demetz\\concatenated_results'

#First delete all file in concatenated_results
shutil.rmtree(concatenateddir,ignore_errors=True)
time.sleep(1)
#create the concatenate dir
os.mkdir(concatenateddir)
#create subdirs for each day
createdirs(rootdir,concatenateddir)
#copy the day results to each day dir
for file in os.listdir(concatenateddir):
    d = os.path.join(concatenateddir, file)
    if os.path.isdir(d):
        copyFromTo(rootdir ,file, concatenateddir)

#concatenate results per day
for file in os.listdir(concatenateddir):
    d = os.path.join(concatenateddir, file)
    if os.path.isdir(d):
        all_files = glob.glob(os.path.join(d, "*.csv"))
        df_from_each_file = (pd.read_csv(f, sep=',') for f in all_files)
        df_merged   = pd.concat(df_from_each_file, ignore_index=True)
        df_merged.to_csv( "merged.csv")
