"""
About:
        This script creates monthly HPSS
        tar files for model data.
Author(s):
	Mallory Row (mallory.row@noaa.gov)
History Log:
        November 2021 - Inital version
Command Line Agruments:
        --YYYYmm: optional, date (format YYYYmm) to run for,
                  default: today
        --archdir: path to archive directory,
                   default: /lfs/h2/emc/vpppg/noscrub/$USER/model_archive
        --hpssdir: path to HPSS directory,
                   default: /NCEPDEV/emc-global/5year/$USER/model_archive
        --model: optional, model name
                 default: gfs
        --cycle: optional, cycle hour
                 default: 00
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
           +"   --yearmon=YYYYmm        optional, "
           +"date (format YYYYmm) to run for, "
           +"default: today\n"
           +"   --archdir=ARCHIVE_DIR   optional, "
           +"path to archive directory, "
           +"default: /lfs/h2/emc/vpppg/noscrub/$USER/model_archive\n"
           +"   --hpssdir=HPSS_DIR      optional, "
           +"path to HPSS directory, "
            +"default: /NCEPDEV/emc-global/5year/$USER/model_archive\n"
           +"   --model=MODEL           optional, "
           +"default: gfs\n"
           +"   --cycle=CYCLE           optional, "
           +"default: 00\n")
    sys.exit(1)

# Command line agrument information
cmd_line_args_dict = {
    '--yearmon=': {
        'run_name': 'YEARMON',
        'default': datetime.datetime.today().strftime('%Y%m')
    },
    '--archdir=': {
        'run_name': 'ARCHIVE_DIR',
        'default': ('/lfs/h2/emc/vpppg/noscrub/'+os.environ['USER']
                    +'/model_archive')
    },
    '--hpssdir=': {
        'run_name': 'HPSS_DIR',
        'default': ('/NCEPDEV/emc-global/5year/'+os.environ['USER']
                    +'/model_archive')
    },
    '--model=': {
        'run_name': 'MODEL',
        'default': 'gfs'
    },
    '--cycle=': {
        'run_name': 'CYCLE',
        'default': '00'
    }
}

# Print usage statement
help_args = ('-h', '--help')
for help_arg in help_args:
    if help_arg in sys.argv:
        usage()
        sys.exit(0)

# Check number of command line arguments
if len(sys.argv[1:]) > 5:
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
                if cmd_line_arg_name == '--yearmon=':
                    if len(arg.replace('--yearmon=','')) != 6:
                        print("--yearmon must be in YYYYmm format, got "
                              +arg.replace('--yearmon=',''))
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
if run_settings_dict['MODEL'] in ['ecm', 'ecmg4']:
    ega_util.run_shell_command(
        ['hsi', '"chmod 750 '+model_hpss_dir+'"']
    )
    ega_util.run_shell_command(
        ['hsi', '"chgrp rstprod '+model_hpss_dir+'"']
    )
model_archive_dir = os.path.join(
    run_settings_dict['ARCHIVE_DIR'], run_settings_dict['MODEL']
)
if not os.path.exists(model_archive_dir):
    print(model_archive_dir+" does not exist")
    sys.exit(1)
os.chdir(model_archive_dir)
print("In directory: "+model_archive_dir)
YEARMON_file_list = glob.glob(
    '*.'+run_settings_dict['YEARMON']+'*'+run_settings_dict['CYCLE']
)
nYEARMON_files = len(YEARMON_file_list)
if nYEARMON_files != 0:
    ega_util.run_shell_command(
        ['htar', '-cvf',
         os.path.join(model_hpss_dir,
                      run_settings_dict['MODEL']+run_settings_dict['CYCLE']+'_'
                      +run_settings_dict['YEARMON']+'.tar'),
         '*'+run_settings_dict['YEARMON']+'*'+run_settings_dict['CYCLE']]
    )
    if run_settings_dict['MODEL'] in ['ecm', 'ecmg4']:
        ega_util.run_shell_command(
            ['hsi', '"chmod 750 '
             +os.path.join(model_hpss_dir, run_settings_dict['MODEL']
                           +run_settings_dict['CYCLE']+'_'
                           +run_settings_dict['YEARMON']+'.tar')+'"']
        )
        ega_util.run_shell_command(
            ['hsi', '"chgrp rstprod '
             +os.path.join(model_hpss_dir, run_settings_dict['MODEL']
                           +run_settings_dict['CYCLE']+'_'
                           +run_settings_dict['YEARMON']+'.tar')+'"']
        )
else:
    print("No files for "+run_settings_dict['YEARMON']+" in "
          +model_archive_dir)

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
