#!/bin/sh
set -x

##################################################
# This script creates monthly HPSS tar files for
# archived global model data.
##################################################

for model in $model_list; do
    if [ $model = "ecm" ];    then cycles="00 06 12 18"; fi
    if [ $model = "ecmg4" ];  then cycles="00 12";       fi
    if [ $model = "gfs" ];    then cycles="00 06 12 18"; fi
    for cycle in $cycles ; do
        cd $DATA
        python ${USHemc_global_archive}/create_monthly_model_hpss_tar.py --yearmon=${TAR_YYYY}${TAR_mm} --archdir=$ARCHINmodel --hpssdir=$HPSSmodel --model=$model --cycle=$cycle
    done
done
