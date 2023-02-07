#!/bin/bash
#SBATCH --time=2-00:00:00
#SBATCH --mem=30G
#SBATCH --array=1
#SBATCH --output=/m/cs/scratch/networks-pm/fmriprep_sub07-%j.out
#SBATCH --cpus-per-task=4

module load singularity-fmriprep/22.1.0
singularity_wrapper exec fmriprep /m/cs/scratch/networks-pm/pm/  /m/cs/scratch/networks-pm/pm_preprocessed/ -w  /m/cs/scratch/networks-pm/temp/ participant --participant-label sub-07 --fs-no-reconall --output-spaces MNI152NLin6Asym:res-2 --fs-license-file /scratch/shareddata/set1/freesurfer/license.txt
