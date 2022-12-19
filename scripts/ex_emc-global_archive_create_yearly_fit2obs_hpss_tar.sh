#!/bin/sh
set -x

##################################################
# This script creates monthly HPSS tar files for
# archived global model data.
##################################################

for model in $fit2obs_model_list; do
    cd $DATA
    python ${USHemc_global_archive}/create_yearly_fit2obs_hpss_tar.py --year=${TAR_YYYY} --archdir=$ARCHINfit2obs --hpssdir=$HPSSfit2obs
done
