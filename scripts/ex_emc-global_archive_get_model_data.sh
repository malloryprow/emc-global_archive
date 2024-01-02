#!/bin/sh
set -x

##################################################
# This script runs the emc_global-archive code
# to archive data from various global models.
##################################################

for model in $model_list; do
    if [ $model = "cdas" ];   then cycles="00";          fhrmin=0; fhrmax=384; fhrinc=24; fi
    if [ $model = "cfsr" ];   then cycles="00";          fhrmin=0; fhrmax=384; fhrinc=24; fi
    if [ $model = "cmc" ];    then cycles="00 12";       fhrmin=0; fhrmax=240; fhrinc=12; fi
    if [ $model = "ecm" ];    then cycles="00 12";       fhrmin=0; fhrmax=240; fhrinc=6; fi
    if [ $model = "ecmg4" ];  then cycles="00 12";       fhrmin=0; fhrmax=240; fhrinc=6;  fi
    if [ $model = "fno" ];    then cycles="00 12";       fhrmin=0; fhrmax=180; fhrinc=12; fi
    if [ $model = "gefsc" ];  then cycles="00 06 12 18"; fhrmin=0; fhrmax=384; fhrinc=6;  fi
    if [ $model = "gefsm" ];  then cycles="00 12";       fhrmin=0; fhrmax=384; fhrinc=6;  fi
    if [ $model = "gfs" ];    then cycles="00 06 12 18"; fhrmin=0; fhrmax=384; fhrinc=3;  fi
    if [ $model = "gfs_wcoss2_para" ];    then cycles="00 06 12 18"; fhrmin=0; fhrmax=384; fhrinc=3;  fi
    if [ $model = "jma" ];    then cycles="00 12";       fhrmin=0; fhrmax=192;  fhrinc=24; fi
    if [ $model = "ncmrwf" ]; then cycles="00 12";       fhrmin=0; fhrmax=240; fhrinc=12; fi
    if [ $model = "ukm" ];    then cycles="00 12";       fhrmin=0; fhrmax=144; fhrinc=12; fi
    for cycle in $cycles ; do
        cd $DATA
        python ${USHemc_global_archive}/get_model_data.py --date=$IDATE --archdir=$ARCHOUTmodel --rundir=$DATA --model=$model --cycle=$cycle --fhrmin=$fhrmin --fhrmax=$fhrmax --fhrinc=$fhrinc
    done
done
