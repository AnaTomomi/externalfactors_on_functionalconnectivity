# effects_externalfactors_on_functionalconnectivity
This repository contains the code and instructions to analyze the data collected for the article "Effects of daily environmental, physiological, and lifestyle factors on functional brain connectivity", as registered in https://osf.io/qz5tw

# 1. Project description
This project follows one subject for 133 days, collecting brain activity, cognitive, and behavioral data from different sources. We collect fMRI data from attention, working memory, resting-state, and movie-watching conditions. We also collect sleep, activity, and physiology data (HR, HRV) from wearables, mood data from EMA on smartphones, and cognitive data (attention and working memory). The main goal is to understand
- Q1: How do behavioral, physiological, and lifestyle factors experienced by the individual on the previous day affect today’s functional brain connectivity patterns? 
- Q2: Can behavioral, physiological and lifestyle factors influence functional connectivity beyond the previous day, and up to the preceding fifteen days? 

# 2. Subfolder explanations
There are ___ main folders in the repository:

# 3. How to run
1. Sequest access to the data. The data is openly available for research purposes, however it is personal data, so it is protected by the GDPR. Please request access to it by writing to researchdata@aalto.fi.

2. Start preprocessing. We need to preprocess the data according to its source. 
  a. Cognitive data: cognitive data are the files produced by the presentation software. To preprocess these files, please run the scripts in ./src/preprocess/cognitive
  b. Behavioral data: behavioral data are the files produced by the different wearables and smartphones. To preprocess these files, please run the scripts in ./src/preprocess/behavioral
  c. MRI data: MRI data are the files taken in the MRI scanner. To preprocess these files, please run the scripts in ./src/preprocess/mri
Each folder contains instructions for running the scripts. Please make sure to change the paths accordingly. Please note that each script name starts with step#_ and this is the cue to know in which order the scripts should be called

3. Start the analysis. Our work has eight hypothesis. Therefore, we have divided the analysis into eight subfolders, so you do not need to run all the analysis. To run a particular analysis, please go to the subfolder ./src/analysis/ and select the folder. Again, you will find different scripts with the step#_ name, so it should be straightforward.

4. Visualize. Our work has eight hypothesis and a few extra supplementary analysis. Therefore, we have divided the visualization into eleven subfolders. To visualize a particular result, please go to the subfolder ./src/visualization/ and select the folder. Again, you will find different scripts with the step#_ name, so it should be straightforward.
