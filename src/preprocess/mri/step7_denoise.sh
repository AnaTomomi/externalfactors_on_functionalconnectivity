#!/bin/bash -l
#SBATCH --time=03:00:00 
#SBATCH --mem-per-cpu=10G
#SBATCH -o /m/cs/scratch/networks-pm/denoise-%j.out

subject=$1
task=$2
strategy=$3
module load matlab
module load fsl
source $FSLDIR/etc/fslconf/fsl.sh

matlab -nodesktop -nosplash -nojvm -r "cd('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/preprocess/mri');  denoise('$subject', '$task', '$strategy'); quit"

