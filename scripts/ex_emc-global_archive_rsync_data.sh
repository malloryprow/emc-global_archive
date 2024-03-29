#!/bin/sh
set -x

##################################################
# This script syncs data across WCOSS2 machines
##################################################

for dir in model_data obs_data fit2obs_data evs_data; do
    cd $DATA
    python ${USHemc_global_archive}/rsync_archive.py --archdir=$ARCHIN/$dir
done

exit
