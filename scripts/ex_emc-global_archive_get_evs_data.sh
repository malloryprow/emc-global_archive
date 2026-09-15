#!/bin/sh
set -x

##################################################
# This script runs the emc_global-archive code
# to archive the EVS large stat files.
##################################################

for component in $evs_component_list; do
    cd $DATA
    python ${USHemc_global_archive}/get_evs_data.py --date=$VDATE --archdir=$ARCHOUTevs --rundir=$DATA --component=$component
done
