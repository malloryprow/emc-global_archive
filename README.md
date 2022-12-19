# emc-global_archive

This is code is used to archive the GFS and other international global determinstic models, observations, and fit2obs files. It is set up to run on WCOSS2.

Set up:

Change directories to "emc-global_archive/sorc" (cd gfs-legacy_verif_v25/sorc)
Execute the script "build.src" (./build.src); this compiles the Fortran codes

Run:

The scripts to run are in emc-global_archive/ecf. For whichever script you wish to run, make sure the configuration is set up as needed. Then submit the jobs to the queue using "qsub".
