import os, glob
import shutil
import time
import fnmatch
import pandas as pd

#create subdirs for each day
def createdirs(rootdir, concatenateddir,typeOfResult):
    
    for file in os.listdir(rootdir):
        d = os.path.join(rootdir, file)
        if os.path.isdir(d):
            #get last 9 characters, of the folder name (time of the test)
            file_time = d[len(d) - 9 :]
            #check if a directory for this time has been already created
            path_already_created = os.path.exists(os.path.join(concatenateddir, typeOfResult + file_time))
            if(path_already_created):
                     continue
            else:
            # Path
                path = os.path.join(concatenateddir, typeOfResult + file_time)
                os.mkdir(path)
                #print("Directory '% s' created" % file_time)
    	
#copy the day results to each day dir
def copyFromTo(fromdir,todir, basedir, typeOfResult):
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
                            #print( "Copied", file, "as", new_name)
            else:
                continue


#Define the directory where the files are and where they have to be concatenate
rootdir = 'I:\\austausch\\demetz\\Test_Experiments'
concatenateddir = 'I:\\austausch\\demetz\\concatenated_results'

#First delete all file in concatenated_results to avoid old data
shutil.rmtree(concatenateddir,ignore_errors=True)
time.sleep(1)
#create the concatenate dir
os.mkdir(concatenateddir)
#create subdirs for each day
createdirs(rootdir,concatenateddir, '_overall_')
createdirs(rootdir,concatenateddir, '_daily_')

#copy the day results to each day dir
for file in os.listdir(concatenateddir):
    d = os.path.join(concatenateddir, file)
    if os.path.isdir(d):
        if '_overall_' in d:
            copyFromTo(rootdir ,file, concatenateddir, '*_overall_results.csv')
        if '_daily_' in d:
            copyFromTo(rootdir ,file, concatenateddir, '*_daily_results.csv')

#concatenate results per day
for file in os.listdir(concatenateddir):
    d = os.path.join(concatenateddir, file)
    if os.path.isdir(d):
        #add a column with the algorithm name to the file
        os.chdir(d)
        for csvfile in os.listdir(d):
            df = pd.read_csv(csvfile,delimiter=';')
            df.insert(0,"algorithm_used",csvfile[0:len(csvfile)-14])
            df.to_csv(csvfile,  index=False, sep=';', encoding='utf-8-sig')
        
        
        #combine all files in the list
        extension = 'csv'
        all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
        combined_csv = pd.concat([pd.read_csv(f, delimiter=';') for f in all_filenames ])

        #export to csv
        combined_csv.to_csv( d + "combined_results.csv", index=False, sep=';', encoding='utf-8-sig')
        print("Concatenated results file created ",  d + "\\" +  "combined_results.csv")
        os.chdir(concatenateddir)

#delete unnecessary directories
#First delete all file in concatenated_results to avoid old data
for file in os.listdir(concatenateddir):
    d = os.path.join(concatenateddir, file)
    if os.path.isdir(d):
        shutil.rmtree(d,ignore_errors=True)

