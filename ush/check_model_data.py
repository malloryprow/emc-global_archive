"""
About:
        This script checks the archived model data for
        missing files.
Author(s):
	Mallory Row (mallory.row@noaa.gov)
History Log:
        November 2021 - Inital version
Command Line Agruments:
        --date: optional, date (format YYYYmmdd) to run for,
                default: today
        --archdir: path to archive directory,
                   default: /lfs/h2/emc/vpppg/noscrub/$USER/model_archive
        --rundir: optional, path to run directory,
                  default: /lfs/h2/emc/stmp/$USER/run_check_model_data
        --model: optional, model name
                 default: gfs
        --cycle: optional, cycle hour
                 default: 00
        --fhrmin: optional, minimum forecast hour
                  default: 0
        --fhrmax: optional, maximum forecast hour
                  default: 120
        --fhrinc: optional, forecast hour increment
                  default: 24
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
           +"default: /lfs/h2/emc/vpppg/noscrub/$USER/model_archive\n"
           +"   --rundir=RUN_DIR        optional, "
           +"default: /lfs/h2/emc/stmp/$USER/run_check_model_data\n"
           +"   --model=MODEL           optional, "
           +"default: gfs\n"
           +"   --cycle=CYCLE           optional, "
           +"default: 00\n"
           +"   --fhrmin=FHR_MIN        optional, "
           +"default: 0\n"
           +"   --fhrmax=FHR_MAX        optional, "
           +"default: 120\n"
           +"   --fhrinc=FHR_INC        optional, "
           +"default: 24\n")
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
                    +'/model_archive')
    },
    '--rundir=': {
        'run_name': 'RUN_DIR',
        'default': ('/lfs/h2/emc/stmp/'+os.environ['USER']
                    +'/run_check_model_data')
    },
    '--model=': {
        'run_name': 'MODEL',
        'default': 'gfs'
    },
    '--cycle=': {
        'run_name': 'CYCLE',
        'default': '00'
    },
    '--fhrmin=': {
        'run_name': 'FHR_MIN',
        'default': '0'
    },
    '--fhrmax=': {
        'run_name': 'FHR_MAX',
        'default': '120'
    },
    '--fhrinc=': {
        'run_name': 'FHR_INC',
        'default': '24'
    }
}

# Print usage statement
help_args = ('-h', '--help')
for help_arg in help_args:
    if help_arg in sys.argv:
        usage()
        sys.exit(0)

# Check number of command line arguments
if len(sys.argv[1:]) > 8:
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

# Check model data
run_dir = os.path.join(
    run_settings_dict['RUN_DIR']
)
if not os.path.exists(run_dir):
    print("Making directory "+run_dir)
    os.makedirs(run_dir)
os.chdir(run_dir)
print("In run directory: "+run_dir)
missing_file_list = []
check_file_list = []
found_file_list = []
CDATE = run_settings_dict['PDY']+run_settings_dict['CYCLE'].zfill(2)
model_archive_dir = os.path.join(
    run_settings_dict['ARCHIVE_DIR'], run_settings_dict['MODEL']
)
if os.path.exists(model_archive_dir):
    if run_settings_dict['MODEL'] not in ['ecmg4']:
        check_file_list.append('pgbanl.'+run_settings_dict['MODEL']+'.'+CDATE)
    if run_settings_dict['MODEL'] == 'ecm' \
            and run_settings_dict['CYCLE'].zfill(2) in ['06', '18']:
        run_settings_dict['FHR_MAX'] = '00'
    fhr = int(run_settings_dict['FHR_MIN'])
    while fhr <= int(run_settings_dict['FHR_MAX']):
        fhr2 = str(fhr).zfill(2)
        if run_settings_dict['MODEL'] == 'ecmg4':
            check_file_list.append('flxf'+fhr2+'.ecm.'+CDATE)
        else:
            check_file_list.append(
                'pgbf'+fhr2+'.'+run_settings_dict['MODEL']+'.'+CDATE
            )
        if run_settings_dict['MODEL'] == 'gfs' and fhr <= 240:
            check_file_list.append('flxf'+fhr2+'.gfs.'+CDATE)
        if run_settings_dict['MODEL'] == 'gfs' and fhr >=240:
            fhr+=12
        else:
            fhr+=int(run_settings_dict['FHR_INC'])
    if run_settings_dict['MODEL'] == 'gfs':
        check_file_list.append('pgbanl.gdas.'+CDATE)
        check_file_list.append('pgbf00.gdas.'+CDATE)
        check_file_list.append('pgbf06.gdas.'+CDATE)
        check_file_list.append('atcfunix.gfs.'+CDATE)
    for check_file in check_file_list:
        archive_file = os.path.join(model_archive_dir, check_file)
        if not ega_util.check_file(archive_file):
            missing_file_list.append(archive_file)
        else:
            found_file_list.append(archive_file)
else:
    print(model_archive_dir+" does not exist")
ncheck_files = len(check_file_list)
nfound_files = len(found_file_list)
nmissing_files = len(missing_file_list)
if ncheck_files != 0:
    print("Found "+str(nfound_files)+", missing "+str(nmissing_files)+", expected "
           +str(ncheck_files)+" for "+CDATE+" in "+model_archive_dir)
if nmissing_files != 0:
    missing_files_txt = os.path.join(
        run_dir, 'missing_files_model_'
        +run_settings_dict['MODEL']+'_'+CDATE+'.txt'
    )
    print("\nWriting missing files to "+missing_files_txt)
    if os.path.exists(missing_files_txt):
        os.remove(missing_files_txt)
    with open(missing_files_txt, 'w') as f:
        for item in missing_file_list:
            f.write("%s\n" % item)

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
