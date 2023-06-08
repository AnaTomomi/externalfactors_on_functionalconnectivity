# wristband data

Wristband data comes form Empatica E4 connect. Here, we employ four measurements (hr, temperature, electrodermal activity, and hrv)

# Preprocessing
Preprocessing these data implies: merging the data from different embrace streams, renaming the files to match the data naming conventions, and computing the daily averages.

## Preprocessing steps
1. Download the data from the empatica cloud system, following their instructions. The script step2_download_empatica.sh can be used. Note that the AWS configuration needs to be done beforehand. After, the first path in the code needs to be changed.
2. run the script ./src/preprocess/behavioral/step3_organize_empatica.py PATH SAVEPATH, where PATH is the path up until the daily folders from empatica start, and SAVEPATH is the path where the new files will be created. This script will create one file per day. 
3. run the script ./src/preprocess/behavioral/step4_aggregate_empatica.py PATH SAVEPATH, where PATH is the path where all the empatica files are, and SAVEPATH is the path where the new files will be created. 

# Quality check
The wristband quality check is the percentage of data loss within a day. 
1. Run the script ./src/quality_check/quality_check_empatica.py. The script takes one positional argument, the path to the folder where data from all days are stored. 

