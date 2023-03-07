#!/bin/bash -l
#SBATCH --time=02:20:00 
#SBATCH --mem-per-cpu=30G
#SBATCH -o /m/cs/scratch/networks-pm/denoise-%j.out

subject=$1
task=$2
strategy=$3
module load matlab
module load fsl
source $FSLDIR/etc/fslconf/fsl.sh
module load anaconda/2020-04-tf2

echo ${subject} 
echo ${task} 
echo ${strategy}

matlab -nodesktop -nosplash -nojvm -r "cd('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/preprocess/mri');  detrend('$subject', '$task', '$strategy'); quit"

python denoise.py ${subject} ${task} ${strategy}
