# Steps

1. Download the MRI files and paste them in the directory. Both the directory and the file should be named **YYYYMMDD**
2. Run the script **. step0_oraganize_mrifiles.sh YYYYMMDD**
3. Run the step1_DICOM2NIFTI.py. Remember to modify the date and the subject accordingly
4. If it is the first time, run the **step2_BIDSformat.py** script. If it is not, open the file /m/cs/project/networks-pm/mri/fast_prepro_bids/participants.tsv and add the participant to the file. Add also the date where the image was taken. Make sure to do this in both folders (scratch and project) where the BIDSes are.
5. Run **step3_anonymize.sh PATH**, where PATH is the subject directory where the .nii files are stored
6. Validate the BIDS folder
7. Copy the folder (or new, missing bits) to scratch Discard the first and last 5 volumes of the image. Use the script **. step4_discardvolumes.sh SUBJECT**, where SUBJECT should be in the "sub-XX" format and XX is the consecutive number of the subject to preprocess. 
8. Run **sbatch step5_fmriprep.sh**. Make sure to modify the subject and the temporal folder, which should be clean, from scrtach.
9. Cut the biopac signal using the script **step6-3-1_HRdivide.m**. The script needs to be run in matlab.
10. Resample the biopac signal to volumes using the script **step6-3-2_HRpreprocess.m**. Again, this needs to be run in matlab
11. Cut the sequences again to match the volumes that were already cut in step 7 using the script **step6-3-3_HRcut.m**
12. Un-gunzip all the files that fmriprep has created, so that matlab does not have a problem reading them. You can use the command **gunzip *.nii.gz**
12. Denoise the files using **step7_denoise.sh SUBJECT TASK STRATEGY**, where SUBJECT has to be in the "sub-##" format, TASK refers to the fMRI task, and STRATEGY is one of the denoise strategies listed in the matlab file denoise.m. Strategies for this case are: 24HMP-8Phys-4GSR-Spike and 24HMP-8Phys-Spike
13. OPTIONAL: If you want to check the preprocessing, use the script **plot_preprocess.py** to do so.
