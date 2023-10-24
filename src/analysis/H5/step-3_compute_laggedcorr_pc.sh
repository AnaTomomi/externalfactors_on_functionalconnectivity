#!/bin/bash
#SBATCH --time=01:30:00
#SBATCH --mem=20G
#SBATCH --array=1-4
#SBATCH --output=/m/cs/scratch/networks-pm/jobs/H5-%j.out
#SBATCH --cpus-per-task=4

n=$SLURM_ARRAY_TASK_ID
variants=`sed "${n}q;d" options.txt`

module load anaconda/2023-01
export PYTHONUNBUFFERED=true
python3 /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis/H5/compute_lagged_corr_pc.py $variants
