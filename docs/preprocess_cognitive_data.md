# cognitive data

Cognitive data comes from the PVT and nback tasks performed inside and outside of the scanner. It comes from the presentation logs. 

# Preprocessing
Preprocessing these data implies computing the scores for the PVT and nback tasks for all days available. 

## Preprocessing steps
1. Download the data from the presentation folder and paste the logs in the right path
2. Run the script ./src/preprocess/cognitive/step0_organize_logs.sh
3. run the script ./src/preprocess/cognitive/step1_compute-pvt-scores.py PATH SAVEFILE. The script takes two positional arguments: the parent path where all cognitive data is stored and the full filename (path+name) where the preprocessed data will be stored
4. run the script ./src/preprocess/cognitive/step2_compute-nback-scores.py PATH SAVEFILE. The script takes two positional arguments: the parent path where all cognitive data is stored and the full filename (path+name) where the preprocessed data will be stored

# Quality check
The cognitive quality check is the percentage of data loss during the whole experiment. 
1. Run the script ./src/quality_check/quality_check_cognitive.py. The script takes one positional argument, the path to the folder where data from all days are stored. 

