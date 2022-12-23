# wristband data

Wristband data comes form Empatica E4 connect. Here, we employ four measurements (hr, temperature, electrodermal activity, and hrv)

# Preprocessing
Preprocessing these data implies: organizing the files with the correct naming scheme, reading the data for 1 day, organize the data in dataframes, and save the dataframes as outputs ready to use. Results from this preprocessing are still considered raw data. 

## Preprocessing steps
1. Download the data from the empatica E4 connect website. Store each session with the name "ses#", where # means the session number. Make sure session 1 is the oldest session in a day, session 2 is the second oldest, and so on. Store all sessions#.zip files in ./data/sub-01/day-00X/behavioral according to the day X to preprocess. 
2. run the script ./src/preprocess/behavioral/step0_organize_wristbandfiles.sh. The only input of this script should be the day number. For example, if we want to preprocess the day 3, we should run ./src/preprocess/behavioral/step0_organize_wristbandfiles.sh 
3. run the script ./src/preprocess/behavioral/step1_unifyfiles_empatica.py. This script takes two positional arguments: the variable we want to preprocess and the path where the data is stored. It assumes we follow the behavioral BIDS organization of the folders. 

# Quality check
The wristband quality check is the percentage of data loss within a day. 
1. Run the script ./src/quality_check/quality_check_empatica.py. The script takes one positional argument, the path to the folder where data from all days are stored. 

# Final preprocessing: daily aggregation
For this particular work, we are interested in daily aggregations of the wristband data. Therefore, we need to aggregate the raw data. To do so:
1. Run the ./src/preprocess/behavioral/step2_daily_aggregate.py script. The script takes two positional arguments: the parent folder for all stored data and the complete name (path+name) of the file where the results will be stored. 
