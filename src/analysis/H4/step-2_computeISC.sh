#!/bin/bash
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --array=1-102
#SBATCH --output=/m/cs/scratch/networks-pm/jobs/mantel-%j.out
#SBATCH --cpus-per-task=4

n=$SLURM_ARRAY_TASK_ID
variants=`sed "${n}q;d" variants.txt`

module load anaconda/2023-01
python3 /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis/H4/computeISC.py $variants
