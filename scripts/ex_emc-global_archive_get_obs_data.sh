#!/bin/sh
set -x

##################################################
# This script runs the emc_global-archive code
# to archive the observation data.
##################################################

cd $DATA
for obs in $obs_list; do
    python ${USHemc_global_archive}/get_obs_data.py --date=$IDATE --archdir=$ARCHOUTobs --rundir=$DATA --obs=$obs
done
