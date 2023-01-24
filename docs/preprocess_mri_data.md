# Steps

1. Download the MRI files and paste them in the directory. Both the directory and the file should be named YYYYMMDD
2. Run the script . /effects_externalfactors_on_functionalconnectivity/src/preprocess/mri/step0_oraganize_mrifiles.sh YYYYMMDD
3. Run the step1_DICOM2NIFTI.py. Remember to modify the date and the subject accordingly
4. If it is the first time, run the step2_BIDSformat.py script. If it is not, open the file /m/cs/project/networks-pm/mri/fast_prepro_bids/participants.tsv and add the participant to the file. Add also the date where the image was taken
5. Run step3_anonymize.sh PATH, where PATH is the subject directory where the .nii files are stored
6. Validate the BIDS folder
7. Copy the folder (or new, missing bits) to scratch /m/cs/scratch/networks-pm/fast_prepro_bids. You can use the command cp -R /m/cs/project/networks-pm/mri/fast_prepro_bids/sub-XXX/ /m/cs/scratch/networks-pm/pm/sub-XXX where XXX is the session
8. Cut the washout parts of each image? 
9. Run sbatch /effects_externalfactors_on_functionalconnectivity/src/preprocess/mri/step4_fmriprep.sh. Make sure to modify the subject and the temporal folder, which should be clean.
10. 
