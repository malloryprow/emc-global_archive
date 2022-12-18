"""
About:
        This script gets production GFS
        model data from HPSS
Author(s):
	Mallory Row (mallory.row@noaa.gov)
History Log:
        November 2021 - Inital version
Command Line Agruments:
        --date: optional, date (format YYYYmmdd) to run for,
                default: today
        --archdir: path to archive directory,
                   default: /lfs/h2/emc/vpppg/noscrub/$USER/model_archive/gfs
        --rundir: optional, path to run directory,
                  default: /lfs/h2/emc/stmp/$USER/run_get_prod_gfs_hpss
        --filetype: optional, file type
                    default: pgb
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
           +"default: /lfs/h2/emc/vpppg/noscrub/$USER/model_archive/gfs\n"
           +"   --rundir=RUN_DIR        optional, "
           +"default: /lfs/h2/emc/stmp/$USER/run_get_prod_gfs_hpss\n"
           +"   --filetype=FILETYPE     optional, "
           +"default: pgb\n"
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
                    +'/model_archive/gfs')
    },
    '--rundir=': {
        'run_name': 'RUN_DIR',
        'default': ('/lfs/h2/emc/stmp/'+os.environ['USER']
                    +'/run_get_prod_gfs_hpss')
    },
    '--filetype=': {
        'run_name': 'FILE_TYPE',
        'default': 'pgb'
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
run_settings_dict['HPSS_PROD_DIR'] = '/NCEPPROD/hpssprod/runhistory'
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
    'CNVGRIB': ('/apps/ops/prod/libs/intel/19.1.3.304/grib_util/1.2.3/bin/'
                +'cnvgrib'),
    'WGRIB2': '/apps/ops/prod/libs/intel/19.1.3.304/wgrib2/2.0.8/bin/wgrib2',
    'gfs_ver': 'v16.3',
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

#print("Using run settings...")
#for run_name in list(run_settings_dict.keys()):
#    print(run_name+' = '+str(run_settings_dict[run_name]))
print("")

# Set up WCOSS2 dictionary
wcoss2_dict = ega_util.get_machine_dict()

# Make output directory
if not os.path.exists(run_settings_dict['ARCHIVE_DIR']):
    os.makedirs(run_settings_dict['ARCHIVE_DIR'])

# Get GFS prod HPSS tar
gfs_archive_dir = os.path.join(run_settings_dict['ARCHIVE_DIR'])
if not os.path.exists(gfs_archive_dir):
    os.makedirs(gfs_archive_dir)
gfs_run_dir = os.path.join(run_settings_dict['RUN_DIR'])
if not os.path.exists(gfs_run_dir):
    os.makedirs(gfs_run_dir)
os.chdir(gfs_run_dir)
print("In run directory: "+gfs_run_dir)
CDATE = run_settings_dict['PDY']+run_settings_dict['CYCLE'].zfill(2)
CDATE_dt = datetime.datetime.strptime(CDATE, '%Y%m%d%H')
YYYYmmddHH = CDATE_dt.strftime('%Y%m%d%H')
YYYYmmdd = CDATE_dt.strftime('%Y%m%d')
YYYYmm = CDATE_dt.strftime('%Y%m')
YYYY = CDATE_dt.strftime('%Y')
mm = CDATE_dt.strftime('%m')
dd = CDATE_dt.strftime('%d')
HH = CDATE_dt.strftime('%H')
if CDATE_dt >= datetime.datetime.strptime('20210321', '%Y%m%d'):
    hpss_tar_filename_prefix = 'com_gfs_prod_gfs.'+YYYYmmdd+'_'+HH+'.gfs'
    hpss_file_prefix = os.path.join(
        'gfs.'+YYYYmmdd, HH, 'atmos', 'gfs.t'+HH+'z.'
    )
elif CDATE_dt \
        >= datetime.datetime.strptime('20200226', '%Y%m%d') \
        and CDATE_dt \
        < datetime.datetime.strptime('20210321', '%Y%m%d'):
    hpss_tar_filename_prefix = 'com_gfs_prod_gfs.'+YYYYmmdd+'_'+HH+'.gfs'
    hpss_file_prefix = os.path.join('gfs.'+YYYYmmdd, HH, 'gfs.t'+HH+'z.')
elif CDATE_dt \
        >= datetime.datetime.strptime('20190612', '%Y%m%d') \
        and CDATE_dt \
        < datetime.datetime.strptime('20200226', '%Y%m%d'):
    hpss_tar_filename_prefix = (
        'gpfs_dell1_nco_ops_com_gfs_prod_gfs.'+YYYYmmdd+'_'+HH+'.gfs'
    )
    hpss_file_prefix = os.path.join('gfs.'+YYYYmmdd, HH, 'gfs.t'+HH+'z.')
elif CDATE_dt \
        >= datetime.datetime.strptime('20170720','%Y%m%d') \
        and CDATE_dt \
        < datetime.datetime.strptime('20190612','%Y%m%d'):
    hpss_tar_filename_prefix = (
        'gpfs_hps_nco_ops_com_gfs_prod_gfs.'+YYYYmmddHH
    )
    hpss_file_prefix = 'gfs.t'+HH+'z.'
elif CDATE_dt \
        >= datetime.datetime.strptime('20160510', '%Y%m%d') \
        and CDATE_dt \
        < datetime.datetime.strptime('20170720', '%Y%m%d'):
    hpss_tar_filename_prefix = 'com2_gfs_prod_gfs.'+YYYYmmddHH
    hpss_file_prefix = 'gfs.t'+HH+'z.'
elif CDATE_dt \
        < datetime.datetime.strptime('20160510', '%Y%m%d'):
    print("Farthest date back supported is 20160510, requested "
          +run_settings_dict['PDY'])
    sys.exit(1)
fhr = int(run_settings_dict['FHR_MIN'])
while fhr <= int(run_settings_dict['FHR_MAX']):
    fhr2 = str(fhr).zfill(2)
    fhr3 = str(fhr).zfill(3)
    # pgb - 1 degree grib2 files
    if run_settings_dict['FILE_TYPE'] == 'pgb':
        archive_file = os.path.join(gfs_archive_dir, 'pgbf'+fhr2+'.gfs.'+CDATE)
        hpss_file = hpss_file_prefix+'pgrb2.1p00.f'+fhr3
        if CDATE_dt \
                >= datetime.datetime.strptime('20190612', '%Y%m%d'):
            hpss_tar_filename = hpss_tar_filename_prefix+'_pgrb2.tar'
        else:
            hpss_tar_filename = hpss_tar_filename_prefix+'.pgrb2_1p00.tar'
        tmp_file = os.path.join(
            gfs_run_dir, 'tmp.pgrb2.1p00.gfs.'+fhr3+'.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if not ega_util.check_file(tmp_file):
                ega_util.run_shell_command(
                    ['htar', '-xvf',
                     os.path.join(
                         run_settings_dict['HPSS_PROD_DIR'],
                         'rh'+YYYY, YYYYmm, YYYYmmdd, hpss_tar_filename
                     ), './'+hpss_file]
                )
                ega_util.run_shell_command(['mv', hpss_file, tmp_file])
            if ega_util.check_file(tmp_file):
                ega_util.convert_grib2_to_grib1(
                    tmp_file, archive_file,
                    run_settings_dict['CNVGRIB']
                )
            ega_util.check_file(archive_file)
    # flx - native grid grib2 files
    elif run_settings_dict['FILE_TYPE'] == 'flx':
        archive_file = os.path.join(gfs_archive_dir, 'flxf'+fhr2+'.gfs.'+CDATE)
        if CDATE_dt \
                >= datetime.datetime.strptime('20170720','%Y%m%d') \
                and CDATE_dt \
                < datetime.datetime.strptime('20190612','%Y%m%d'):
            hpss_file = (
                'gpfs/hps/nco/ops/com/gfs/prod/gfs.'+YYYYmmdd+'/'
                +hpss_file_prefix+'sfluxgrbf'+fhr2+'.grib2'
            )
        elif CDATE_dt \
                >= datetime.datetime.strptime('20160510', '%Y%m%d') \
                and CDATE_dt \
                < datetime.datetime.strptime('20170720', '%Y%m%d'):
            hpss_file = hpss_file_prefix+'sfluxgrbf'+fhr2+'.grib2'
        else:
            hpss_file = hpss_file_prefix+'sfluxgrbf'+fhr3+'.grib2'
        if CDATE_dt \
                >= datetime.datetime.strptime('20190612', '%Y%m%d'):
            hpss_tar_filename = hpss_tar_filename_prefix+'_flux.tar'
        else:
            hpss_tar_filename = hpss_tar_filename_prefix+'.sfluxgrb.tar'
        tmp1_file = os.path.join(
            gfs_run_dir, 'tmp.sfluxgrb.gfs.'+fhr3+'.'+CDATE
        )
        tmp2_file = os.path.join(
            gfs_run_dir, 'tmp.sfluxgrb.gfs.PRATE.2mTMP.'
            +fhr3+'.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if not ega_util.check_file(tmp1_file):
                if CDATE_dt \
                        >= datetime.datetime.strptime('20170720','%Y%m%d') \
                        and CDATE_dt \
                        < datetime.datetime.strptime('20190612','%Y%m%d'):
                    ega_util.run_shell_command(
                        ['htar', '-xvf',
                         os.path.join(
                             run_settings_dict['HPSS_PROD_DIR'],
                             'rh'+YYYY, YYYYmm, YYYYmmdd, hpss_tar_filename
                         ), '/'+hpss_file]
                    )
                else:
                    ega_util.run_shell_command(
                        ['htar', '-xvf',
                         os.path.join(
                             run_settings_dict['HPSS_PROD_DIR'],
                             'rh'+YYYY, YYYYmm, YYYYmmdd, hpss_tar_filename
                         ), './'+hpss_file]
                    )
                ega_util.run_shell_command(['mv', hpss_file, tmp1_file])
            if ega_util.check_file(tmp1_file):
                if not ega_util.check_file(tmp2_file):
                    ega_util.run_shell_command(
                        [run_settings_dict['WGRIB2'], tmp1_file,
                         '-match', '"(:PRATE:surface:)|'
                         +'(:TMP:2 m above ground:)"', '-grib',
                         tmp2_file]
                    )
                if ega_util.check_file(tmp2_file):
                    ega_util.convert_grib2_to_grib1(
                        tmp2_file, archive_file,
                        run_settings_dict['CNVGRIB']
                    )
            ega_util.check_file(archive_file)
    else:
        print(run_settings_dict['FILE_TYPE']+" not recongized")
        sys.exit(1)
    if fhr >= 240:
        fhr+=12
    else:
        fhr+=int(run_settings_dict['FHR_INC'])

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
