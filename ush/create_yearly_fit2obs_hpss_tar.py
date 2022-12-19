"""
About:
        This script creates yearly HPSS
        tar files for fit2obs data.
Author(s):
	Mallory Row (mallory.row@noaa.gov)
History Log:
        December 2022 - Inital version
Command Line Agruments:
        --YYYY: optional, date (format YYYY) to run for,
                default: today
        --archdir: path to archive directory,
                   default: /lfs/h2/emc/vpppg/noscrub/$USER/fit2obs_archive
        --hpssdir: path to HPSS directory,
                   default: /NCEPDEV/emc-global/5year/$USER/fit2obs_archive
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
           +"   --year=YYYY        optional, "
           +"date (format YYYY) to run for, "
           +"default: today\n"
           +"   --archdir=ARCHIVE_DIR   optional, "
           +"path to archive directory, "
           +"default: /lfs/h2/emc/vpppg/noscrub/$USER/fit2obs_archive\n"
           +"   --hpssdir=HPSS_DIR      optional, "
           +"path to HPSS directory, "
            +"default: /NCEPDEV/emc-global/5year/$USER/fit2obs_archive\n"
           +"   --model=MODEL           optional, "
           +"default: fnl\n")
    sys.exit(1)

# Command line agrument information
cmd_line_args_dict = {
    '--year=': {
        'run_name': 'YEAR',
        'default': datetime.datetime.today().strftime('%Y')
    },
    '--archdir=': {
        'run_name': 'ARCHIVE_DIR',
        'default': ('/lfs/h2/emc/vpppg/noscrub/'+os.environ['USER']
                    +'/fit2obs_archive')
    },
    '--hpssdir=': {
        'run_name': 'HPSS_DIR',
        'default': ('/NCEPDEV/emc-global/5year/'+os.environ['USER']
                    +'/fit2obs_archive')
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
                if cmd_line_arg_name == '--year=':
                    if len(arg.replace('--year=','')) != 4:
                        print("--year must be in YYYY format, got "
                              +arg.replace('--year=',''))
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
env_var_dict = {}
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

# Create HPSS tar
model_hpss_dir = os.path.join(
    run_settings_dict['HPSS_DIR'], run_settings_dict['MODEL']
)
ega_util.run_shell_command(
    ['hsi', '"mkdir -p '+model_hpss_dir+'"']
)
if run_settings_dict['MODEL'] in ['fnl']:
    ega_util.run_shell_command(
        ['hsi', '"chmod 750 '+model_hpss_dir+'"']
    )
    ega_util.run_shell_command(
        ['hsi', '"chgrp rstprod '+model_hpss_dir+'"']
    )
model_archive_dir = os.path.join(
    run_settings_dict['ARCHIVE_DIR'], run_settings_dict['MODEL']
)
model_fits_dir = os.path.join(
    model_archive_dir, 'fits'
)
model_horiz_anl_dir = os.path.join(
    model_archive_dir, 'horiz', 'anl'
)
model_horiz_fcs_dir = os.path.join(
    model_archive_dir, 'horiz', 'fcs'
)
if not os.path.exists(model_archive_dir):
    print(model_archive_dir+" does not exist")
    sys.exit(1)
os.chdir(model_archive_dir)
print("In directory: "+model_archive_dir)
YEAR_fits_file_list = glob.glob(
    os.path.join(model_fits_dir,
                 '*.'+run_settings_dict['YEAR']+'*')
)
nYEAR_fits_files = len(YEAR_fits_file_list)
YEAR_horiz_anl_file_list = glob.glob(
    os.path.join(model_horiz_anl_dir,
                 '*.'+run_settings_dict['YEAR']+'*')
)
nYEAR_horiz_anl_files = len(YEAR_horiz_anl_file_list)
YEAR_horiz_fcs_file_list = glob.glob(
    os.path.join(model_horiz_fcs_dir,
                 '*.'+run_settings_dict['YEAR']+'*')
)
nYEAR_horiz_fcs_files = len(YEAR_horiz_fcs_file_list)
nYEAR_files = nYEAR_fits_files+ nYEAR_horiz_anl_files+ nYEAR_horiz_fcs_files
if nYEAR_files != 0:
    ega_util.run_shell_command(
        ['tar', '-cvf',
         run_settings_dict['MODEL']+'_'+run_settings_dict['YEAR']+'.tar',
         os.path.join('fits',
                      '*.'+run_settings_dict['YEAR']+'*'),
         os.path.join('horiz', 'anl',
                      '*.'+run_settings_dict['YEAR']+'*'),
         os.path.join('horiz', 'fcs',
                      '*.'+run_settings_dict['YEAR']+'*')]
    )
    ega_util.run_shell_command(
        ['hsi', 'put',
         run_settings_dict['MODEL']+'_'+run_settings_dict['YEAR']+'.tar',
         ':',
         os.path.join(model_hpss_dir,
                      run_settings_dict['MODEL']+'_'
                      +run_settings_dict['YEAR']+'.tar')
         ]
    )
    if run_settings_dict['MODEL'] in ['fnl']:
        ega_util.run_shell_command(
            ['hsi', '"chmod 750 '
             +os.path.join(model_hpss_dir, run_settings_dict['MODEL']+'_'
                           +run_settings_dict['YEAR']+'.tar')+'"']
        )
        ega_util.run_shell_command(
            ['hsi', '"chgrp rstprod '
             +os.path.join(model_hpss_dir, run_settings_dict['MODEL']+'_'
                           +run_settings_dict['YEAR']+'.tar')+'"']
        )
    os.remove(run_settings_dict['MODEL']+'_'+run_settings_dict['YEAR']+'.tar')
else:
    print("No files for "+run_settings_dict['YEAR']+" in "
          +model_archive_dir)

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
