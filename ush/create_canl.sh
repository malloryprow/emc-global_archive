#!/bin/sh
set -x

##################################################
# This script creates the common analysis between
# GFS analysis, CMC f00, UKM f00, and ECM f00.
# Command line agruments:
#       1 - PDY, in form of YYYYmmdd
##################################################

# Command line arguments
export PDY=${1:-`date +%Y%m%d`}

# Set code paths
export HOMEemc_global_archive=${HOMEemc_global_archive:-`eval "cd ../;pwd"`}

# Set paths
export ARCHIVE_dir=/lfs/h2/emc/vpppg/noscrub/$USER/archive/model_data
export pid=${pid:-$$}
export jobid=create_canl.${pid}
export RUN_dir=/lfs/h2/emc/stmp/$USER/${jobid}
mkdir -p $RUN_dir

# Load modules
source ${HOMEemc_global_archive}/versions/run.ver
module reset
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}
module load intel/${intel_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load python/${python_ver}

# Run
SENDARCH=NO
cycles="00 12"
for cycle in $cycles ; do
    python ${HOMEemc_global_archive}/ush/create_canl.py --date=$PDY --archdir=$ARCHIVE_dir --rundir=$RUN_dir --cycle=$cycle
    exit
done
