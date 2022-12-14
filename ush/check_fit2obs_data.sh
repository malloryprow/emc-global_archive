#!/bin/sh
set -x

##################################################
# This script runs the EMC_global-archive code
# checks the archived fit-to-obs data.
# Command line agruments:
#       1 - PDY, in form of YYYYmmdd
##################################################

# Command line arguments
export PDY=${1:-`date +%Y%m%d`}
export cyc=${2:-`date +%H`}

# Set code paths
export HOMEemc_global_archive=${HOMEemc_global_archive:-`eval "cd ../;pwd"`}

# Set output paths
export ARCHIVE_dir=/lfs/h2/emc/vpppg/noscrub/$USER/archive/fit2obs_data
export pid=${pid:-$$}
export jobid=check_fit2obs_data.${pid}
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
for model in fnl; do
    python ${HOMEemc_global_archive}/ush/check_fit2obs_data.py --date=$PDY --cycle=$cyc --archdir=$ARCHIVE_dir --rundir=$RUN_dir --model=$model
done
