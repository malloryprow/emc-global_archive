#!/bin/sh
set -x

##################################################
# This script runs the emc_global-archive code
# to archive data from various global models.
##################################################

for model in $model_list; do
    if [ $model = "ecm" ];    then cycles="00 12";       fhrmin=0; fhrmax=240; fhrinc=6; fi
    if [ $model = "ecmg4" ];  then cycles="00 12";       fhrmin=0; fhrmax=240; fhrinc=6;  fi
    if [ $model = "gfs" ];    then cycles="00 06 12 18"; fhrmin=0; fhrmax=384; fhrinc=3;  fi
    if [ $model = "eagle_solo" ]; then cycles="00 06 12 18"; fhrmin=0; fhrmax=384; fhrinc=6;  fi
    for cycle in $cycles ; do
        cd $DATA
        python ${USHemc_global_archive}/get_model_data.py --date=$IDATE --archdir=$ARCHOUTmodel --rundir=$DATA --model=$model --cycle=$cycle --fhrmin=$fhrmin --fhrmax=$fhrmax --fhrinc=$fhrinc
    done
done
