"""
About:
        This script gets model data.
Author(s):
        Mallory Row (mallory.row@noaa.gov)
History Log:
        November 2021 - Inital version
Command Line Agruments:
        --removedate: optional, date (format YYYYmmdd) to delete for,
                      default: today
        --archdir: path to archive directory,
                   default: /lfs/h2/emc/vpppg/noscrub/$USER/model_archive/gfs
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
           +"    --removedate=PDY optional, removal date (format YYYYmmdd),"
           +"default: today"
           +"   --archdir=ARCHIVE_DIR   optional, "
           +"path to archive directory, "
           +"default: /lfs/h2/emc/vpppg/noscrub/$USER/model_archive/gfs\n")
    sys.exit(1)

# Command line agrument information
cmd_line_args_dict = {
    '--removedate=': {
        'run_name': 'PDY',
        'default': datetime.datetime.today().strftime('%Y%m%d')
    },
    '--archdir=': {
        'run_name': 'ARCHIVE_DIR',
        'default': ('/lfs/h2/emc/vpppg/noscrub/'+os.environ['USER']
                    +'/model_archive/gfs')
    }
}

# Print usage statement
help_args = ('-h', '--help')
for help_arg in help_args:
    if help_arg in sys.argv:
        usage()
        sys.exit(0)

# Check number of command line arguments
if len(sys.argv[1:]) > 2:
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
                if cmd_line_arg_name == '--removedate=':
                    if len(arg.replace('--removedate=','')) != 8:
                        print("--removedate must be in YYYYmmdd format, got "
                              +arg.replace('--removedate=',''))
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

# Set up WCOSS2 dictionary
wcoss2_dict = ega_util.get_machine_dict()

# Remove files
remove_archive_dir = os.path.join(run_settings_dict['ARCHIVE_DIR'])
if not os.path.exists(remove_archive_dir):
    print(remove_archive_dir+" does not exist")
    sys.exit(1)
os.chdir(remove_archive_dir)
print("In directory: "+remove_archive_dir)
if remove_archive_dir.rpartition('/')[2] == 'get_d':
    PDY_dt = datetime.datetime.strptime(run_settings_dict['PDY'], '%Y%m%d')
    remove_file_list = glob.glob(
        os.path.join(remove_archive_dir,'*'+PDY_dt.strftime('%Y%j')+'*')
    )
elif remove_archive_dir.rpartition('/')[2] == 'osi_saf':
    remove_file_list = glob.glob(
        os.path.join(remove_archive_dir,
                     'ice_conc_*_polstere-100_multi_'
                     '*'+run_settings_dict['PDY']+'1200.nc')
    )
elif remove_archive_dir.rpartition('/')[2] == 'ghrsst_ospo':
    remove_file_list = glob.glob(
        os.path.join(remove_archive_dir,
                     run_settings_dict['PDY']+'_OSPO_L4_GHRSST')
    )
elif 'evs_data' in remove_archive_dir:
    remove_file_list = glob.glob(
        os.path.join(remove_archive_dir+'.'+run_settings_dict['PDY'])
    )
else:
    remove_file_list = glob.glob(
        os.path.join(remove_archive_dir,'*'+run_settings_dict['PDY']+'*')
    )
nremove_files = len(remove_file_list)
if nremove_files != 0:
    print("Removing "+str(nremove_files)+" files "
          +' '.join(remove_file_list))
    ega_util.run_shell_command(
        ['rm', '-rf', ' '.join(remove_file_list)]
    )
    ega_util.run_shell_command(
        ['ssh', os.environ['USER']+'@'+wcoss2_dict['OTHER'],
         '"rm -rf '+' '.join(remove_file_list)+'"']
    )
else:
    print("No files matching date "+run_settings_dict['PDY']+" in "
          +remove_archive_dir)

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
