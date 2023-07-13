# eyetracker data

Eyetracker data comes from the EyeLink 1000 eye tracker in AMI centre. It is a fMRI simultaneous recording of eye movements and fixations. 

# Preprocessing
Preprocessing these data implies: organizing the files with the correct naming scheme, converting the data, checking the quality, and computing the blinking ratio. 

## Preprocessing steps
1. Transfer the files from the EyeLink computer in the AMI centre using the getfile icon in the stimulus computed. Save the files in the MRI folder and change the name using the scheme **sub-##_day-DAY_task-TASK_device-eyetracker.edf**
2. Install the visualEDF2ASC converter from the manufacturer.
3. After the installation open the converter and select all .edf files, then press convert. New .asc files will be created in the same folders as the .edf files.
4. Copy the files from that folder to the BIDS folder. The script step8_organize_eyetrack.py PATH SAVEPATH may help with that. 
5. Extract the relevant information from the eyetracker file with the step9_extract_eyetracker-info.py PATH, where PATH refers to the BIDS folder. The script will extract information about the fixation, saccades, and blinks according to https://risoms.github.io/mdl/docs/build/manual/EyeLink%201000%20Plus%20User%20Manual%201.0.12.pdf
6. Compute the % of sleeping time in the scanner according to the blink information. Run the script step10_compute_blinks.py PATH SAVEPATH, where PATH is where the extracted information from step 5 is saved, and SAVEPATH is the folder where the % of sleeping time in the scanner will be stored. This script will compute the proportion of time that a subject was having microsleeps in the MRI scanner. 

# Quality check
Here, the eyetracker data is most useful detecting the moments of microsleeps in the MRI scanner in the resting-state task. However, we should also check the quality of the data in the other tasks. To do so, run the script quality_eyetrack.py PATH, SAVEPATH, where PATH is the folder where the information from preprocessing step 5 is stored. The quality_eyetrack.py script will then plot the distribution of the duration of fixation points (i.e. how long the eyes were fixed in one point). Take a look at these distributions and compare the values within the sessions, try to spot if there are some noticeable changes in the distributions (e.g. absent distributions). Although the distributions are not always the same, they do resemble and there should not be contrasts too evident between tasks within a session. 

Given the eyetracker data main purpose, we also plot the eye position in the x-asis during the fixation points during the resting-state MRI. These plots will help understand the data quality. Check the length and the spikes. 
