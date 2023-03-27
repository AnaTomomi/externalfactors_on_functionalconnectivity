#!/bin/bash -l
#SBATCH --time=00:40:00 
#SBATCH --mem-per-cpu=45G
#SBATCH -o /m/cs/scratch/networks-pm/jobs/denoise-%j.out

subject=$1
task=$2
strategy=$3
FWHM=2.5532 #This number is FWHM/2.35
denoisepath=/m/cs/scratch/networks-pm/pm_denoise

module load matlab
module load fsl
source $FSLDIR/etc/fslconf/fsl.sh
module load anaconda/2023-01

echo ${subject} 
echo ${task} 
echo ${strategy}

[ ! -d "${denoisepath}/${subject}" ] && mkdir -p "${denoisepath}/${subject}"

matlab -nodesktop -nosplash -nojvm -r "cd('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/preprocess/mri');  detrend('$subject', '$task', '$strategy'); quit"
echo "signals detrended"

python denoise.py ${subject} ${task} ${strategy}
echo "signals denoised"

fslmaths ${denoisepath}/${subject}/${subject}_task-${task}_SGdetrend_${strategy}_HPF.nii -kernel gauss $FWHM -fmean ${denoisepath}/${subject}/${subject}_task-${task}_SGdetrend_${strategy}_HPF_smooth-6mm.nii

gunzip -d ${denoisepath}/${subject}/${subject}_task-${task}_SGdetrend_${strategy}_HPF_smooth-6mm.nii #decompress
