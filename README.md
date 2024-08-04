# Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological, and lifestyle factors on functional brain connectivity
This repository contains the code and instructions to analyze the data collected for the article "Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological, and lifestyle factors on functional brain connectivity", as registered in https://osf.io/qz5tw

# 1. Project description
This project follows one subject for 133 days, collecting brain activity, cognitive, and behavioral data from different sources. We collect fMRI data from attention, working memory, resting-state, and movie-watching conditions. We also collect sleep, activity, and physiology data (HR, HRV) from wearables, mood data from EMA on smartphones, and cognitive data (attention and working memory). The main goal is to understand
- Q1: How do behavioral, physiological, and lifestyle factors experienced by the individual on the previous day affect today’s functional brain connectivity patterns? 
- Q2: Can behavioral, physiological and lifestyle factors influence functional connectivity beyond the previous day, and up to the preceding fifteen days? 

# 2. Subfolder explanations
There are three main folders in the repository:

- docs: contains documentation on how to preprocess and analyze data to replicate the results published in the paper "Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological, and lifestyle factors on functional brain connectivity".
- results: results from the statistical tests run to test hypothesis H1-H8 and the supplementary results.
- src: source code to preprocess and analyze the data.

Each folder contains further explanations about their contents in their README files. 

# 3. How to replicate the results
1. Request access to the data. The data is openly available for research purposes, however it is personal data collected and stored in Europe, so it is protected by the GDPR. Visit https://zenodo.org/records/10571956 to request data access. If there are any questions, please write to researchdata@aalto.fi.

2. Start preprocessing. We need to preprocess the data according to its source. 
  a. **Cognitive data**: cognitive data are the files produced by the presentation software. To preprocess these files, please read the documentation in `./docs/preprocess_cognitive_data.md` run the scripts in `./src/preprocess/cognitive` 
  b. **Behavioral data**: behavioral data are the files produced by the different wearables and smartphones. To preprocess these files, please read the documentation in `./docs/preprocess_behavioral.md` and run the scripts in `./src/preprocess/behavioral`
  c. **MRI data**: MRI data are the files taken in the MRI scanner. To preprocess these files, please read the documentation in `./docs/preprocess_mri_data.m` and run the scripts in `./src/preprocess/mri`
Each folder contains instructions for running the scripts. Please make sure to change the paths accordingly. 
Please note that each script name starts with step#_ and this is the cue to know in which order the scripts should be called.

3. Start the analysis. Our work has eight hypotheses. Therefore, we have divided the analysis into eight subfolders, so you do not need to run all the analysis. To run a particular analysis, please read the documentation in `/docs/analysis.md`. Go to the subfolder `./src/analysis/` and select the folder for the hypotheses in question. Again, you will find different scripts with the step#_ name, so it should be straightforward. If detailed explanations are needed, read the analysis.md file in the docs folder.

4. Visualize. Our work has eight hypothesis and a few extra supplementary analysis. To visualize a particular result, please go to the subfolder `./src/visualization/` and select the script. Further documentation is provided in this folder. 

# 4. Extras
For convinience, ***we have also realeased the uncorrected results for each hypothesis in the ./results folder***. As ususal, there are eight folders, one for each hypothesis and one more for the supplementary results. Inside each folder, there are several files according to the denoise confounds used in cleaning the fMRI data (see the README.md file in the results folder). Results from H1, H2, H3, H5, H6, and H7 have three suffixes: global-eff for the global efficiency results, parti-coeff for the participation coefficient, and reg-links for the links. 

# 5. Citation
Please cite the following work: Triana AM, Salmitaival J, Hayward N, Saramäki J, Glerean E (2022) Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological, and lifestyle factors on functional brain connectivity. Preregistration at OSF: DOI 10.17605/OSF.IO/5HU9C

# 6. Questions?
No problem! Please contact ana.trianahoyos@aalto.fi. We'll try to help you the best we can. 
