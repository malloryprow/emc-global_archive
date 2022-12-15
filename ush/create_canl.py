"""
About:
        This script the common analysis from
        GFS analysis, CMC f00, UKM f00, and
        ECM f00.
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
                  default: /lfs/h2/emc/stmp/$USER/run_create_canl
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
           +"   --date=PDY              optional, "
           +"date (format YYYYmmdd) to run for, "
           +"default: today\n"
           +"   --archdir=ARCHIVE_DIR   optional, "
           +"path to archive directory, "
           +"default: /lfs/h2/emc/vpppg/noscrub/$USER/model_archive\n"
           +"   --rundir=RUN_DIR        optional, "
           +"default: /lfs/h2/emc/stmp/$USER/run_create_canl\n"
           +"   --cycle=CYCLE           optional, "
           +"default: 00\n")
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
                    +'/run_create_canl')
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
if len(sys.argv[1:]) > 4:
    print("Too many agruments")
    usage()

# Set up dictionary for run settings
run_settings_dict = {}

# Run settings: hard coded
print("Hard coded settings...")
run_settings_dict['grid'] = '3'
run_settings_dict['npts'] = '65160'
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
    'COPYGB': ('/apps/ops/prod/libs/intel/19.1.3.304/grib_util/1.2.3/bin/'
               +'copygb'),
    'HOMEemc_global_archive': os.path.join(os.getcwd(), '..'),
    'SENDARCH', 'YES'
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

# Make archive directory
canl_archive_dir = os.path.join(run_settings_dict['ARCHIVE_DIR'], 'canl')
if run_settings_dict['SENDARCH'] == 'YES':
    if not os.path.exists(run_settings_dict['ARCHIVE_DIR']):
        print("Making directory "+canl_archive_dir)
        os.makedirs(canl_archive_dir)
        #ega_util.set_rstprod_permissions(canl_archive_dir)
CDATE = run_settings_dict['PDY']+run_settings_dict['CYCLE'].zfill(2)
canl_run_dir = os.path.join(
    run_settings_dict['RUN_DIR'], 'canl', CDATE
)
if not os.path.exists(canl_run_dir):
    print("Making directory "+canl_run_dir)
    os.makedirs(canl_run_dir)
os.chdir(canl_run_dir)
print("In run directory: "+canl_run_dir)

# Create common analysis
run_file = os.path.join(canl_run_dir, 'pgbanl.canl.'+CDATE)
archive_file = os.path.join(canl_archive_dir, 'pgbanl.canl.'+CDATE)
nn = 0
if not ega_util.check_file(archive_file):
    create_canl = True
    for model in ['gfs', 'ecm', 'ukm', 'cmc']:
        nn+=1
        if model == 'gfs':
            model_archive_file_name = 'pgbanl.gfs.'+CDATE
        else:
            model_archive_file_name = 'pgbf00.'+model+'.'+CDATE
        model_archive_file = os.path.join(
            run_settings_dict['ARCHIVE_DIR'], model, model_archive_file_name
        )
        if not ega_util.check_file(model_archive_file):
            create_canl = False
        else:
            model_tmp_file = os.path.join(canl_run_dir, 'input'+str(nn))
            if not ega_util.check_file(model_tmp_file):
                ega_util.regrid_copygb(
                    model_archive_file, model_tmp_file,
                    run_settings_dict['grid'], run_settings_dict['COPYGB']
                )
            if not ega_util.check_file(model_tmp_file):
                create_canl = False
            else:
                if model == 'ecm':
                    ega_util.set_rstprod_permissions(model_tmp_file)
    if create_canl:
        for var in ['HGT', 'TMP', 'UGRD', 'VGRD']:
            for level in ['1000', '925', '850', '700', '500', '250', '200']:
                kpds6='100'
                kpds7=level
                outtmp_varlevel = 'outtmp_'+var+level
                if var == 'HGT':
                    kpds5 = '7'
                elif var == 'TMP':
                    kpds5 = '11'
                elif var == 'UGRD':
                    kpds5 = '33'
                elif var == 'VGRD':
                    kpds5 = '34'
                ega_util.run_shell_command(
                    [os.path.join(
                         run_settings_dict['HOMEemc_global_archive'],
                         'exec', 'mean_anl'
                     ), str(nn), kpds5, kpds6, kpds7, run_settings_dict['npts']]
                )
                if ega_util.check_file('outtmp'):
                    ega_util.run_shell_command(
                        ['mv', 'outtmp', outtmp_varlevel]
                    )
        outtmp_file_list = glob.glob('outtmp*')
        if len(outtmp_file_list) != 0:
            ega_util.run_shell_command(
                ['cat', 'outtmp*', '>'+run_file]
            )
        if run_settings_dict['SENDARCH'] == 'YES':
            ega_util.copy_file(run_file, archive_file)
            ega_util.check_file(archive_file)

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
