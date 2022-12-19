#!/bin/sh
set -x

##################################################
# This script runs the emc_global-archive code
# to archive the observation data.
##################################################

for obs in $obs_list; do
    cd $DATA
    python ${USHemc_global_archive}/get_obs_data.py --date=$IDATE --archdir=$ARCHOUTobs --rundir=$DATA --obs=$obs
done
