# smartphone data

Smartphone data comes from two sources: passive sensors and active sensors. The passive sensors are those that do not require human input to collect data. In this case, the passive sensors are: location, application, battery, call and SMS logs, and screen. The active sensors are those that require human input. In this case, there is only one sensor called EMA. 

# Preprocessing
Preprocessing these data implies several steps depending on the sensor. For now, we will focus on the active sensor.

## Preprocessing steps
1. Run the script step1_download_smartphone.sh to download the data from the koota service to the right path. Notice that the koota service requires a login. To use the script, the cookies ID is required. Log in to the koota service (koota.cs.aalto.fi). Press F12 in the browser and check the cookies ID. Paste it in the script and then run it. The script requires two input arguments: the starting and ending date. Both are required in YYYY-MM-DD format
2. Run the script step5_organize_smartphone.py PATH SAVEPATH. Where PATH refers to the folder where all the log files downloaded from koota are. SAVEPATH refers to the path of the folder where the new file will be saved. This script will unify all the log files in one csv file. 
3. Run the script step6_compute_ema.py FILE SAVEPATH. Where FILE is the file path that contains all the unified EMA log files and SAVEPATH is the path where the scores will be saved. This script will compute the negative and positive affect based on the answers to the PANAS questions asked via EMA. It will also organize other information regarding sleep, menstruation, alcohol and caffeine consumption, and social scores that were provided via EMA. 
4. Run the script step_7_aggregate_smartphone.py PATH SAVEPATH. Where PATH refers to the folder where the unified koota files are. SAVEPATH refers to the path of the folder where the new file will be saved. This script will compute daily aggregations for calls, battery, SMS, screen, and GPS. This needs the niimpy package to preprocess. 

# Quality check
The smartphone quality check is the percentage of data loss during the whole experiment. 
1. Run the script ./src/quality_check/quality_check_smartphone.py. The script takes one positional argument, the path to the folder where data from all days are stored. 

