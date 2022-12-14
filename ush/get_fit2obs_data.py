"""
About:
        This script gets the fit-to-obs files.
        It will look for the files in COMROOT
        under the CFS, and if they are not there,
        it will check the shared storage. Gets files
        for models: gfs/fnl
Author(s):
	Mallory Row (mallory.row@noaa.gov)
History Log:
        November 2021 - Inital version
Command Line Agruments: 
        --date: optional, date (format YYYYmmdd) to run for,
                default: today
        --archdir: optional, path to archive directory,
                   default: /lfs/h2/emc/vpppg/noscrub/$USER/fit2obs_archive
        --rundir: optional, path to run directory,
                  default: /lfs/h2/emc/stmp/$USER/run_get_fit2obs_data
        --model: optional, model name
                 default: fnl
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import os
import sys
import datetime
import glob
import emc_global_archive_util as ega_util

print("\nBEGIN: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")

def usage():
    """! How to call this script.
    """
    filename = os.path.basename(__file__)
    print ("Usage: "+filename+" arg1 arg2\n"
           +"-h|--help               Display this usage statement\n"
           +"Arguments:\n"
           +"   --date=PDY              optional, "
           +"date (format YYYYmmdd) to run for, "
           +"default: today\n"
           +"   --archdir=ARCHIVE_DIR   optional, "
           +"path to archive directory, "
           +"default: /lfs/h2/emc/vpppg/noscrub/$USER/fit2obs_archive\n"
           +"   --rundir=RUN_DIR        optional, "
           +"default: /lfs/h2/emc/stmp/$USER/run_get_fit2obs_data\n"
           +"   --model=MODEL           optional, "
           +"default: fnl\n")
    sys.exit(1)

# Command line agrument information
cmd_line_args_dict = {
    '--date=': {
        'run_name': 'PDY',
        'default': datetime.datetime.today().strftime('%Y%m%d')
    },
    '--archdir=': {
        'run_name': 'ARCHIVE_DIR',
        'default': ('/lfs/h2/emc/vpppg/noscrub/'+os.environ['USER']
                    +'/fit2obs_archive')
    },
    '--rundir=': {
        'run_name': 'RUN_DIR',
        'default': ('/lfs/h2/emc/stmp/'+os.environ['USER']
                    +'/run_get_fit2obs_data')
    },
    '--model=': {
        'run_name': 'MODEL',
        'default': 'fnl'
    }
}

# Print usage statement
help_args = ('-h', '--help')
for help_arg in help_args:
    if help_arg in sys.argv:
        usage()
        sys.exit(0)

# Check number of command line arguments
if len(sys.argv[1:]) > 4:
    print("Too many agruments")
    usage()

# Set up dictionary for run settings
run_settings_dict = {}

# Run settings: hard coded
print("Hard coded settings...")
run_settings_dict['fnl_cycle_list'] = ['00', '06', '12', '18']
for run_name in list(run_settings_dict.keys()):
    print(run_name+' = '+str(run_settings_dict[run_name]))

# Run settings: command line arguments
print("Command line argument settings...")
for cmd_line_arg_name in list(cmd_line_args_dict.keys()):
    cmd_line_arg_opt_dict = cmd_line_args_dict[cmd_line_arg_name]
    cmd_line_arg_opt_run_name = cmd_line_arg_opt_dict['run_name']
    cmd_line_arg_opt_default = cmd_line_arg_opt_dict['default']
    if any(cmd_line_arg_name in arg for arg in sys.argv[1:]):
        for arg in sys.argv[1:]:
            if cmd_line_arg_name in arg:
                if cmd_line_arg_name == '--date=':
                    if len(arg.replace('--date=','')) != 8:
                        print("--date must be in YYYYmmdd format, got "
                              +arg.replace('--date=',''))
                        sys.exit(1)
                print(cmd_line_arg_name+" passed, using  "
                      +arg.replace(cmd_line_arg_name, ''))
                run_settings_dict[cmd_line_arg_opt_run_name] = (
                    arg.replace(cmd_line_arg_name, '')
                )
    else:
        print(cmd_line_arg_name+" not passed, using default "
              +cmd_line_arg_opt_default)
        run_settings_dict[cmd_line_arg_opt_run_name] = (
            cmd_line_arg_opt_default
        )

# Run settings: environment variables
print("Environment variable settings...")
env_var_dict = {
    'COMROOT': '/lfs/h1/ops/prod/com',
    'cfs_ver': 'v2.3',
    'SENDARCH': 'YES'
}
for env_var_name in list(env_var_dict.keys()):
    if env_var_name in os.environ.keys():
        env_var_value = os.environ[env_var_name]
        print("Using "+env_var_name+" value "+env_var_value+" from "
              +"environment")
        env_var_value = os.environ[env_var_name]
    else:
        env_var_value = env_var_dict[env_var_name]
        print(env_var_name+" not in environment using default value "
              +env_var_value)
    run_settings_dict[env_var_name] = env_var_value

print("\nUsing run settings...")
for run_name in list(run_settings_dict.keys()):
    print(run_name+' = '+str(run_settings_dict[run_name]))
print("")

# Get dates
PDYm_dict = ega_util.get_PDYm_dict(run_settings_dict['PDY'])

# Set up WCOSS2 dictionary
wcoss2_dict = ega_util.get_machine_dict()

# Make archive directory
model_archive_dir = os.path.join(
    run_settings_dict['ARCHIVE_DIR'], run_settings_dict['MODEL']
)
if run_settings_dict['SENDARCH'] == 'YES':
    if not os.path.exists(run_settings_dict['ARCHIVE_DIR']):
        print("Making directory "+run_settings_dict['ARCHIVE_DIR'])
        os.makedirs(run_settings_dict['ARCHIVE_DIR'])
    if not os.path.exists(model_archive_dir):
        print("Making directory "+model_archive_dir)
        os.makedirs(model_archive_dir)
        if run_settings_dict['MODEL'] == 'fnl':
            ega_util.set_rstprod_permissions(model_archive_dir)
base_model_run_dir = os.path.join(
    run_settings_dict['RUN_DIR'], run_settings_dict['MODEL']
)
if not os.path.exists(base_model_run_dir):
    print("Making directory "+base_model_run_dir)
    os.makedirs(base_model_run_dir)
    if run_settings_dict['MODEL'] == 'fnl':
        ega_util.set_rstprod_permissions(base_model_run_dir)
os.chdir(base_model_run_dir)
print("In run directory: "+base_model_run_dir)

# fnl - Operational GFS
if run_settings_dict['MODEL'] == 'fnl':
    model_prod_dir = os.path.join(
        run_settings_dict['COMROOT'], 'cfs', run_settings_dict['cfs_ver'],
        'fit2obs', 'GFS.fits'
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        model_run_dir = os.path.join(base_model_run_dir, PDYm)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
            ega_util.set_rstprod_permissions(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        for cycle in run_settings_dict['fnl_cycle_list']:
            archive_file = os.path.join(
                model_archive_dir, 'fits','f24.raob.'+PDYm+cycle
            )
            if not ega_util.check_file(archive_file):
                source_tar = os.path.join(
                    model_prod_dir, PDYm[0:4], 'GFS.fits.'+PDYm+cycle
                )
                if ega_util.check_file(source_tar):
                    ega_util.run_shell_command(
                        ['tar','-xvf', source_tar, '-C', model_run_dir]
                    )
                    if run_settings_dict['SENDARCH'] == 'YES':
                        for fit2obs_mid_dir in ['fits', 'horiz/fcs',
                                                'horiz/anl']:
                            for run_fit2obs_file \
                                    in glob.glob(os.path.join(model_run_dir,
                                                              fit2obs_mid_dir,
                                                              '*')):
                                if not os.path.exists(
                                    os.path.join(model_archive_dir,
                                                 fit2obs_mid_dir)
                                ):
                                    print("Making directory "
                                          +os.path.join(model_archive_dir,
                                                     fit2obs_mid_dir))
                                    os.makedirs(
                                        os.path.join(model_archive_dir,
                                                     fit2obs_mid_dir)
                                    )
                                    ega_util.set_rstprod_permissions(
                                        os.path.join(model_archive_dir,
                                                     fit2obs_mid_dir)
                                    )
                                ega_util.copy_file(
                                    run_fit2obs_file,
                                    os.path.join(model_archive_dir,
                                                 fit2obs_mid_dir,
                                                 run_fit2obs_file\
                                                 .rpartition('/')[2])
                                )
                            ega_util.set_rstprod_permissions(
                                os.path.join(
                                    model_archive_dir, fit2obs_mid_dir,
                                    '*'+PDYm+cycle+'*'
                                )
                            )
else:
    print(run_settings_dict['MODEL']+" not recongized")
    sys.exit(1)

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
