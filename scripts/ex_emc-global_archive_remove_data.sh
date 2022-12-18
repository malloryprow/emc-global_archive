#!/bin/sh
set -x

##################################################
# This script removes data across WCOSS2 machines
##################################################

# Remove model data
for model in $model_list; do
    if [ $model = "cdas" ];   then rm_back_hr=2184;  fi
    if [ $model = "cfsr" ];   then rm_back_hr=2184;  fi
    if [ $model = "cmc" ];    then rm_back_hr=2184;  fi
    if [ $model = "ecm" ];    then rm_back_hr=8088;  fi
    if [ $model = "ecmg4" ];  then rm_back_hr=2184;  fi
    if [ $model = "fno" ];    then rm_back_hr=2184;  fi
    if [ $model = "gfs" ];    then rm_back_hr=17616; fi
    if [ $model = "gefsc" ];  then rm_back_hr=2184;  fi
    if [ $model = "gefsm" ];  then rm_back_hr=2184;  fi
    if [ $model = "jma" ];    then rm_back_hr=2184;  fi
    if [ $model = "ncmrwf" ]; then rm_back_hr=2184;  fi
    if [ $model = "ukm" ];    then rm_back_hr=2184;  fi
    cd $DATA
    rCDATE=`$NDATE -$rm_back_hr ${PDY}00`
    rPDY=`echo $rCDATE |cut -c 1-8`
    python ${USHemc_global_archive}/remove_data.py --removedate=$rPDY --archdir=$ARCHIN/model_data/$model
done

# Remove obs data
for obs in $obs_list; do
    if [ $obs = "prepbufr_gdas" ];    then rm_back_hr=17616; fi
    if [ $obs = "prepbufr_nam" ];     then rm_back_hr=17616; fi
    if [ $obs = "prepbufr_rap" ];     then rm_back_hr=17616; fi
    if [ $obs = "ccpa_accum24hr" ];   then rm_back_hr=17616; fi
    if [ $obs = "ccpa_accum6hr" ];    then rm_back_hr=17616; fi
    if [ $obs = "nohrsc_accum24hr" ]; then rm_back_hr=17616; fi
    if [ $obs = "get_d" ];            then rm_back_hr=17616; fi
    if [ $obs = "osi_saf" ];          then rm_back_hr=17616; fi
    if [ $obs = "ghrsst_median" ];    then rm_back_hr=17616; fi
    if [ $obs = "OBSPRCP" ];          then rm_back_hr=17616; fi
    cd $DATA
    rCDATE=`$NDATE -$rm_back_hr ${PDY}00`
    rPDY=`echo $rCDATE |cut -c 1-8`
    if [ $obs = "prepbufr_gdas" ]; then
        python ${USHemc_global_archive}/remove_data.py --removedate=$rPDY --archdir=$ARCHIN/obs_data/prepbufr/gdas
    elif [ $obs = "prepbufr_nam" ]; then
        python ${USHemc_global_archive}/remove_data.py --removedate=$rPDY --archdir=$ARCHIN/obs_data/prepbufr/nam
    elif [ $obs = "prepbufr_rap" ]; then
        python ${USHemc_global_archive}/remove_data.py --removedate=$rPDY --archdir=$ARCHIN/obs_data/prepbufr/rap
    else
        python ${USHemc_global_archive}/remove_data.py --removedate=$rPDY --archdir=$ARCHIN/obs_data/$obs
    fi
done

# Remove fit-to-obs data
for model in $fit2obs_model_list; do
    if [ $model = "fnl" ]; then rm_back_hr=17616; fi
    cd $DATA
    rCDATE=`$NDATE -$rm_back_hr ${PDY}00`
    rPDY=`echo $rCDATE |cut -c 1-8`
    if [ $model = "fnl" ]; then
        python ${USHemc_global_archive}/remove_data.py --removedate=$rPDY --archdir=$ARCHIN/fit2obs_data/fnl/fits
        python ${USHemc_global_archive}/remove_data.py --removedate=$rPDY --archdir=$ARCHIN/fit2obs_data/fnl/horiz/anl
        python ${USHemc_global_archive}/remove_data.py --removedate=$rPDY --archdir=$ARCHIN/fit2obs_data/fnl/horiz/fcs
    fi
done
