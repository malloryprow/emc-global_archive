#!/bin/sh
set -x

##################################################
# This script gets monthly HPSS tar files
# for model data.
# Command line agruments:
#       1 - YYYYmm, in form of YYYYmm
##################################################

# Command line arguments
export YYYYmm=${1:-`date +%Y%m`}

# Set code paths
export HOMEemc_global_archive=${HOMEemc_global_archive:-`eval "cd ../;pwd"`}

# Set paths
export ARCHIVE_dir=/lfs/h2/emc/vpppg/noscrub/$USER/archive2/model_data
export HPSS_dir=/NCEPDEV/emc-global/5year/$USER/model_data

# Load modules
source ${HOMEemc_global_archive}/versions/run.ver
module reset
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}
module load intel/${intel_ver}
module load python/${python_ver}

# Run
for model in gfs cmc fno ukm ecm cdas jma cfsr gefsc gefsm ncmrwf ecmg4; do
    if [ $model = "cdas" ];   then cycles="00";          fi
    if [ $model = "cfsr" ];   then cycles="00";          fi
    if [ $model = "cmc" ];    then cycles="00 12";       fi
    if [ $model = "ecm" ];    then cycles="00 06 12 18"; fi
    if [ $model = "ecmg4" ];  then cycles="00 12";       fi
    if [ $model = "fno" ];    then cycles="00 12";       fi
    if [ $model = "gefsc" ];  then cycles="00 06 12 18"; fi
    if [ $model = "gefsm" ];  then cycles="00 12";       fi
    if [ $model = "gfs" ];    then cycles="00 06 12 18"; fi
    if [ $model = "jma" ];    then cycles="00 12";       fi
    if [ $model = "ncmrwf" ]; then cycles="00 12";       fi
    if [ $model = "ukm" ];    then cycles="00 12";       fi
    for cycle in $cycles ; do
        python ${HOMEemc_global_archive}/ush/get_monthly_model_hpss_tar.py --yearmon=$YYYYmm --archdir=$ARCHIVE_dir --hpssdir=$HPSS_dir  --model=$model --cycle=$cycle
    done
done
