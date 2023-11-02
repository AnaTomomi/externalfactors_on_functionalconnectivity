#!/bin/bash
#SBATCH --time=00:40:00
#SBATCH --mem=10G
#SBATCH --array=1-96
#SBATCH --output=/m/cs/scratch/networks-pm/jobs/H5-fakecorr-%j.out
#SBATCH --cpus-per-task=4

n=$SLURM_ARRAY_TASK_ID
variants=`sed "${n}q;d" nodes.txt`

module load anaconda/2023-01
export PYTHONUNBUFFERED=true
python3 /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis/H5/compute_fake_corr.py $variants
