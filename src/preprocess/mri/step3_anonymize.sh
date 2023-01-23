#!/bin/bash

module load fsl
source $FSLDIR/etc/fslconf/fsl.sh
source /m/cs/scratch/networks-pm/software/deface/bin/activate

find $1 -type f -name '*_T1w.nii' -print -exec pydeface {} --outfile {} --force \;

