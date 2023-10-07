#!/bin/bash
#SBATCH --time=08:00:00
#SBATCH --mem=32G
#SBATCH --array=121-145
#SBATCH --output=/m/cs/scratch/networks-pm/jobs/beta-%j.out
#SBATCH --cpus-per-task=8

n=$SLURM_ARRAY_TASK_ID
variants=`sed "${n}q;d" variants.txt`

module load anaconda/2023-01
python3 /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis/H1/compute_betaseries.py $variants
