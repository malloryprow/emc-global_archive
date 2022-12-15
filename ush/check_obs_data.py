"""
About:
        This script checks the archived observation
        data for missing files.
Author(s):
	Mallory Row (mallory.row@noaa.gov)
History Log:
        November 2021 - Inital version
Command Line Agruments: 
        --date: optional, date (format YYYYmmdd) to run for,
                default: today
        --archdir: path to archive directory,
                   default: /lfs/h2/emc/vpppg/noscrub/$USER/obs_archive
        --rundir: optional, path to run directory,
                  default: /lfs/h2/emc/stmp/$USER/run_check_obs_data
        --obs: optional, observation name,
               default: prepbufr_gdas
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import os
import sys
import datetime
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
           +"default: /lfs/h2/emc/vpppg/noscrub/$USER/obs_archive\n"
           +"   --rundir=RUN_DIR        optional, "
           +"default: /lfs/h2/emc/stmp/$USER/run_check_obs_data\n"
           +"   --obs=obs               optional, "
           +"default: prepbufr_gdas\n")
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
                    +'/obs_archive')
    },
    '--rundir=': {
        'run_name': 'RUN_DIR',
        'default': ('/lfs/h2/emc/stmp/'+os.environ['USER']
                    +'/run_check_obs_data')
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

# Check obs data
if run_settings_dict['OBS'] in ['prepbufr_gdas', 'prepbufr_nam']:
    obs_archive_dir = os.path.join(
        run_settings_dict['ARCHIVE_DIR'],
        run_settings_dict['OBS'].split('_')[0],
        run_settings_dict['OBS'].split('_')[1]
    )
else:
    obs_archive_dir = os.path.join(
        run_settings_dict['ARCHIVE_DIR'], run_settings_dict['OBS']
    )
run_dir = os.path.join(run_settings_dict['RUN_DIR'])
if not os.path.exists(run_dir):
    print("Making directory "+run_dir)
    os.makedirs(run_dir)
os.chdir(run_dir)
print("In run directory: "+run_dir)
missing_file_list = []
check_file_list = []
found_file_list = []
if os.path.exists(obs_archive_dir):
    PDY_dt = datetime.datetime.strptime(run_settings_dict['PDY'], '%Y%m%d')
    if run_settings_dict['OBS'] == 'prepbufr_gdas':
        check_file_list.append('prepbufr.gdas.'+run_settings_dict['PDY']+'00')
        check_file_list.append('prepbufr.gdas.'+run_settings_dict['PDY']+'06')
        check_file_list.append('prepbufr.gdas.'+run_settings_dict['PDY']+'12')
        check_file_list.append('prepbufr.gdas.'+run_settings_dict['PDY']+'18')
    elif run_settings_dict['OBS'] == 'prepbufr_nam':
        check_file_list.append(
            'nam.'+run_settings_dict['PDY']+'/nam.t00z.prepbufr.tm00'
        )
        check_file_list.append(
            'nam.'+run_settings_dict['PDY']+'/nam.t00z.prepbufr.tm03'
        )
        check_file_list.append(
            'nam.'+run_settings_dict['PDY']+'/nam.t06z.prepbufr.tm00'
        )
        check_file_list.append(
            'nam.'+run_settings_dict['PDY']+'/nam.t06z.prepbufr.tm03'
        )
        check_file_list.append(
            'nam.'+run_settings_dict['PDY']+'/nam.t12z.prepbufr.tm00'
        )
        check_file_list.append(
            'nam.'+run_settings_dict['PDY']+'/nam.t12z.prepbufr.tm03'
        )
        check_file_list.append(
            'nam.'+run_settings_dict['PDY']+'/nam.t18z.prepbufr.tm00'
        )
        check_file_list.append(
            'nam.'+run_settings_dict['PDY']+'/nam.t18z.prepbufr.tm03'
        )
    elif run_settings_dict['OBS'] == 'prepbufr_rap':
        check_file_list.append(
            'rap.'+run_settings_dict['PDY']+'/rap.t00z.prepbufr.tm00'
        )
        check_file_list.append(
            'rap.'+run_settings_dict['PDY']+'/rap.t03z.prepbufr.tm00'
        )
        check_file_list.append(
            'rap.'+run_settings_dict['PDY']+'/rap.t06z.prepbufr.tm00'
        )
        check_file_list.append(
            'rap.'+run_settings_dict['PDY']+'/rap.t09z.prepbufr.tm00'
        )
        check_file_list.append(
            'rap.'+run_settings_dict['PDY']+'/rap.t12z.prepbufr.tm00'
        )
        check_file_list.append(
            'rap.'+run_settings_dict['PDY']+'/rap.t15z.prepbufr.tm00'
        )
        check_file_list.append(
            'rap.'+run_settings_dict['PDY']+'/rap.t18z.prepbufr.tm00'
        )
        check_file_list.append(
            'rap.'+run_settings_dict['PDY']+'/rap.t21z.prepbufr.tm00'
        )
    elif run_settings_dict['OBS'] == 'ccpa_accum24hr':
        check_file_list.append('ccpa.'+run_settings_dict['PDY']+'12.24h')
    elif run_settings_dict['OBS'] == 'ccpa_accum6hr':
        check_file_list.append('ccpa.hrap.'+run_settings_dict['PDY']+'00.6h')
        check_file_list.append('ccpa.hrap.'+run_settings_dict['PDY']+'06.6h')
        check_file_list.append('ccpa.hrap.'+run_settings_dict['PDY']+'12.6h')
        check_file_list.append('ccpa.hrap.'+run_settings_dict['PDY']+'18.6h')
    elif run_settings_dict['OBS'] == 'nohrsc_accum24hr':
        check_file_list.append('nohrsc.'+run_settings_dict['PDY']+'12.24h')
    elif run_settings_dict['OBS'] == 'get_d':
        check_file_list.append('GETDL3_DAL_CONUS_'+PDY_dt.strftime('%Y%j')
                               +'_1.0.nc')
    elif run_settings_dict['OBS'] == 'osi_saf':
        PDYm1_dt = PDY - datetime.timedelta(days=1)
        PDYm7_dt = PDY - datetime.timedelta(days=7)
        check_file_list.append('osi_saf.multi.'
                               +PDYm1_dt.strftime('%Y%m%d')+'00to'
                               +run_settings_dict['PDY']+'00_G004.nc')
        check_file_list.append('osi_saf.multi.'
                               +PDYm7_dt.strftime('%Y%m%d')+'00to'
                               +run_settings_dict['PDY']+'00_G004.nc')
    elif run_settings_dict['OBS'] == 'ghrsst_median':
        PDYm1_dt = PDY - datetime.timedelta(days=1)
        check_file_list.append('UKMO-L4_GHRSST-SSTfnd-GMPE-GLOB_valid'
                               +PDYm1_dt.strftime('%Y%m%d')+'00to'
                               +run_settings_dict['PDY']+'00.nc')
    elif run_settings_dict['OBS'] == 'OBSPRCP':
        check_file_list.append('usa-dlyprcp-'+run_settings_dict['PDY']) 
    for check_file in check_file_list:
        archive_file = os.path.join(obs_archive_dir, check_file)
        if not ega_util.check_file(archive_file):
            missing_file_list.append(archive_file)
        else:
            found_file_list.append(archive_file)
else:
    print(obs_archive_dir+" does not exist")
ncheck_files = len(check_file_list)
nfound_files = len(found_file_list)
nmissing_files = len(missing_file_list)
if ncheck_files != 0:
    print("Found "+str(nfound_files)+", missing "+str(nmissing_files)+", expected "
           +str(ncheck_files)+" for "+run_settings_dict['PDY']+" in "
           +obs_archive_dir)
if nmissing_files != 0:
    missing_files_txt = os.path.join(
        run_dir, 'missing_files_obs_'+run_settings_dict['OBS']+'_'
        +run_settings_dict['PDY']+'.txt'
    )
    print("\nWriting missing files to "+missing_files_txt)
    if os.path.exists(missing_files_txt):
        os.remove(missing_files_txt)
    with open(missing_files_txt, 'w') as f:
        for item in missing_file_list:
            f.write("%s\n" % item)

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
