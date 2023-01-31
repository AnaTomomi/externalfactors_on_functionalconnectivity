#! user/bin/bash

subject=$1
origpath=/m/cs/project/networks-pm/mri/fast_prepro_bids
path=/m/cs/scratch/networks-pm/pm

module load fsl
source $FSLDIR/etc/fslconf/fsl.sh

cp -R ${origpath}/${subject} ${path}/${subject}

fslroi ${path}/${subject}/func/${subject}_task-pvt_bold.nii ${path}/${subject}/func/${subject}_task-pvt_bold.nii 5 1116
gzip -df ${path}/${subject}/func/${subject}_task-pvt_bold.nii.gz
echo "PVT done"
fslroi ${path}/${subject}/func/${subject}_task-resting_bold.nii ${path}/${subject}/func/${subject}_task-resting_bold.nii 5 1102
gzip -df ${path}/${subject}/func/${subject}_task-resting_bold.nii.gz
echo "resting done"
fslroi ${path}/${subject}/func/${subject}_task-movie_bold.nii ${path}/${subject}/func/${subject}_task-movie_bold.nii 5 1059
gzip -df ${path}/${subject}/func/${subject}_task-movie_bold.nii.gz
echo "movie done"
fslroi ${path}/${subject}/func/${subject}_task-nback_bold.nii ${path}/${subject}/func/${subject}_task-nback_bold.nii 5 614
gzip -df ${path}/${subject}/func/${subject}_task-nback_bold.nii.gz
echo "nback done"
