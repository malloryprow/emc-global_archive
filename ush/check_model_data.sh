#!/bin/sh
set -x

##################################################
# This script runs the EMC_global-archive code
# to check the archived model data.
# Command line agruments:
#       1 - PDY, in form of YYYYmmdd
#       2 - cyc, in form of HH
##################################################

# Command line arguments
export PDY=${1:-`date +%Y%m%d`}
export cyc=${2:-`date +%H`}

# Set code paths
export HOMEemc_global_archive=${HOMEemc_global_archive:-`eval "cd ../;pwd"`}

# Set output paths
export ARCHIVE_dir=/lfs/h2/emc/vpppg/noscrub/$USER/archive/model_data
export pid=${pid:-$$}
export jobid=check_model_data.${pid}
export RUN_dir=/lfs/h2/emc/stmp/$USER/${jobid}
mkdir -p $RUN_dir

# Load modules
source ${HOMEemc_global_archive}/versions/run.ver
module reset
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}
module load intel/${intel_ver}
module load python/${python_ver}

# Run
for model in gfs cmc fno ukm ecm cdas jma cfsr ncmrwf ecmg4; do
    if [ $model = "cdas" ];   then fhrmin=0; fhrmax=384; fhrinc=24; fi
    if [ $model = "cfsr" ];   then fhrmin=0; fhrmax=384; fhrinc=24; fi
    if [ $model = "cmc" ];    then fhrmin=0; fhrmax=240; fhrinc=12; fi
    if [ $model = "ecm" ];    then fhrmin=0; fhrmax=240; fhrinc=12; fi
    if [ $model = "ecmg4" ];  then fhrmin=0; fhrmax=240; fhrinc=6;  fi
    if [ $model = "fno" ];    then fhrmin=0; fhrmax=180; fhrinc=12; fi
    if [ $model = "gefsc" ];  then fhrmin=0; fhrmax=384; fhrinc=6;  fi
    if [ $model = "gefsm" ];  then fhrmin=0; fhrmax=384; fhrinc=6;  fi
    if [ $model = "gfs" ];    then fhrmin=0; fhrmax=384; fhrinc=3;  fi
    if [ $model = "jma" ];    then fhrmin=0; fhrmax=72;  fhrinc=24; fi
    if [ $model = "ncmrwf" ]; then fhrmin=0; fhrmax=240; fhrinc=12; fi
    if [ $model = "ukm" ];    then fhrmin=0; fhrmax=144; fhrinc=12; fi
    if [ $model = "ecm" ]; then
        if [ $cyc = "06" ] -o [ $cyc = "18" ]; then
            fhrmax=0
        fi
    fi
    python ${HOMEemc_global_archive}/ush/check_model_data.py --date=$PDY --archdir=$ARCHIVE_dir --rundir=$RUN_dir --model=$model --cycle=$cyc --fhrmin=$fhrmin --fhrmax=$fhrmax --fhrinc=$fhrinc
done

exit
