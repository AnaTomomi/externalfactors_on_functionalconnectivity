# What?
This folder contains all results (uncorrected and corrected for multiple comparisons) for the eight hypothesis. The results are organized in .csv, .xlsx, and .mat files. They follow some naming conventions trying to imitate the BIDS-format, so reading them should be easy. Keep reading to find out how.

# Naming conventions
We tried to follow this BIDS-like naming format for intermediate results too, but keep in mind that this work tested several variants of preprocessing and thresholding, as well as eight hypothesis, so the names are long. Here is the rosetta stone for understanding the files. If the names contain:

- **24HMP-8Phys-Spkike**: the results have been derived using a preprocessing stratefy where we regressed the following confounds from the fMRI data: 24 Friston head movement parameters, 8 physiological confounds (CSF and WM-related), and the Spike confound as preprocessed by fmriprep. This variant is presented in the main manuscript. 
- **24HMP-8Phys-4GSR-Spkike**: the results have been derived using a preprocessing stratefy where we regressed the following confounds from the fMRI data: 24 Friston head movement parameters, 8 physiological confounds (CSF and WM-related), 4 global signal confounds, and the Spike confound as preprocessed by fmriprep. This variant is used for the supplementary figures. 
- **seitzeman-set1**: the results are derived using the seitzman-set1 parcellation (see https://doi.org/10.1016/j.neuroimage.2019.116290). This parcellation uses spheres.
- **seitzeman-set2**: the results are derived using the seitzman-set2 parcellation (see https://doi.org/10.1016/j.neuroimage.2019.116290). 
- **thr-10**: the results are derived by thresholding the network at 10%.
- **thr-20**: the results are derived by thresholding the network at 20%.
- **thr-30**: the results are derived by thresholding the network at 30%.
- **global-eff**: results derived for global-efficiency measurements.
- **parti-coeff**: results derived for the participation coefficient.
- **ref-links**: results derived for the individual links (H1 to H3 only).
- **BHcorrected**: the results have been corrected for multiple comparisons using the Benjamin and Hochberg method. If there is no mention of this label, the results are **uncorrected**
- **finaltable**: the results are organized and only the values surviving the multiple comparison correction are shown. These tables are also shown in the Supplementary Tables. 

For example, the file __./results/H3/global-eff_24HMP-8Phys-Spike_HPF_seitzman-set1_thr-30.csv__ contains the results for Hypothesis 3 (rs-fMRI related). The data was preprocessed by regressing 24 Friston head movement parameters, 8 physiological confounds (CSF and WM-related), and the Spike confound as preprocessed by fmriprep. These results are for the global efficiency of the networks as computed using the seitzman-set1 parcellation. The network was thresholded at 30% before the global efficiency computation (see methods). These results have not yet been corrected for multiple comparisons. 

***NOTE: Statistical values for H5, H6, and H7 are in .mat files in a 3D array of (variables, lags, networks)***

# Naming conventions for H4 and H8

H4 and H8 are special because the models test each behavioral or physiological variable individually, so the name of the variable would be in the title. 

## H4:
H4 contains mostly json files with statistics and a couple of excel files. The json files follow a similar logic, if the name contains:

- mantel-ak: they refer to mantel tests run with the AnnaKarenina model.
- mantel-nn: they refer to mantel tests run with the NearestNeighbors model.

In addition, there are two excel tables: H4_finaltable.xlsx which are the organized results shown in the paper and H4_stability, which lists the stability results shown in the Supplementary Information.

## H8:
H8 results are divided in four subfolders, depending on the sliding window used in the analysis. Yet, all files follow this naming conventions:

- **decoder**: results from the decoder (see https://doi.org/10.1073/pnas.2110474118). No comparison with any external factor yet.
- the number next to the name of the variable refers to the lag.
- **step-X**: the sliding window step (1TR, 2TR, or 4TR).
- **tstat**: T-statistic
- **corrp**: corrected p-value

# Supplementary results
The folder contains results for the GLM supplementary analysis, as shown in the Supplementary Figure 42. In addition, the folder contains the framewise displacement values (as computed by fmriprep) for all the sessions and tasks. This data is plotted in the Supplementary Figure 15. 
