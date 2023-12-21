After all data has been preprocessed, it is time to start running the analysis. All scripts needed are in the analysis folder. Common scripts or functions that are needed for most hypothesis are in the analysis folder. In addition, there is one folder per hypothesis, where specifics like the variables are preconfigured. Remember that there are 8 different hypothesis, so we will go in order.

# General scripts
To run the analysis, we need to generate the atlases. Here, we use the atlas in https://doi.org/10.1016/j.neuroimage.2019.116290. 
1. Run the script **generate_SeitzmanAtlas.m** according to the paper. This may need to run twice, first for seitzman-set1 and then for seitzman-set2. 

# H1: PVT
The first hypothesis states "fluctuations in sleep patterns are correlation with functional connectivity within the FPN, DMN, somatomotor, and CON during sustained attention".
0. Compute the behavioral data for the PVT task. Use the function *get_behav_data_tasks* in the **utils.py** general script to do so. Use it with lag=1.
1. Generate the beta series. Use the script **step-1_compute_betaseries.sh** for that purpose. This script will compute the beta series for several denoise strategies and sessions. The script will use the python script **compute_betaseries.py** and the file *variants.txt* as a support. 
2. Compute the ROI-averaged betas and the adjacency networks by running the script **step-2_compute_averagedROIbetas.py**. Open the script to change the denoise strategies and the atlas. 
3. Generate the information about the parcellation for the specific data using the general script **extractROIsinfo.m**
4. Compute the global efficiency and participation coefficient by using the script **step-3_compute_graphmetrics.m**. Open the script to change the denoise strategies and the atlas. 
5. Organize the adjacency matrices into links to be regressed by using the script **step-4_matrix2links.m**. This script will automatically select the subset of links according to chosen networks. 
6. Compute the regression analysis by using the script **step-5_compute_regressions.sh**. This will automatically compute the values for global efficiency, participation coefficient, and links. This script uses the file *options.txt* as a support for inputting the denoise strategy and atlas name. It also uses the scripts *eff.R*, *pc.R*, and *links.R*.
7. Correct for multiple comparisons using the script **step-6_FDRcorr.m** 

# H2: N-back
The second hypothesis states "fluctuations in sleep and physical activity patterns are correlated with functional connectivity within the default mode, fronto-parietal, and somatomotor networks during working memory tasks".
0. Compute the behavioral data for the N-back task. Use the function *get_behav_data_tasks* in the **utils.py** general script to do so. Use it with lag=1. This is the same script as H1.
1. Generate the beta series. Use the script **step-1_compute_betaseries.sh** for that purpose. This script will compute the beta series for several denoise strategies and sessions. The script will use the python script **compute_betaseries.py** and the file *variants.txt* as a support. This script is the same as the H1, (i.e. look in the H1 folder). 
2. Compute the ROI-averaged betas and the adjacency networks by running the script **step2_compute_averagedROIbetas.py**. Open the script to change the denoise strategies and the atlas. This script is the same as the H1, (i.e. look in the H1 folder). Be sure to also change the contrast to 'twoback' for this task.
3. Generate the information about the parcellation for the specific data using the general script **extractROIsinfo.m**
4. Compute the network contrast by running **step-3_copute_nback_nets.py**. This step is important to obtain the contrast "2-back - 1-back" netowrk. 
5. Compute the global efficiency and participation coefficient by using the script **step-4_compute_graphmetrics.m**. Open the script to change the denoise strategies and the atlas. 
6. Organize the adjacency matrices into links to be regressed by using the script **step-5_matrix2links.m**. This script will automatically select the subset of links according to chosen networks. 
7. Compute the regression analysis by using the script **step-6_compute_regressions.sh**. This will automatically compute the values for global efficiency, participation coefficient, and links. This script uses the file *options.txt* as a support for inputting the denoise strategy and atlas name. It also uses the scripts *eff.R*, *pc.R*, and *links.R*.
8. Correct for multiple comparisons using the script **step-7_FDRcorr.m** 

# H3: Resting state
The third hypothesis states "fluctuations in sleep, autonomic nervous system activity, and mood patterns are correlated within functional connectivity in the default mode, fronto-parietal, and cingulo-opercular networks during resting-state fMRI".
0. Compute the behavioral data for the resting state. Use the function *get_behav_data_movie* in the **utils.py** general script to do so. Use it with lag=1.
1. Compute the ROI-averaged betas and the adjacency networks by running the script **step-1_compute_resting_conn.py**. Open the script to change the denoise strategies and the atlas. 
2. Generate the information about the parcellation for the specific data using the general script **extractROIsinfo.m**
3. Compute the global efficiency and participation coefficient by using the script **step-2_compute_graphmetrics.m**. Open the script to change the denoise strategies and the atlas. 
4. Organize the adjacency matrices into links to be regressed by using the script **step-3_matrix2links.m**. This script will automatically select the subset of links according to chosen networks. 
5. Compute the regression analysis by using the script **step-4_compute_regressions.sh**. This will automatically compute the values for global efficiency, participation coefficient, and links. This script uses the file *options.txt* as a support for inputting the denoise strategy and atlas name. It also uses the scripts *eff.R*, *pc.R*, and *links.R*.
6. Correct for multiple comparisons using the script **step-5_FDRcorr.m** 

# H4: Movie
The fourth hypothesis states " Increased similarity in the sleep, autonomic nervous system activity, or mood patterns between days is reflected as an increase in inter-day similarity within the frontoparietal, default mode, and salience networks during movie-watching tasks"
0. Compute the behavioral data for the movie data. Use the function *get_behav_data_movie* in the **utils.py** general script to do so. Use it with lag=1.
1. Compute the averaged-ROI timeseries for the movie data by running the script **step-1_compute_ISCmat-py**. Open the script to change the strategies and atlas.
2. Compute the Mantel test by running the script **step-2_computeISC.sh**. The *variants.txt* and *computeISC.py* scripts are needed. 
3. Summarize the results by running the script **step-3_generate_resultstable.py**

# H5: PVT
The fifth hypothesis states "Sleep patterns experienced over the past fifteen days are correlated with functional connectivity in the fronto-parietal, default mode, somatomotor, and cingulo-opercular networks during sustained attention tasks".
0. Compute the lagged behavioral data. Use the function *get_behav_data_15days* in the **utils.py** general script to do so. Use it with lag=16.
1. Create the surrogate data by running the script **create_fake_data.py** in the general folder.
2. Run the **step-1_compute_fake_corrs.sh** script to compute the correlations for global efficiency and participation coefficients with the surrogate data. The script uses the *nodes.txt* file and the *compute_fake_corr.py* script. 
3. Run the **step-2_compute_laggedcorr.sh** script to compute the lagged correlations for the participation coefficient. Warning! This process may take up to 2 days of computations. The script uses the *options.txt* file and the *compute_lagged_corr_pc.py* script. 
4. Run the **step-3_FDRcorr.m** to correct for multiple comparisons.

# H6: Nback
The sixth hypothesis states "Sleep and physical activity patterns experienced over the past fifteen days are correlated with functional connectivity in the default mod, fronto-parietal, and somatomotor networks during working memory tasks".
0. Compute the lagged behavioral data. Use the function *get_behav_data_15days* in the **utils.py** general script to do so. Use it with lag=16.
1. Create the surrogate data by running the script **create_fake_data.py** in the general folder. If you have created already the surrogate data, there is no need to do it again. 
2. Run the **step-1_compute_fake_corrs.sh** script to compute the correlations for global efficiency and participation coefficients with the surrogate data. The script uses the *nodes.txt* file and the *compute_fake_corr.py* script. 
3. Run the **step-2_compute_laggedcorr.sh** script to compute the lagged correlations for the participation coefficient. Warning! This process may take up to 2 days of computations. The script uses the *options.txt* file and the *compute_lagged_corr_pc.py* script. 
4. Run the **step-3_FDRcorr.m** to correct for multiple comparisons.

# H7: Resting state
The seventh hypothesis states "Sleep, autonomic nervous system activity, and mood patterns experienced over the past fifteen days are correlated with functional connectivity in the default mode, frontoparietal, and cingulo-opercular networks during resting-state fMRI".
0. Compute the lagged behavioral data. Use the function *get_behav_data_15days* in the **utils.py** general script to do so. Use it with lag=16.
1. Create the surrogate data by running the script **create_fake_data.py** in the general folder. If you have created already the surrogate data, there is no need to do it again. 
2. Run the **step-1_compute_fake_corrs.sh** script to compute the correlations for global efficiency and participation coefficients with the surrogate data. The script uses the *nodes.txt* file and the *compute_fake_corr.py* script. 
3. Run the **step-2_compute_laggedcorr.sh** script to compute the lagged correlations for the participation coefficient. Warning! This process may take up to 2 days of computations. The script uses the *options.txt* file and the *compute_lagged_corr_pc.py* script. 
4. Run the **step-3_FDRcorr.m** to correct for multiple comparisons.

# H8: Movie decoder
The eight and final hypothesis states "Between-days time-segment classification accuracy is explained by daily behavioral, physiological, and lifestyle factors".
1. Run the ISCToolbox and make sure to check the box that saves the matrices as memory maps.
2. Pre-compute the spheres to be used by running the script
3. Compute the decode-maps by running the script 
4. Merege the maps by running the script
5. 

# Supplementary analysis
