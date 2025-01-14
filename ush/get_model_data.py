"""
About:
        This script gets data from various
        global models. It will reformat the
        data as needed for that model.
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
                  default: /lfs/h2/emc/stmp/$USER/run_get_model_data
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
import subprocess
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
           +"default: /lfs/h2/emc/stmp/$USER/run_get_model_data\n"
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
                    +'/run_get_model_data')
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
env_var_dict = {
    'COMROOT': '/lfs/h1/ops/prod/com',
    'DCOMROOT': '/lfs/h1/ops/prod/dcom',
    'OPSROOT': '/lfs/h1/ops/prod',
    'COPYGB': ('/apps/ops/prod/libs/intel/19.1.3.304/grib_util/1.2.3/bin/'
               +'copygb'),
    'COPYGB2': ('/apps/ops/prod/libs/intel/19.1.3.304/grib_util/1.2.3/bin/'
               +'copygb2'),
    'WGRIB': ('/apps/ops/prod/libs/intel/19.1.3.304/grib_util/1.2.3/bin/'
               +'wgrib'),
    'WGRIB2': '/apps/ops/prod/libs/intel/19.1.3.304/wgrib2/2.0.8/bin/wgrib2',
    'CNVGRIB': ('/apps/ops/prod/libs/intel/19.1.3.304/grib_util/1.2.3/bin/'
                +'cnvgrib'),
    'cdas_ver': 'v1.2',
    'cmc_ver': 'v1.2',
    'cfs_ver': 'v2.3',
    'ens_tracker_ver': 'v1.3',
    'gefs_ver': 'v12.3',
    'gfs_ver': 'v16.3',
    'naefs_ver': 'v6.1',
    'HOMEemc_global_archive': os.path.join(os.getcwd(), '..'),
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
    if not os.path.exists(model_archive_dir):
        print("Making directory "+model_archive_dir)
        os.makedirs(model_archive_dir)
        if run_settings_dict['MODEL'] in ['ecm', 'ecmg4']:
            ega_util.set_rstprod_permissions(model_archive_dir)
base_model_run_dir = os.path.join(
    run_settings_dict['RUN_DIR'], run_settings_dict['MODEL']
)
if not os.path.exists(base_model_run_dir):
    print("Making directory "+base_model_run_dir)
    os.makedirs(base_model_run_dir)
    if run_settings_dict['MODEL'] in ['ecm', 'ecmg4']:
        ega_util.set_rstprod_permissions(base_model_run_dir)
os.chdir(base_model_run_dir)
print("In run directory: "+base_model_run_dir)

# Get model data
# cdas - GFS version used for the NCEP/NCAR Reanalysis Project
if run_settings_dict['MODEL'] == 'cdas':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        PDYm_YYYYmm = PDYm[0:6]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['COMROOT'], run_settings_dict['MODEL'],
            run_settings_dict['cdas_ver'], 'cdas.'+PDYm_YYYYmm
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.cdas.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.cdas.'+CDATE
            )
            source_file = os.path.join(
                model_prod_path, 'pgb.f'+fhr2+CDATE
            )
            if not ega_util.check_file(archive_file):
                ega_util.copy_file(source_file, run_file)
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    ega_util.check_file(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.cdas.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.cdas.'+CDATE
        )
        source_file = os.path.join(
            model_archive_dir, 'pgbf00.cdas.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.link_file(source_file, archive_file)
                ega_util.check_file(archive_file)
# cfsr - Legacy GFS used for Climate Forecast System Reanalysis
elif run_settings_dict['MODEL'] == 'cfsr':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        CDATE_YYYY = CDATE[0:4]
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['COMROOT'], 'cfs',
            run_settings_dict['cfs_ver'], 'cfs.'+PDYm,
            run_settings_dict['CYCLE'].zfill(2), '6hrly_grib_01'
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            run_file = os.path.join(
               model_run_dir, 'pgbf'+fhr2+'.cfsr.'+CDATE
            )
            archive_file = os.path.join(
               model_archive_dir, 'pgbf'+fhr2+'.cfsr.'+CDATE
            )
            VDATE_dt = (datetime.datetime.strptime(CDATE, '%Y%m%d%H')
                        +datetime.timedelta(hours=fhr))
            source_file = os.path.join(
                model_prod_path,
                'pgbf'+VDATE_dt.strftime('%Y%m%d%H')+'.01.'+CDATE+'.grb2'
            )
            if not ega_util.check_file(archive_file):
                ega_util.copy_file(source_file, run_file)
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    ega_util.check_file(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.cfsr.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.cfsr.'+CDATE
        )
        source_file = os.path.join(
            run_settings_dict['COMROOT'], 'cfs',
            run_settings_dict['cfs_ver'], 'cdas.'+PDYm,
            'cdas1.t'+run_settings_dict['CYCLE'].zfill(2)+'z.pgrblanl'
        )
        if not ega_util.check_file(archive_file):
            ega_util.copy_file(source_file, run_file)
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.copy_file(run_file, archive_file)
                ega_util.check_file(archive_file)
# cmc - Operational Canadian Meteorological Center
elif run_settings_dict['MODEL'] == 'cmc':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['COMROOT'], run_settings_dict['MODEL'],
            run_settings_dict['cmc_ver'], 'cmc.'+PDYm
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            fhr3 = str(fhr).zfill(3)
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.cmc.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.cmc.'+CDATE
            )
            source_file = os.path.join(
                model_prod_path, 'cmc_'+CDATE+'f'+fhr3
            )
            if not ega_util.check_file(archive_file):
                ega_util.copy_file(source_file, run_file)
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    ega_util.check_file(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.cmc.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.cmc.'+CDATE
        )
        source_file = os.path.join(
            model_archive_dir, 'pgbf00.cmc.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.link_file(source_file, archive_file)
                ega_util.check_file(archive_file)
# ecm - Operational European Center for Medium-Range Weather Forecasts
elif run_settings_dict['MODEL'] == 'ecm':
    ECM2NCEPGRIB = os.path.join(
        run_settings_dict['HOMEemc_global_archive'], 'exec',
        'ecm_gfs_look_alike_new'
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        CDATE_mmdd = CDATE[4:8]
        CDATE_mmddHH = CDATE[4:]
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
            ega_util.set_rstprod_permissions(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['DCOMROOT'], PDYm, 'wgrbbul', 'ecmwf'
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            fhr3 = str(fhr).zfill(3)
            VDATE_dt = (datetime.datetime.strptime(CDATE, '%Y%m%d%H')
                        +datetime.timedelta(hours=fhr))
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.ecm.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.ecm.'+CDATE
            )
            source_file = os.path.join(
                model_prod_path,
                'DCD'+CDATE_mmddHH+'00'+VDATE_dt.strftime('%m%d%H')+'001'
            )
            tmp_file = os.path.join(model_run_dir, 'tmp.f'+fhr3+'.'+CDATE)
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp_file):
                    ega_util.copy_file(source_file, tmp_file)
                if ega_util.check_file(tmp_file):
                    ega_util.set_rstprod_permissions(tmp_file)
                    ega_util.run_shell_command(
                        [ECM2NCEPGRIB, tmp_file, run_file]
                    )
                    if run_settings_dict['SENDARCH'] == 'YES':
                        ega_util.copy_file(run_file, archive_file)
                        if ega_util.check_file(archive_file):
                            ega_util.set_rstprod_permissions(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
        for cycx in ['00', '06', '12', '18']:
            run_file = os.path.join(
                model_run_dir, 'pgbf00.ecm.'+PDYm+cycx
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf00.ecm.'+PDYm+cycx
            )
            source_file = os.path.join(
                model_prod_path,
                'DCD'+CDATE_mmdd+cycx+'00'+CDATE_mmdd+cycx+'001'
            )
            tmp_file = os.path.join(model_run_dir, 'tmp.f000.'+PDYm+cycx)
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp_file):
                    ega_util.copy_file(source_file, tmp_file)
                if ega_util.check_file(tmp_file):
                    ega_util.set_rstprod_permissions(tmp_file)
                    ega_util.run_shell_command(
                        [ECM2NCEPGRIB, tmp_file, run_file]
                    )
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    if ega_util.check_file(archive_file):
                        ega_util.set_rstprod_permissions(archive_file)
            run_file = os.path.join(
                model_run_dir, 'pgbanl.ecm.'+PDYm+cycx
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbanl.ecm.'+PDYm+cycx
            )
            source_file = os.path.join(
                model_archive_dir, 'pgbf00.ecm.'+PDYm+cycx
            )
            if not ega_util.check_file(archive_file):
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.link_file(source_file, archive_file)
                    if ega_util.check_file(archive_file):
                        ega_util.set_rstprod_permissions(archive_file)
# ecmg4 - Operational European Center for Medium-Range Weather Forecasts Hi-Res
elif run_settings_dict['MODEL'] == 'ecmg4':
    ecmg4_var_kpds_dict = {
        'surface 10-m zonal wind': '4*-1,165,1,0',
        'surface 10-m meridional wind': '4*-1,166,1,0',
        'surface 2-m temperature': '4*-1,167,1,0',
        'surface 2-m dew-point temperature': '4*-1,168,1,0',
        'surface Mean sea-level pressure [Pa]': '4*-1,151,1,0',
        'surface Snow depth [m of water equivalent]': '4*-1,141,1,0',
        'surface Total cloud cover [(0 - 1)]': '4*-1,164,1,0',
        'surface Total column water [kg m**-2]': '4*-1,136,1,0',
        'surface Total precipitation [m]': '4*-1,228,1,0',
    }
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        CDATE_mmddHH = CDATE[4:]
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
            ega_util.set_rstprod_permissions(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['DCOMROOT'], PDYm, 'wgrbbul', 'ecmwf'
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            fhr3 = str(fhr).zfill(3)
            VDATE_dt = (datetime.datetime.strptime(CDATE, '%Y%m%d%H')
                        +datetime.timedelta(hours=fhr))
            run_file = os.path.join(
                model_run_dir, 'flxf'+fhr2+'.ecm.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'flxf'+fhr2+'.ecm.'+CDATE
            )
            if fhr2 == '00':
                source_file_suffix = '011'
            else:
                source_file_suffix = '001'
            source_file = os.path.join(
                model_prod_path,
                'U1D'+CDATE_mmddHH+'00'+VDATE_dt.strftime('%m%d%H')
                +source_file_suffix
            )
            tmpnlcopygb_file = os.path.join(model_run_dir, 'tmpnlcopygb')
            tmp_file = os.path.join(model_run_dir, 'tmp.f'+fhr3+'.'+CDATE)
            if not os.path.exists(tmpnlcopygb_file):
                tmpnlcopygb = open(tmpnlcopygb_file, 'w')
                tmpnlcopygb.write(
                    ' &NLCOPYGB IDS(49)=2, IDS(165)=2, IDS(166)=2, '
                    +'IDS(168)=2, IDS(167)=2, IDS(159)=2, IDS(59)=2, '
                    +'IDS(31)=2, IDS(156)=2, IDS(151)=2, IDS(3)=2, '
                    +'IDS(157)=2, IDS(134)=2, IDS(130)=2, IDS(131)=2, '
                    +'IDS(132)=2, IDS(138)=7, IDS(121)=2, IDS(122)=2, '
                    +'IDS(143)=4, IDS(142)=4, IDS(141)=4, IDS(144)=4, '
                    +'IDS(164)=4, IDS(136)=4, IDS(228)=4, IDS(135)=4, /'
                )
                tmpnlcopygb.close()
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp_file):
                    ega_util.copy_file(source_file, tmp_file)
                if ega_util.check_file(tmp_file):
                    ega_util.set_rstprod_permissions(tmp_file)
                    for var, kpds in ecmg4_var_kpds_dict.items():
                        ega_util.run_shell_command(
                            [run_settings_dict['COPYGB'], '-N', tmpnlcopygb_file,
                             '-k"'+kpds+'"', '-a', '-x', tmp_file,
                             run_file]
                        )
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    if ega_util.check_file(archive_file):
                        ega_util.set_rstprod_permissions(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
# fno -  Operational U.S. Navy Fleet Numerical Meteorology and Oceanograpy Center
elif run_settings_dict['MODEL'] == 'fno':
    model_prod_path = os.path.join(
        run_settings_dict['DCOMROOT'], 'navgem'
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            fhr3 = str(fhr).zfill(3)
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.fno.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.fno.'+CDATE
            )
            source_file = os.path.join(
                model_prod_path, 'US058GMET-OPSbd2.NAVGEM'+fhr3+'-'+CDATE
                +'-NOAA-halfdeg.gr2'
            )
            tmp1_file = os.path.join(model_run_dir, 'tmp.f'+fhr3+'.'+CDATE)
            tmp2_file = os.path.join(
                model_run_dir, 'tmp.grib1.f'+fhr3+'.'+CDATE
            )
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp1_file):
                    ega_util.copy_file(source_file, tmp1_file)
                if ega_util.check_file(tmp1_file):
                    if not ega_util.check_file(tmp2_file):
                        ega_util.convert_grib2_to_grib1(
                            tmp1_file, tmp2_file,
                            run_settings_dict['CNVGRIB']
                        )
                    if ega_util.check_file(tmp2_file):
                        ega_util.regrid_copygb(
                            tmp2_file, run_file, '3',
                            run_settings_dict['COPYGB']
                        )
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    ega_util.check_file(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.fno.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.fno.'+CDATE
        )
        source_file = os.path.join(
            model_archive_dir, 'pgbf00.fno.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.link_file(source_file, archive_file)
                ega_util.check_file(archive_file)
# gefsc - Operational Global Ensemble Forecast System - Control
elif run_settings_dict['MODEL'] == 'gefsc':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['COMROOT'], 'gefs',
            run_settings_dict['gefs_ver'], 'gefs.'+PDYm,
            run_settings_dict['CYCLE'].zfill(2), 'atmos', 'pgrb2ap5'
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            fhr3 = str(fhr).zfill(3)
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.gefsc.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.gefsc.'+CDATE
            )
            source_file = os.path.join(
                model_prod_path, 'gec00.t'+run_settings_dict['CYCLE'].zfill(2)
                +'z.pgrb2a.0p50.f'+fhr3
            )
            tmp_file = os.path.join(model_run_dir, 'tmp.f'+fhr3+'.'+CDATE)
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp_file):
                    ega_util.copy_file(source_file, tmp_file)
                if ega_util.check_file(tmp_file):
                    ega_util.convert_grib2_to_grib1(
                        tmp_file, run_file,
                        run_settings_dict['CNVGRIB']
                    )
                    if run_settings_dict['SENDARCH'] == 'YES':
                        ega_util.link_file(run_file, archive_file)
                        ega_util.check_file(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.gefsc.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.gefsc.'+CDATE
        )
        source_file = os.path.join(
            model_archive_dir, 'pgbf00.gefsc.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.link_file(source_file, archive_file)
                ega_util.check_file(archive_file)
# gefsm - Operational Global Ensemble Forecast System - Mean
elif run_settings_dict['MODEL'] == 'gefsm':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['COMROOT'], 'gefs',
            run_settings_dict['gefs_ver'], 'gefs.'+PDYm,
            run_settings_dict['CYCLE'].zfill(2), 'atmos', 'pgrb2ap5'
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            fhr3 = str(fhr).zfill(3)
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.gefsm.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.gefsm.'+CDATE
            )
            source_file = os.path.join(
                model_prod_path, 'geavg.t'+run_settings_dict['CYCLE'].zfill(2)
                +'z.pgrb2a.0p50.f'+fhr3
            )
            tmp_file = os.path.join(model_run_dir, 'tmp.f'+fhr3+'.'+CDATE)
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp_file):
                    ega_util.copy_file(source_file, tmp_file)
                if ega_util.check_file(tmp_file):
                    ega_util.convert_grib2_to_grib1(
                        tmp_file, run_file,
                        run_settings_dict['CNVGRIB']
                    )
                    if run_settings_dict['SENDARCH'] == 'YES':
                        ega_util.copy_file(run_file, archive_file)
                        ega_util.check_file(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.gefsm.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.gefsm.'+CDATE
        )
        source_file = os.path.join(
            run_settings_dict['ARCHIVE_DIR'], 'gfs',
            'pgbanl.gfs.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.link_file(source_file, archive_file)
                ega_util.check_file(archive_file)
elif run_settings_dict['MODEL'] == 'gfs':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['COMROOT'], run_settings_dict['MODEL'],
            run_settings_dict['gfs_ver'], 'gfs.'+PDYm,
            run_settings_dict['CYCLE'].zfill(2), 'atmos'
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            fhr3 = str(fhr).zfill(3)
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.gfs.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.gfs.'+CDATE
            )
            source_file = os.path.join(
                model_prod_path, 'gfs.t'+run_settings_dict['CYCLE'].zfill(2)
                +'z.pgrb2.1p00.f'+fhr3
            )
            tmp_file = os.path.join(
                model_run_dir, 'tmp.pgrb2.1p00.gfs.f'+fhr3+'.'+CDATE
            )
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp_file):
                    ega_util.copy_file(source_file, tmp_file)
                if ega_util.check_file(tmp_file):
                    ega_util.convert_grib2_to_grib1(
                        tmp_file, run_file,
                        run_settings_dict['CNVGRIB']
                    )
                    if run_settings_dict['SENDARCH'] == 'YES':
                        ega_util.copy_file(run_file, archive_file)
                        ega_util.check_file(archive_file)
            if fhr <= 240:
                run_file = os.path.join(
                    model_run_dir, 'flxf'+fhr2+'.gfs.'+CDATE
                )
                archive_file = os.path.join(
                    model_archive_dir, 'flxf'+fhr2+'.gfs.'+CDATE
                )
                source_file = os.path.join(
                    model_prod_path, 'gfs.t'
                    +run_settings_dict['CYCLE'].zfill(2)+'z.sfluxgrbf'+fhr3
                    +'.grib2'
                )
                tmp1_file = os.path.join(
                    model_run_dir, 'tmp.sfluxgrb.gfs.f'+fhr3+'.'+CDATE
                )
                tmp2_file = os.path.join(
                    model_run_dir, 'tmp.sfluxgrb.gfs.PRATE.2mTMP.f'
                    +fhr3+'.'+CDATE
                )
                if not ega_util.check_file(archive_file):
                    if not ega_util.check_file(tmp1_file):
                        ega_util.copy_file(source_file, tmp1_file)
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
                                tmp2_file, run_file,
                                run_settings_dict['CNVGRIB']
                            )
                        if run_settings_dict['SENDARCH'] == 'YES':
                            ega_util.copy_file(run_file, archive_file)
                            ega_util.check_file(archive_file)
            if fhr >= 240:
                fhr+=12
            else:
                fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.gfs.'+CDATE
        ) 
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.gfs.'+CDATE
        )
        source_file = os.path.join(
            model_prod_path, 'gfs.t'+run_settings_dict['CYCLE'].zfill(2)
            +'z.pgrb2.1p00.anl'
        )
        tmp_file = os.path.join(
            model_run_dir, 'tmp.pgrb2.1p00.gfs.anl.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if not ega_util.check_file(tmp_file):
                ega_util.copy_file(source_file, tmp_file)
            if ega_util.check_file(tmp_file):
                ega_util.convert_grib2_to_grib1(
                    tmp_file, run_file,
                    run_settings_dict['CNVGRIB']
                )
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.copy_file(run_file, archive_file)
                ega_util.check_file(archive_file)
        for fs in ['anl', 'f000', 'f006']:
            source_file = os.path.join(
                run_settings_dict['COMROOT'], run_settings_dict['MODEL'],
                run_settings_dict['gfs_ver'], 'gdas.'+PDYm,
                run_settings_dict['CYCLE'].zfill(2), 'atmos',
                'gdas.t'+run_settings_dict['CYCLE'].zfill(2)
                +'z.pgrb2.1p00.'+fs
            )
            if fs != 'anl':
                run_file = os.path.join(
                    model_run_dir, 'pgbf'+fs[2:]+'.gdas.'+CDATE
                )
                archive_file = os.path.join(
                    model_archive_dir, 'pgbf'+fs[2:]+'.gdas.'+CDATE
                )
            else:
                run_file = os.path.join(
                    model_run_dir, 'pgb'+fs+'.gdas.'+CDATE
                )
                archive_file = os.path.join(
                    model_archive_dir, 'pgb'+fs+'.gdas.'+CDATE
                )
            tmp_file = os.path.join(
                model_run_dir, 'tmp.pgrb2.1p00.gdas.'+fs+'.'+CDATE
            )
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp_file):
                    ega_util.copy_file(source_file, tmp_file)
                if ega_util.check_file(tmp_file):
                    ega_util.convert_grib2_to_grib1(
                        tmp_file, run_file,
                        run_settings_dict['CNVGRIB']
                    )
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    ega_util.check_file(archive_file)
        source_file = os.path.join(
            run_settings_dict['COMROOT'], 'ens_tracker',
            run_settings_dict['ens_tracker_ver'], 'gfs.'+PDYm,
            run_settings_dict['CYCLE'].zfill(2), 'tctrack',
            'avn.t'+run_settings_dict['CYCLE'].zfill(2)
            +'z.cyclone.trackatcfunix'
        )
        run_file = os.path.join(
            model_run_dir, 'atcfunix.gfs.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'atcfunix.gfs.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            ega_util.copy_file(source_file, run_file)
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.copy_file(run_file, archive_file)
                ega_util.check_file(archive_file)
elif run_settings_dict['MODEL'] == 'gfs_wcoss2_para':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            '/lfs/h1/ops/para/com', 'gfs',
            run_settings_dict['gfs_ver'], 'gfs.'+PDYm,
            run_settings_dict['CYCLE'].zfill(2), 'atmos'
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            fhr3 = str(fhr).zfill(3)
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.gfs.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.gfs.'+CDATE
            )
            source_file = os.path.join(
                model_prod_path, 'gfs.t'+run_settings_dict['CYCLE'].zfill(2)
                +'z.pgrb2.1p00.f'+fhr3
            )
            tmp_file = os.path.join(
                model_run_dir, 'tmp.pgrb2.1p00.gfs.f'+fhr3+'.'+CDATE
            )
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp_file):
                    ega_util.copy_file(source_file, tmp_file)
                if ega_util.check_file(tmp_file):
                    ega_util.convert_grib2_to_grib1(
                        tmp_file, run_file,
                        run_settings_dict['CNVGRIB']
                    )
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    ega_util.check_file(archive_file)
            if fhr <= 240:
                run_file = os.path.join(
                    model_run_dir, 'flxf'+fhr2+'.gfs.'+CDATE
                )
                archive_file = os.path.join(
                    model_archive_dir, 'flxf'+fhr2+'.gfs.'+CDATE
                )
                source_file = os.path.join(
                    model_prod_path, 'gfs.t'
                    +run_settings_dict['CYCLE'].zfill(2)+'z.sfluxgrbf'+fhr3
                    +'.grib2'
                )
                tmp1_file = os.path.join(
                    model_run_dir, 'tmp.sfluxgrb.gfs.f'+fhr3+'.'+CDATE
                )
                tmp2_file = os.path.join(
                    model_run_dir, 'tmp.sfluxgrb.gfs.PRATE.2mTMP.f'
                    +fhr3+'.'+CDATE
                )
                if not ega_util.check_file(archive_file):
                    if not ega_util.check_file(tmp1_file):
                        ega_util.copy_file(source_file, tmp1_file)
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
                                tmp2_file, run_file,
                                run_settings_dict['CNVGRIB']
                            )
                        if run_settings_dict['SENDARCH'] == 'YES':
                            ega_util.copy_file(run_file, archive_file)
                            ega_util.check_file(archive_file)
            if fhr >= 240:
                fhr+=12
            else:
                fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.gfs.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.gfs.'+CDATE
        )
        source_file = os.path.join(
            model_prod_path, 'gfs.t'+run_settings_dict['CYCLE'].zfill(2)
            +'z.pgrb2.1p00.anl'
        )
        tmp_file = os.path.join(
            model_run_dir, 'tmp.pgrb2.1p00.gfs.anl.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if not ega_util.check_file(tmp_file):
                ega_util.copy_file(source_file, tmp_file)
            if ega_util.check_file(tmp_file):
                ega_util.convert_grib2_to_grib1(
                    tmp_file, run_file,
                    run_settings_dict['CNVGRIB']
                )
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.copy_file(run_file, archive_file)
                ega_util.check_file(archive_file)
        for fs in ['anl', 'f000', 'f006']:
            source_file = os.path.join(
                run_settings_dict['COMROOT'], 'gfs',
                run_settings_dict['gfs_ver'], 'gdas.'+PDYm,
                run_settings_dict['CYCLE'].zfill(2), 'atmos',
                'gdas.t'+run_settings_dict['CYCLE'].zfill(2)
                +'z.pgrb2.1p00.'+fs
            )
            if fs != 'anl':
                run_file = os.path.join(
                    model_run_dir, 'pgbf'+fs[2:]+'.gdas.'+CDATE
                )
                archive_file = os.path.join(
                    model_archive_dir, 'pgbf'+fs[2:]+'.gdas.'+CDATE
                )
            else:
                run_file = os.path.join(
                    model_run_dir, 'pgb'+fs+'.gdas.'+CDATE
                )
                archive_file = os.path.join(
                    model_archive_dir, 'pgb'+fs+'.gdas.'+CDATE
                )
            tmp_file = os.path.join(
                model_run_dir, 'tmp.pgrb2.1p00.gdas.'+fs+'.'+CDATE
            )
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp_file):
                    ega_util.copy_file(source_file, tmp_file)
                if ega_util.check_file(tmp_file):
                    ega_util.convert_grib2_to_grib1(
                        tmp_file, run_file,
                        run_settings_dict['CNVGRIB']
                    )
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    ega_util.check_file(archive_file)
elif run_settings_dict['MODEL'] == 'jma':
    JMAMERGE = os.path.join(
        run_settings_dict['HOMEemc_global_archive'], 'exec',
        'jma_merge'
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['DCOMROOT'], PDYm, 'wgrbbul'
        )
        source_n_file = os.path.join(
            model_prod_path, 'jma_n_'+run_settings_dict['CYCLE'].zfill(2)
        )
        source_s_file = os.path.join(
            model_prod_path, 'jma_s_'+run_settings_dict['CYCLE'].zfill(2)
        )
        tmp_n_file = os.path.join(model_run_dir, 'tmp.n.'+CDATE)
        tmp_s_file = os.path.join(model_run_dir, 'tmp.s.'+CDATE)
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            fhr3 = str(fhr).zfill(3)
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.jma.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.jma.'+CDATE
            )
            tmp_n_fhr_file = os.path.join(
                model_run_dir, 'tmp.n.f'+fhr3+'.'+CDATE
            )
            tmp_s_fhr_file = os.path.join(
                model_run_dir, 'tmp.s.f'+fhr3+'.'+CDATE
            )
            if fhr == 0:
                fhr_file_str = ':anl'
            else:
                fhr_file_str = fhr2+'hr'
            if not ega_util.check_file(archive_file):
                if not ega_util.check_file(tmp_n_file):
                    ega_util.copy_file(source_n_file, tmp_n_file)
                if ega_util.check_file(tmp_n_file):
                    ega_util.run_shell_command(
                        [run_settings_dict['WGRIB']+' '+tmp_n_file+' | '
                         +'grep "'+fhr_file_str+'" | '
                         +run_settings_dict['WGRIB']+' '+tmp_n_file+' -i '
                         +'-grib -o '+tmp_n_fhr_file]
                    )
                if not ega_util.check_file(tmp_s_file):
                    ega_util.copy_file(source_s_file, tmp_s_file)
                if ega_util.check_file(tmp_s_file):
                    ega_util.run_shell_command(
                        [run_settings_dict['WGRIB']+' '+tmp_s_file+' | '
                         +'grep "'+fhr_file_str+'" | '
                         +run_settings_dict['WGRIB']+' '+tmp_s_file+' -i '
                         +'-grib -o '+tmp_s_fhr_file]
                    )
                if ega_util.check_file(tmp_n_fhr_file) \
                        and ega_util.check_file(tmp_s_fhr_file):
                    ega_util.run_shell_command(
                        [JMAMERGE, tmp_n_fhr_file.rpartition('/')[2],
                         tmp_s_fhr_file.rpartition('/')[2],
                         run_file.rpartition('/')[2]]
                    )
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(
                        run_file.rpartition('/')[2], archive_file,
                    )
                    ega_util.check_file(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.jma.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.jma.'+CDATE
        )
        source_file = os.path.join(
            model_archive_dir, 'pgbf00.jma.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.link_file(source_file, archive_file)
                ega_util.check_file(archive_file)
elif run_settings_dict['MODEL'] == 'ncmrwf':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['DCOMROOT'], PDYm, 'wgrbbul',
            'ncmrwf_gdas'
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            fhr3 = str(fhr).zfill(3)
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.ncmrwf.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.ncmrwf.'+CDATE
            )
            source_file = os.path.join(
                model_prod_path, 'gdas1.t'+run_settings_dict['CYCLE'].zfill(2)
                +'z.grbf'+fhr2
            )
            if not ega_util.check_file(archive_file):
                tmp_file = os.path.join(model_run_dir, 'tmp.f'+fhr3+'.'+CDATE)
                if not ega_util.check_file(tmp_file):
                    ega_util.copy_file(source_file, tmp_file)
                if ega_util.check_file(tmp_file):
                    ega_util.convert_grib2_to_grib1(
                        tmp_file, run_file,
                        run_settings_dict['CNVGRIB']
                    )
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    ega_util.check_file(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.ncmrwf.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.ncmrwf.'+CDATE
        )
        source_file = os.path.join(
            model_archive_dir, 'pgbf00.ncmrwf.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.link_file(source_file, archive_file)
                ega_util.check_file(archive_file)
elif run_settings_dict['MODEL'] == 'ukm':
    UKMHIRESMERGE = os.path.join(
        run_settings_dict['HOMEemc_global_archive'], 'exec',
        'ukm_hires_merge'
    )
    ukm_lead_id_dict = {
        '00': 'AAT',
        '06': 'BBT',
        '12': 'CCT',
        '18': 'DDT',
        '24': 'EET',
        '30': 'FFT',
        '36': 'GGT',
        '42': 'HHT',
        '48': 'IIT',
        '54': 'JJT',
        '60': 'JJT',
        '66': 'KKT',
        '72': 'KKT',
        '78': 'QQT',
        '84': 'LLT',
        '90': 'TTT',
        '96': 'MMT',
        '102': 'UUT',
        '108': 'NNT',
        '114': 'VVT',
        '120': 'OOT',
        '126': '11T',
        '132': 'PPA',
        '138': '22T',
        '144': 'PPA'
    }
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        model_run_dir = os.path.join(base_model_run_dir, CDATE)
        if not os.path.exists(model_run_dir):
            print("Making directory "+model_run_dir)
            os.makedirs(model_run_dir)
        os.chdir(model_run_dir)
        print("In run directory: "+model_run_dir)
        model_prod_path = os.path.join(
            run_settings_dict['DCOMROOT'], PDYm, 'wgrbbul',
            'ukmet_hires'
        )
        fhr = int(run_settings_dict['FHR_MIN'])
        while fhr <= int(run_settings_dict['FHR_MAX']):
            fhr2 = str(fhr).zfill(2)
            if fhr2 == '00':
               fhr_wgrib_str = 'anl'
            else:
               fhr_wgrib_str = str(fhr)+'hr'
            run_file = os.path.join(
                model_run_dir, 'pgbf'+fhr2+'.ukm.'+CDATE
            )
            archive_file = os.path.join(
                model_archive_dir, 'pgbf'+fhr2+'.ukm.'+CDATE
            )
            if fhr2 in list(ukm_lead_id_dict.keys()):
                source_file = os.path.join(
                    model_prod_path, 'GAB'+run_settings_dict['CYCLE'].zfill(2)
                    +ukm_lead_id_dict[fhr2]+'.GRB'
                )
                tmp_fhr_file = os.path.join(
                    model_run_dir, 'tmp.'
                    +'GAB'+run_settings_dict['CYCLE'].zfill(2)
                    +ukm_lead_id_dict[fhr2]+'.GRB.f'+str(fhr)
                )
                if not ega_util.check_file(archive_file):
                    if not ega_util.check_file(tmp_fhr_file):
                        ega_util.run_shell_command(
                            [run_settings_dict['WGRIB']+' '+source_file+' | '
                             +'grep "'+fhr_wgrib_str+'" | '
                             +run_settings_dict['WGRIB']+' '+source_file+' -i '
                             +'-grib -o '+tmp_fhr_file]
                        )
                        #ega_util.copy_file(source_file, tmp_file)
                    if ega_util.check_file(tmp_fhr_file):
                        ega_util.run_shell_command(
                            [UKMHIRESMERGE, tmp_fhr_file.rpartition('/')[2],
                             run_file.rpartition('/')[2],
                             str(fhr).zfill(1)]
                        )
                    if run_settings_dict['SENDARCH'] == 'YES':
                        ega_util.copy_file(
                            run_file.rpartition('/')[2], archive_file,
                        )
                        ega_util.check_file(archive_file)
            fhr+=int(run_settings_dict['FHR_INC'])
        run_file = os.path.join(
            model_run_dir, 'pgbanl.ukm.'+CDATE
        )
        archive_file = os.path.join(
            model_archive_dir, 'pgbanl.ukm.'+CDATE
        )
        source_file = os.path.join(
            model_archive_dir, 'pgbf00.ukm.'+CDATE
        )
        if not ega_util.check_file(archive_file):
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.link_file(source_file, archive_file)
                ega_util.check_file(archive_file)
elif run_settings_dict['MODEL'] == 'graphcastgfs':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        CDATE = PDYm+run_settings_dict['CYCLE'].zfill(2)
        aws_url = os.path.join(
            'https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com',
            f"graphcastgfs.{PDYm}", CDATE[-2:]
        )
        for file_levels_num in ['13', '13_test']:
            model_run_dir = os.path.join(base_model_run_dir, file_levels_num,
                                         CDATE)
            if not os.path.exists(model_run_dir):
                print("Making directory "+model_run_dir)
                os.makedirs(model_run_dir)
            os.chdir(model_run_dir)
            print("In run directory: "+model_run_dir)
            file_levels_num_model_archive_dir = os.path.join(
                model_archive_dir, f"graphcastgfs{file_levels_num}",
                f"graphcastgfs.{PDYm}", CDATE[-2:]
            )
            if not os.path.exists(file_levels_num_model_archive_dir):
                print("Making directory "+file_levels_num_model_archive_dir)
                os.makedirs(file_levels_num_model_archive_dir)
            # Set AWS URL for date and cycle
            if file_levels_num == '13_test':
                aws_file_levels_num_url = os.path.join(
                    aws_url, 'forecasts_13_levels_test'
                )
            else:
                aws_file_levels_num_url = os.path.join(
                    aws_url,
                    f"forecasts_{file_levels_num}_levels"
                )
            fhr = int(run_settings_dict['FHR_MIN'])
            while fhr <= int(run_settings_dict['FHR_MAX']):
                fhr3 = str(fhr).zfill(3)
                source_file = os.path.join(
                    aws_file_levels_num_url,
                    f"graphcastgfs.t{CDATE[-2:]}z.pgrb2.0p25.f{fhr3}"
                )
                archive_file = os.path.join(
                    file_levels_num_model_archive_dir,
                    source_file.rpartition('/')[2]
                )
                if not ega_util.check_file(archive_file):
                    print(f"Downloading {source_file}")
                    run_wget = subprocess.run(
                        ['wget', source_file], capture_output=True
                    )
                    if int(run_wget.returncode) != 0:
                        print(run_wget)
                    if run_settings_dict['SENDARCH'] == 'YES':
                        ega_util.copy_file(
                            source_file.rpartition('/')[2], archive_file,
                        )
                        ega_util.check_file(archive_file)
                fhr+=int(run_settings_dict['FHR_INC'])
else:
    print(run_settings_dict['MODEL']+" not recongized")
    sys.exit(1)

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
