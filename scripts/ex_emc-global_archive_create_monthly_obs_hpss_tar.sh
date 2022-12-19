#!/bin/sh
set -x

##################################################
# This script creates monthly HPSS tar files for
# archived global obs data.
##################################################

for obs in $obs_list; do
    cd $DATA
    python ${USHemc_global_archive}/create_monthly_obs_hpss_tar.py --yearmon=${TAR_YYYY}${TAR_mm} --archdir=$ARCHINobs --hpssdir=$HPSSobs --obs=$obs
done
