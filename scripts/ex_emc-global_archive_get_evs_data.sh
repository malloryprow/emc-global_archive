#!/bin/sh
set -x

##################################################
# This script runs the emc_global-archive code
# to archive the EVS large stat files.
##################################################

for model in $evs_model_list; do
    cd $DATA
    python ${USHemc_global_archive}/get_evs_data.py --date=$VDATE --archdir=$ARCHOUTevs --rundir=$DATA --model=$model
done
