"""
About:
        This script creates monthly HPSS
        tar files for obs data.
Author(s):
	Mallory Row (mallory.row@noaa.gov)
History Log:
        December 2022 - Inital version
Command Line Agruments:
        --YYYYmm: optional, date (format YYYYmm) to run for,
                  default: today
        --archdir: path to archive directory,
                   default: /lfs/h2/emc/vpppg/noscrub/$USER/obs_archive
        --hpssdir: path to HPSS directory,
                   default: /NCEPDEV/emc-global/5year/$USER/obs_archive
        -obs: optional, obs name
              default: prepbufr_gdas
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import os
import sys
import datetime
from dateutil.relativedelta import relativedelta
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
           +"default: /lfs/h2/emc/vpppg/noscrub/$USER/obs_archive\n"
           +"   --hpssdir=HPSS_DIR      optional, "
           +"path to HPSS directory, "
            +"default: /NCEPDEV/emc-global/5year/$USER/obs_archive\n"
           +"   --obs=OBS           optional, "
           +"default: prepbufr_gdas\n")
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
                    +'/obs_archive')
    },
    '--hpssdir=': {
        'run_name': 'HPSS_DIR',
        'default': ('/NCEPDEV/emc-global/5year/'+os.environ['USER']
                    +'/obs_archive')
    },
    '--obs=': {
        'run_name': 'OBS',
        'default': 'prepbufr_gdas'
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
obs_hpss_dir = os.path.join(
    run_settings_dict['HPSS_DIR'], run_settings_dict['OBS']
)
ega_util.run_shell_command(
    ['hsi', '"mkdir -p '+obs_hpss_dir+'"']
)
if run_settings_dict['OBS'] in ['prepbufr_gdas', 'prepbufr_nam', 'prepbufr_rap']:
    ega_util.run_shell_command(
        ['hsi', '"chmod 750 '+obs_hpss_dir+'"']
    )
    ega_util.run_shell_command(
        ['hsi', '"chgrp rstprod '+obs_hpss_dir+'"']
    )
if run_settings_dict['OBS'] in ['prepbufr_gdas', 'prepbufr_nam', 'prepbufr_rap']:
    obs_archive_dir = os.path.join(
        run_settings_dict['ARCHIVE_DIR'],
        run_settings_dict['OBS'].partition('_')[0],
        run_settings_dict['OBS'].partition('_')[2]
    )
else:
    obs_archive_dir = os.path.join(
        run_settings_dict['ARCHIVE_DIR'], run_settings_dict['OBS']
    )
if not os.path.exists(obs_archive_dir):
    print(obs_archive_dir+" does not exist")
    sys.exit(1)
os.chdir(obs_archive_dir)
print("In directory: "+obs_archive_dir)
if run_settings_dict['OBS'] == 'get_d':
    YEARMON_start_dt = datetime.datetime.strptime(
        run_settings_dict['YEARMON']+'01', '%Y%m%d'
    )
    YEARMON_end_dt = (
        (YEARMON_start_dt + relativedelta(months=1))
        - datetime.timedelta(days=1)
    )
    YEARMON_file_list = []
    for get_d_file in glob.glob('*'+run_settings_dict['YEARMON'][0:4]+'*'):
        get_d_file_date_dt = datetime.datetime.strptime(
            get_d_file.replace('GETDL3_DAL_CONUS_', '')\
            .replace('_1.0.nc', ''), '%Y%j'
        )
        if get_d_file_date_dt <= YEARMON_end_dt \
                and get_d_file_date_dt >= YEARMON_start_dt:
            YEARMON_file_list.append(get_d_file)
    if len(YEARMON_file_list) != 0:
        tar_cmd = ['tar', '-cvf',
                   run_settings_dict['OBS']+'_'
                   +run_settings_dict['YEARMON']+'.tar']
        for tar_get_d_file in YEARMON_file_list:
            tar_cmd.append(tar_get_d_file)
        ega_util.run_shell_command(tar_cmd)
        ega_util.run_shell_command(
            ['hsi', 'put',
             run_settings_dict['OBS']+'_'+run_settings_dict['YEARMON']+'.tar',
             ':',
             os.path.join(obs_hpss_dir,
                          run_settings_dict['OBS']+'_'
                          +run_settings_dict['YEARMON']+'.tar')
            ]
        )
        os.remove(run_settings_dict['OBS']+'_'
                  +run_settings_dict['YEARMON']+'.tar')
    else:
        print("No files for "+run_settings_dict['YEARMON']+" in "
              +obs_archive_dir)
else:
    if run_settings_dict['OBS'] == 'OBSPRCP':
        YEARMON_file_list = glob.glob(
            '*-'+run_settings_dict['YEARMON']+'*'
        )
    elif run_settings_dict['OBS'] == 'osi_saf':
        YEARMON_file_list = glob.glob(
            'ice_conc_*_polstere-100_multi_'
            +run_settings_dict['YEARMON']+'*'
        )
    elif run_settings_dict['OBS'] == 'ghrsst_ospo':
        YEARMON_file_list = glob.glob(
            run_settings_dict['YEARMON']+'*'
        )
    elif run_settings_dict['OBS'] == 'ndbc_buoy':
        YEARMON_file_list = glob.glob(
            'buoy_'+run_settings_dict['YEARMON']+'*'
        )
    else:
        YEARMON_file_list = glob.glob(
            '*.'+run_settings_dict['YEARMON']+'*'
        )
    nYEARMON_files = len(YEARMON_file_list)
    if nYEARMON_files != 0:
        ega_util.run_shell_command(
            ['htar', '-cvf',
             os.path.join(obs_hpss_dir,
                          run_settings_dict['OBS']+'_'
                          +run_settings_dict['YEARMON']+'.tar'),
             '*'+run_settings_dict['YEARMON']+'*']
        )
        if run_settings_dict['OBS'] in ['prepbufr_gdas', 'prepbufr_nam',
                                        'prepbufr_rap']:
            ega_util.run_shell_command(
                ['hsi', '"chmod 750 '
                 +os.path.join(obs_hpss_dir, run_settings_dict['OBS']+'_'
                               +run_settings_dict['YEARMON']+'.tar')+'"']
            )
            ega_util.run_shell_command(
                ['hsi', '"chgrp rstprod '
                 +os.path.join(obs_hpss_dir, run_settings_dict['OBS']+'_'
                               +run_settings_dict['YEARMON']+'.tar')+'"']
            )
    else:
        print("No files for "+run_settings_dict['YEARMON']+" in "
              +obs_archive_dir)

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
