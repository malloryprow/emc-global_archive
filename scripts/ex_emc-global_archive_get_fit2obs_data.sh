#!/bin/sh
set -x

##################################################
# This script runs the emc_global-archive code
# to archive the fit-to-obs data.
##################################################

cd $DATA
for model in $fit2obs_model_list; do
    python ${USHemc_global_archive}/get_fit2obs_data.py --date=$IDATE --archdir=$ARCHOUTfit2obs --rundir=$DATA --model=$model
done
