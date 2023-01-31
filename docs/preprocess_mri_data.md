# Steps

1. Download the MRI files and paste them in the directory. Both the directory and the file should be named YYYYMMDD
2. Run the script . /effects_externalfactors_on_functionalconnectivity/src/preprocess/mri/step0_oraganize_mrifiles.sh YYYYMMDD
3. Run the step1_DICOM2NIFTI.py. Remember to modify the date and the subject accordingly
4. If it is the first time, run the step2_BIDSformat.py script. If it is not, open the file /m/cs/project/networks-pm/mri/fast_prepro_bids/participants.tsv and add the participant to the file. Add also the date where the image was taken. Make sure to do this in both folders (scratch and project) where the BIDSes are.
5. Run step3_anonymize.sh PATH, where PATH is the subject directory where the .nii files are stored
6. Validate the BIDS folder
7. Copy the folder (or new, missing bits) to scratch Discard the first 5 volumes of the image. Use the script . /effects_externalfactors_on_functionalconnectivity/src/preprocess/mri/step4_discardvolumes.sh SUBJECT, where SUBJECT should be in the "sub-XX" format and XX is the consecutive number of the subject to preprocess. 
9. Run sbatch /effects_externalfactors_on_functionalconnectivity/src/preprocess/mri/step5_fmriprep.sh. Make sure to modify the subject and the temporal folder, which should be clean, from scrtach.
10. Cut the biopac signal using the script 
