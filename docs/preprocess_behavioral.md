# Behavioral data
Behavioral data are collected using other sensors like: smartphone, smartring, smartband, eye-tracker, and questionnaires. Here are some instructions to preprocess the behavioral data:

# Questionnaires
There are two questionnaires, one set at the beginning of the experiment and a set to be filled after each scanner session. 

## Preprocessing
1. Run the script **step0_compute_questionnaire_scores.py** PATH SAVEPATH. This script preprocesses the initial set of questionnaires (PSS, PHQ9, OASIS, PSQI, and Big5). Because of the file, it also processes the PSS, PHQ9, and GAD for the weekly questionnaires.
2. Run the script **step11_compute_postscanner_scores.py** ORIG_FILE SAVE_FILE, where ORIG_FILE is the original file and SAVE_FILE the organized one.

# smartphone data
Smartphone data comes from two sources: passive sensors and active sensors. The passive sensors are those that do not require human input to collect data. In this case, the passive sensors are: location, application, battery, call and SMS logs, and screen. The active sensors are those that require human input. In this case, there is only one sensor called EMA. 

## Preprocessing
Preprocessing these data implies several steps depending on the sensor. For now, we will focus on the active sensor.

1. Run the script **step1_download_smartphone.sh** to download the data from the koota service to the right path. Notice that the koota service requires a login. To use the script, the cookies ID is required. Log in to the koota service (koota.cs.aalto.fi). Press F12 in the browser and check the cookies ID. Paste it in the script and then run it. The script requires two input arguments: the starting and ending date. Both are required in YYYY-MM-DD format
2. Run the script **step5_organize_smartphone.py** PATH SAVEPATH. Where PATH refers to the folder where all the log files downloaded from koota are. SAVEPATH refers to the path of the folder where the new file will be saved. This script will unify all the log files in one csv file. 
3. Run the script **step6_compute_ema.py** FILE SAVEPATH. Where FILE is the file path that contains all the unified EMA log files and SAVEPATH is the path where the scores will be saved. This script will compute the negative and positive affect based on the answers to the PANAS questions asked via EMA. It will also organize other information regarding sleep, menstruation, alcohol and caffeine consumption, and social scores that were provided via EMA. 
4. Run the script **step_7_aggregate_smartphone.py** FILE SAVEPATH. Where PATH refers to the folder where the unified koota files are. SAVEPATH refers to the path of the folder where the new file will be saved. This script will compute daily aggregations for calls, battery, SMS, screen, and GPS. This needs the niimpy package to preprocess. 

## Quality check
The smartphone quality check is the percentage of data loss during the whole experiment. 
1. Run the script ./src/quality_check/**quality_check_smartphone.py**. The script takes one positional argument, the path to the folder where data from all days are stored. 


# wristband data
Wristband data comes form Empatica E4 connect. Here, we employ four measurements (hr, temperature, electrodermal activity, and hrv)

## Preprocessing
Preprocessing these data implies: merging the data from different embrace streams, renaming the files to match the data naming conventions, and computing the daily averages.

1. Download the data from the empatica cloud system, following their instructions. The script **step2_download_empatica.sh** can be used. Note that the AWS configuration needs to be done beforehand. After, the first path in the code needs to be changed.
2. run the script ./src/preprocess/behavioral/**step3_organize_empatica.py** PATH SAVEPATH, where PATH is the path up until the daily folders from empatica start, and SAVEPATH is the path where the new files will be created. This script will create one file per day, merging the different measurements in one table. 
3. run the script ./src/preprocess/behavioral/**step4_aggregate_empatica.py** PATH SAVEPATH, where PATH is the path where all the empatica files are, and SAVEPATH is the path where the new files will be created. This script will compute basic statistics on the different measurements and aggregate the data per day. 

## Quality check
The wristband quality check is the percentage of data loss within a day. 
1. Run the script ./src/quality_check/**quality_check_empatica.py**. The script takes one positional argument, the path to the folder where data from all days are stored. 

# eyetracker data

Eyetracker data comes from the EyeLink 1000 eye tracker in AMI centre. It is a fMRI simultaneous recording of eye movements and fixations. 

## Preprocessing
Preprocessing these data implies: organizing the files with the correct naming scheme, converting the data, checking the quality, and computing the blinking ratio. 

1. Transfer the files from the EyeLink computer in the AMI centre using the getfile icon in the stimulus computed. Save the files in the MRI folder and change the name using the scheme **sub-##_day-DAY_task-TASK_device-eyetracker.edf**
2. Install the visualEDF2ASC converter from the manufacturer.
3. After the installation open the converter and select all .edf files, then press convert. New .asc files will be created in the same folders as the .edf files.
4. Copy the files from that folder to the BIDS folder. The script **step8_organize_eyetrack.py** PATH SAVEPATH may help with that. 
5. Extract the relevant information from the eyetracker file with the **step9_extract_eyetracker-info.py** PATH, where PATH refers to the BIDS folder. The script will extract information about the fixation, saccades, and blinks according to https://risoms.github.io/mdl/docs/build/manual/EyeLink%201000%20Plus%20User%20Manual%201.0.12.pdf
6. Compute the % of sleeping time in the scanner according to the blink information. Run the script **step10_compute_blinks.py** PATH SAVEPATH, where PATH is where the extracted information from step 5 is saved, and SAVEPATH is the folder where the % of sleeping time in the scanner will be stored. This script will compute the proportion of time that a subject was having microsleeps in the MRI scanner. 

## Quality check
Here, the eyetracker data is most useful detecting the moments of microsleeps in the MRI scanner in the resting-state task. However, we should also check the quality of the data in the other tasks. To do so, run the script quality_eyetrack.py PATH, SAVEPATH, where PATH is the folder where the information from preprocessing step 5 is stored. The quality_eyetrack.py script will then plot the distribution of the duration of fixation points (i.e. how long the eyes were fixed in one point). Take a look at these distributions and compare the values within the sessions, try to spot if there are some noticeable changes in the distributions (e.g. absent distributions). Although the distributions are not always the same, they do resemble and there should not be contrasts too evident between tasks within a session. 

Given the eyetracker data main purpose, we also plot the eye position in the x-asis during the fixation points during the resting-state MRI. These plots will help understand the data quality. Check the length and the spikes. 
