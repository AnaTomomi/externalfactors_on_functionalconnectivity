# Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological, and lifestyle factors on functional brain connectivity
This repository contains the code and instructions to analyze the data collected for the article "Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological, and lifestyle factors on functional brain connectivity", as registered in https://osf.io/qz5tw

# 1. Project description
This project follows one subject for 133 days, collecting brain activity, cognitive, and behavioral data from different sources. We collect fMRI data from attention, working memory, resting-state, and movie-watching conditions. We also collect sleep, activity, and physiology data (HR, HRV) from wearables, mood data from EMA on smartphones, and cognitive data (attention and working memory). The main goal is to understand
- Q1: How do behavioral, physiological, and lifestyle factors experienced by the individual on the previous day affect today’s functional brain connectivity patterns? 
- Q2: Can behavioral, physiological and lifestyle factors influence functional connectivity beyond the previous day, and up to the preceding fifteen days? 

# 2. Subfolder explanations
There are three main folders in the repository:

- docs: contains documentation on how to preprocess and analyze data to replicate the results published in the paper "Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological, and lifestyle factors on functional brain connectivity".
- results: results from the statistical tests run to test hypothesis H1-H8. 
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
For convinience, ***we have also realeased the uncorrected results for each hypothesis in the ./results folder***. As ususal, there are eight folders, one for each hypothesis. Inside each folder, there are several files according to the denoise confounds used in cleaning the fMRI data (see naming convention). Results from H1, H2, H3, H5, H6, and H7 have three suffixes: global-eff for the global efficiency results, parti-coeff for the participation coefficient, and reg-links for the links. 

# 5. Naming conventions
All MRI files follow the BIDS format. The cofnitive and behavioral data also follows a BIDS-like format that should be straightforward to read. We tried to follow this BIDS-like naming format for intermediate results too, but keep in mind that this work tested several variants of preprocessing and thresholding, as well as eight hypothesis, so the names are long. Here is the rosetta stone for understanding the files. If the names contain:

- 24HMP-8Phys-Spkike: the results have been derived using a preprocessing stratefy where we regressed the following confounds from the fMRI data: 24 Friston head movement parameters, 8 physiological confounds (CSF and WM-related), and the Spike confound as preprocessed by fmriprep. This variant is presented in the main manuscript. 
- 24HMP-8Phys-4GSR-Spkike: the results have been derived using a preprocessing stratefy where we regressed the following confounds from the fMRI data: 24 Friston head movement parameters, 8 physiological confounds (CSF and WM-related), 4 global signal confounds, and the Spike confound as preprocessed by fmriprep. This variant is used for the supplementary figures. 
- seitzeman-set1: the results are derived using the seitzman-set1 parcellation (see https://doi.org/10.1016/j.neuroimage.2019.116290). This parcellation uses spheres.
- seitzeman-set2: the results are derived using the seitzman-set2 parcellation (see https://doi.org/10.1016/j.neuroimage.2019.116290). 
- thr-10: the results are derived by thresholding the network at 10%.
- thr-20: the results are derived by thresholding the network at 20%.
- thr-30: the results are derived by thresholding the network at 30%.
- global-eff: results derived for global-efficiency measurements.
- parti-coeff: results derived for the participation coefficient. 
- BHcorrected: the results have been corrected for multiple comparisons using the Benjamin and Hochberg method. If there is no mention of this label, the results are **uncorrected**
- finaltable: the results are organized and only the values surviving the multiple comparison correction are shown. These tables are also shown in the Supplementary Tables. 

For example, the file __./results/H3/global-eff_24HMP-8Phys-Spike_HPF_seitzman-set1_thr-30.csv__ contains the results for Hypothesis 3 (rs-fMRI related). The data was preprocessed by regressing 24 Friston head movement parameters, 8 physiological confounds (CSF and WM-related), and the Spike confound as preprocessed by fmriprep. These results are for the global efficiency of the networks as computed using the seitzman-set1 parcellation. The network was thresholded at 30% before the global efficiency computation (see methods). These results have not yet been corrected for multiple comparisons. 


# 5. Citation
Please cite the following work: Triana AM, Salmitaival J, Hayward N, Saramäki J, Glerean E (2022) Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological, and lifestyle factors on functional brain connectivity. Preregistration at OSF: DOI 10.17605/OSF.IO/5HU9C
