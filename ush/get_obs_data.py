"""
About:
        This script gets observational data. It
        gathers GDAS and NAM prepbufr files, and
        24 hour accumulation CCPA files from
        verf_precip (all in COMROOT), and
        CPC rain gauge from an FTP.
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
                  default: /lfs/h2/emc/stmp/$USER/run_get_obs_data
        --obs: optional, observation name,
               default: prepbufr_gdas
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import os
import sys
import datetime
import numpy as np
import netCDF4 as netcdf
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
           +"default: /lfs/h2/emc/vpppg/noscrub/$USER/obs_archive\n"
           +"   --rundir=RUN_DIR        optional, "
           +"default: /lfs/h2/emc/stmp/$USER/run_get_obs_data\n"
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
                    +'/run_get_obs_data')
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
run_settings_dict['cpc_rain_gauge_ftp'] = 'ftp.cpc.ncep.noaa.gov'
run_settings_dict['cpc_rain_gauge_ftp_dir'] = 'GIS/JAWF/Precip'
run_settings_dict['prepbufr_gdas_cycle_list'] = ['00', '06', '12', '18']
run_settings_dict['prepbufr_nam_cycle_list'] = ['00', '06', '12', '18']
run_settings_dict['prepbufr_nam_suffix_list'] = ['tm00', 'tm03']
run_settings_dict['prepbufr_rap_cycle_list'] = ['00', '03', '06', '09',
                                                '12', '15', '18', '21']
run_settings_dict['ccpa_accum6hr_valid_hr_list'] = ['00', '06', '12', '18']
run_settings_dict['nesdis_get_d_ftp'] = 'ftp://ftp.star.nesdis.noaa.gov'
run_settings_dict['nesdis_get_d_ftp_dir'] = ('pub/smcd/emb/lfang/'
                                             +'GET-D_ET_H_updated')
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
    'ccpa_ver': 'v4.2',
    'gfs_ver': 'v16.3',
    'nam_ver': 'v4.2',
    'obsproc_ver': 'v1.1',
    'verf_precip_ver': 'v4.5',
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
if run_settings_dict['OBS'] in ['prepbufr_gdas', 'prepbufr_nam',
                                'prepbufr_rap']:
    obs_archive_dir = os.path.join(
        run_settings_dict['ARCHIVE_DIR'],
        run_settings_dict['OBS'].partition('_')[0],
        run_settings_dict['OBS'].partition('_')[2]
    )
else:
    obs_archive_dir = os.path.join(
        run_settings_dict['ARCHIVE_DIR'], run_settings_dict['OBS']
    )
if run_settings_dict['SENDARCH'] == 'YES':
    if not os.path.exists(obs_archive_dir):
        print("Making directory "+obs_archive_dir)
        os.makedirs(obs_archive_dir)
        if run_settings_dict['OBS'] in ['prepbufr_gdas', 'prepbufr_nam',
                                        'prepbufr_rap']:
            ega_util.set_rstprod_permissions(obs_archive_dir)
base_obs_run_dir = os.path.join(
    run_settings_dict['RUN_DIR'], run_settings_dict['OBS']
)
if not os.path.exists(base_obs_run_dir):
    print("Making directory "+base_obs_run_dir)
    os.makedirs(base_obs_run_dir)
    if run_settings_dict['OBS'] in ['prepbufr_gdas', 'prepbufr_nam',
                                    'prepbufr_rap']:
        ega_util.set_rstprod_permissions(base_obs_run_dir)
os.chdir(base_obs_run_dir)
print("In run directory: "+base_obs_run_dir)

# Get obs data
# prepbufr_gdas - Operational GDAS prepbufr files
if run_settings_dict['OBS'] == 'prepbufr_gdas':
    #gdas_prod_dir = os.path.join(
    #    run_settings_dict['COMROOT'], 'gfs', run_settings_dict['gfs_ver']
    #)
    gdas_prod_dir = os.path.join(
        run_settings_dict['COMROOT'], 'obsproc', run_settings_dict['obsproc_ver']
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
            ega_util.set_rstprod_permissions(obs_run_dir)
        os.chdir(obs_run_dir)
        print("In run directory: "+obs_run_dir)
        for cyc in run_settings_dict['prepbufr_gdas_cycle_list']:
            run_file = os.path.join(
                obs_run_dir, 'prepbufr.gdas.'+PDYm+cyc
            )
            archive_file = os.path.join(
                obs_archive_dir, 'prepbufr.gdas.'+PDYm+cyc
            )
            source_file = os.path.join(
                gdas_prod_dir, 'gdas.'+PDYm, cyc, 'atmos',
                'gdas.t'+cyc+'z.prepbufr'
            )
            if not ega_util.check_file(archive_file):
                ega_util.copy_file(source_file, run_file)
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    if ega_util.check_file(archive_file):
                        ega_util.set_rstprod_permissions(archive_file)
# prepbufr_nam - Operational NAM prepbufr files
elif run_settings_dict['OBS'] == 'prepbufr_nam':
    #nam_prod_dir = os.path.join(
    #    run_settings_dict['COMROOT'], 'nam', run_settings_dict['nam_ver']
    #)
    nam_prod_dir = os.path.join(
        run_settings_dict['COMROOT'], 'obsproc', run_settings_dict['obsproc_ver']
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_archive_PDYm_dir = os.path.join(obs_archive_dir, 'nam.'+PDYm)
        if run_settings_dict['SENDARCH'] == 'YES':
            if not os.path.exists(obs_archive_PDYm_dir):
                print("Making directory "+obs_archive_PDYm_dir)
                os.makedirs(obs_archive_PDYm_dir)
                ega_util.set_rstprod_permissions(obs_archive_PDYm_dir)
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
            ega_util.set_rstprod_permissions(obs_run_dir)
        os.chdir(obs_run_dir)
        print("In run directory: "+obs_run_dir)
        for cyc in run_settings_dict['prepbufr_nam_cycle_list']:
            for suffix in run_settings_dict['prepbufr_nam_suffix_list']:
                run_file = os.path.join(
                    obs_run_dir, 'nam.t'+cyc+'z.prepbufr.'+suffix
                )
                archive_file = os.path.join(
                    obs_archive_PDYm_dir, 'nam.t'+cyc+'z.prepbufr.'+suffix
                )
                source_file = os.path.join(
                    nam_prod_dir, 'nam.'+PDYm, 'nam.t'+cyc+'z.prepbufr.'+suffix
                )
                if not ega_util.check_file(archive_file):
                    ega_util.copy_file(source_file, run_file)
                    if run_settings_dict['SENDARCH'] == 'YES':
                        ega_util.copy_file(run_file, archive_file)
                        if ega_util.check_file(archive_file):
                            ega_util.set_rstprod_permissions(archive_file)
# prepbufr_rap - Operational RAP prepbufr files
elif run_settings_dict['OBS'] == 'prepbufr_rap':
    rap_prod_dir = os.path.join(
        run_settings_dict['COMROOT'], 'obsproc', run_settings_dict['obsproc_ver']
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_archive_PDYm_dir = os.path.join(obs_archive_dir, 'rap.'+PDYm)
        if run_settings_dict['SENDARCH'] == 'YES':
            if not os.path.exists(obs_archive_PDYm_dir):
                print("Making directory "+obs_archive_PDYm_dir)
                os.makedirs(obs_archive_PDYm_dir)
                ega_util.set_rstprod_permissions(obs_archive_PDYm_dir)
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
            ega_util.set_rstprod_permissions(obs_run_dir)
        os.chdir(obs_run_dir)
        print("In run directory: "+obs_run_dir)
        for cyc in run_settings_dict['prepbufr_rap_cycle_list']:
            run_file = os.path.join(
                obs_run_dir, 'rap.t'+cyc+'z.prepbufr.tm00'
            )
            archive_file = os.path.join(
                obs_archive_PDYm_dir, 'rap.t'+cyc+'z.prepbufr.tm00'
            )
            source_file = os.path.join(
                rap_prod_dir, 'rap.'+PDYm, 'rap.t'+cyc+'z.prepbufr.tm00'
            )
            if not ega_util.check_file(archive_file):
                ega_util.copy_file(source_file, run_file)
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    if ega_util.check_file(archive_file):
                        ega_util.set_rstprod_permissions(archive_file)
# ccpa_accum24hr - CCPA 24 hour accumulation files
elif run_settings_dict['OBS'] == 'ccpa_accum24hr':
    CCPA24HR_ACCUM = os.path.join(
        run_settings_dict['HOMEemc_global_archive'], 'exec',
        'ccpa24hr_accum'
    )
    ccpa_accum24hr_prod_dir = os.path.join(
        run_settings_dict['COMROOT'], 'verf_precip',
        run_settings_dict['verf_precip_ver']
    )
    ccpa_prod_dir = os.path.join(
        run_settings_dict['COMROOT'], 'ccpa',
        run_settings_dict['ccpa_ver']
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        PDYm_dt = datetime.datetime.strptime(PDYm, '%Y%m%d')
        PDYm_m1_dt = PDYm_dt - datetime.timedelta(hours=24)
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        print("In run directory: "+obs_run_dir)
        run_file = os.path.join(
            obs_run_dir, 'ccpa.'+PDYm+'12.24h'
        )
        archive_file = os.path.join(
            obs_archive_dir, 'ccpa.'+PDYm+'12.24h'
        )
        source_file = os.path.join(
            ccpa_accum24hr_prod_dir, 'precip.'+PDYm, 'ccpa.'+PDYm+'12.24h'
        )
        if not ega_util.check_file(archive_file):
            input_acc_ccpa_file = os.path.join(obs_run_dir, 'input_acc_ccpa')
            with open(input_acc_ccpa_file, 'w') as write_iac:
                write_iac.write('obs\n')
                write_iac.write('ccpa.\n')
                ccpa1 = os.path.join(
                    ccpa_prod_dir, 'ccpa.'+PDYm_m1_dt.strftime('%Y%m%d'), '18',
                    'ccpa.t18z.06h.hrap.conus'
                )
                if os.path.exists(ccpa1):
                    write_iac.write(ccpa1+'\n')
                ccpa2=os.path.join(
                    ccpa_prod_dir, 'ccpa.'+PDYm, '00',
                    'ccpa.t00z.06h.hrap.conus'
                )
                if os.path.exists(ccpa2):
                    write_iac.write(ccpa2+'\n')
                ccpa3=os.path.join(
                    ccpa_prod_dir, 'ccpa.'+PDYm, '06',
                    'ccpa.t06z.06h.hrap.conus'
                )
                if os.path.exists(ccpa3):
                    write_iac.write(ccpa3+'\n')
                ccpa4=os.path.join(
                    ccpa_prod_dir, 'ccpa.'+PDYm, '12',
                    'ccpa.t12z.06h.hrap.conus'
                )
                if os.path.exists(ccpa4):
                    write_iac.write(ccpa4)
            ega_util.run_shell_command(
                [CCPA24HR_ACCUM, '<', input_acc_ccpa_file]
            )
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.copy_file(run_file, archive_file)
                ega_util.check_file(archive_file)
# ccpa_accum6hr - CCPA 6 hour accumulation files
elif run_settings_dict['OBS'] == 'ccpa_accum6hr':
    ccpa_accum6hr_prod_dir = os.path.join(
        run_settings_dict['COMROOT'], 'ccpa',
        run_settings_dict['ccpa_ver']
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        print("In run directory: "+obs_run_dir)
        for valid_hr in run_settings_dict['ccpa_accum6hr_valid_hr_list']:
            for grid in ['hrap', '1p0']:
                run_file = os.path.join(
                    obs_run_dir, 'ccpa.'+grid+'.'+PDYm+valid_hr+'.6h'
                )
                archive_file = os.path.join(
                    obs_archive_dir, 'ccpa.'+grid+'.'+PDYm+valid_hr+'.6h'
                )
                source_file = os.path.join(
                    ccpa_accum6hr_prod_dir, 'ccpa.'+PDYm, valid_hr,
                    'ccpa.t'+valid_hr+'z.06h.'+grid+'.conus.gb2'
                )
                if not ega_util.check_file(archive_file):
                    ega_util.copy_file(source_file, run_file)
                    if run_settings_dict['SENDARCH'] == 'YES':
                        ega_util.copy_file(run_file, archive_file)
                        ega_util.check_file(archive_file)
# nohrsc_accum24hr - NOHRSC 24 hour accumulation files
elif run_settings_dict['OBS'] == 'nohrsc_accum24hr':
    nohrsc_accum24hr_prod_dir = os.path.join(
        run_settings_dict['DCOMROOT']
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        print("In run directory: "+obs_run_dir)
        run_file = os.path.join(
            obs_run_dir, 'nohrsc.'+PDYm+'12.24h'
        )
        archive_file = os.path.join(
            obs_archive_dir, 'nohrsc.'+PDYm+'12.24h'
        )
        source_file = os.path.join(
            nohrsc_accum24hr_prod_dir, PDYm, 'wgrbbul', 'nohrsc_snowfall',
            'sfav2_CONUS_24h_'+PDYm+'12_grid184.grb2'
        )
        if not ega_util.check_file(archive_file):
            ega_util.copy_file(source_file, run_file)
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.copy_file(run_file, archive_file)
                ega_util.check_file(archive_file)
#osi_saf - sea ice concentration files
elif run_settings_dict['OBS'] == 'osi_saf':
    osi_saf_prod_dir = os.path.join(
        run_settings_dict['DCOMROOT']
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        PDYm_dt = datetime.datetime.strptime(PDYm, '%Y%m%d')
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        print("In run directory: "+obs_run_dir)
        # Daily NH and SH files
        for hem in ['nh', 'sh']:
            daily_hem_run_file = os.path.join(
                obs_run_dir, 'ice_conc_'+hem+'_polstere-100_multi_'
                +PDYm_dt.strftime('%Y%m%d')+'1200.nc'
            )
            daily_hem_archive_file = os.path.join(
                obs_archive_dir, 'ice_conc_'+hem+'_polstere-100_multi_'
                +PDYm_dt.strftime('%Y%m%d')+'1200.nc'
            )
            if not ega_util.check_file(daily_hem_archive_file):
                source_hem_file = os.path.join(
                    osi_saf_prod_dir, PDYm_dt.strftime('%Y%m%d'),
                    'seaice', 'osisaf',
                    'ice_conc_'+hem+'_polstere-100_multi_'
                    +PDYm_dt.strftime('%Y%m%d')+'1200.nc'
                )
                if not ega_util.check_file(daily_hem_run_file):
                    ega_util.copy_file(source_hem_file, daily_hem_run_file)
                if ega_util.check_file(daily_hem_run_file):
                    if run_settings_dict['SENDARCH'] == 'YES':
                        ega_util.copy_file(daily_hem_run_file, daily_hem_archive_file)
# get_d - NESDIS GET_D Flux files
elif run_settings_dict['OBS']  == 'get_d':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        PDYm_dt = datetime.datetime.strptime(PDYm, '%Y%m%d')
        PDYm_YYYY = PDYm_dt.strftime('%Y')
        PDYm_j = PDYm_dt.strftime('%j')
        ftp_file = os.path.join(PDYm_YYYY, 'GETDL3_DAL_CONUS_'
                                +PDYm_YYYY+PDYm_j+'_1.0.nc')
        run_file = os.path.join(obs_run_dir, 'GETDL3_DAL_CONUS_'
                                    +PDYm_YYYY+PDYm_j+'_1.0.nc')
        archive_file = os.path.join(obs_archive_dir, 'GETDL3_DAL_CONUS_'
                                    +PDYm_YYYY+PDYm_j+'_1.0.nc')
        if not ega_util.check_file(archive_file):
            ega_util.run_shell_command(
                ['lftp', '-c',
                 'open '+run_settings_dict['nesdis_get_d_ftp']+'; '
                 'cd '+run_settings_dict['nesdis_get_d_ftp_dir']+'; '
                 'get '+ftp_file+' -o '+run_file]
            )
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.copy_file(run_file, archive_file)
                ega_util.check_file(archive_file)
# ghrsst_ospo - GHRSST OSPO SST
elif run_settings_dict['OBS']  == 'ghrsst_ospo':
    ghrsst_ospo_prod_dir = os.path.join(
        run_settings_dict['DCOMROOT']
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        PDYm_dt = datetime.datetime.strptime(PDYm, '%Y%m%d')
        prod_file = os.path.join(ghrsst_ospo_prod_dir,
                                 PDYm_dt.strftime('%Y%m%d'),
                                 'validation_data', 'marine',
                                 'ghrsst', PDYm_dt.strftime('%Y%m%d')
                                 +'_OSPO_L4_GHRSST.nc')
        run_file = os.path.join(obs_run_dir,
                                PDYm_dt.strftime('%Y%m%d')
                                +'_OSPO_L4_GHRSST.nc')
        archive_file = os.path.join(obs_archive_dir,
                                    PDYm_dt.strftime('%Y%m%d')
                                    +'_OSPO_L4_GHRSST.nc')
        if not ega_util.check_file(archive_file):
            ega_util.copy_file(prod_file, run_file)
            if ega_util.check_file(run_file):
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    ega_util.check_file(archive_file)
# ndbc_buoy - NDBC buoy
elif run_settings_dict['OBS']  == 'ndbc_buoy':
    ndbc_buoy_prod_dir = os.path.join(
        run_settings_dict['DCOMROOT']
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        PDYm_dt = datetime.datetime.strptime(PDYm, '%Y%m%d')
        prod_files = os.path.join(ndbc_buoy_prod_dir,
                                  PDYm_dt.strftime('%Y%m%d'),
                                  'validation_data', 'marine',
                                  'buoy')
        run_file = os.path.join(obs_run_dir,
                                f"buoy_{PDYm_dt:%Y%m%d}.tar")
        archive_file = os.path.join(obs_archive_dir,
                                    f"buoy_{PDYm_dt:%Y%m%d}.tar")
        if not ega_util.check_file(archive_file):
            if len(glob.glob(prod_files+'/*')) != 0:
                ega_util.run_shell_command(
                    ['tar', '-cvf', run_file, '-C', prod_files, '.']
                )
                if ega_util.check_file(run_file):
                    if run_settings_dict['SENDARCH'] == 'YES':
                        ega_util.copy_file(run_file, archive_file)
                        ega_util.check_file(archive_file)
            else:
                print(f"No files matching {prod_files}/*")
# JASON3 - satellite altimetry
elif run_settings_dict['OBS']  == 'jason3':
    jason3_prod_dir = os.path.join(
        run_settings_dict['DCOMROOT']
    )
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        PDYm_dt = datetime.datetime.strptime(PDYm, '%Y%m%d')
        prod_file = os.path.join(jason3_prod_dir,
                                 PDYm_dt.strftime('%Y%m%d'),
                                 'b031', 'xx124')
        run_file = os.path.join(obs_run_dir,
                                'jason3_b031_xx124_'
                                +PDYm_dt.strftime('%Y%m%d'))
        archive_file = os.path.join(obs_archive_dir,
                                    'jason3_b031_xx124_'
                                     +PDYm_dt.strftime('%Y%m%d'))
        if not ega_util.check_file(archive_file):
            ega_util.copy_file(prod_file, run_file)
            if ega_util.check_file(run_file):
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(run_file, archive_file)
                    ega_util.check_file(archive_file)
# OBSPRCP - CPC rain gauge files
elif run_settings_dict['OBS'] == 'OBSPRCP':
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        ftp_file = 'prcp-obs-'+PDYm+'.txt'
        run_file = os.path.join(obs_run_dir, 'usa-dlyprcp-'+PDYm)
        archive_file = os.path.join(obs_archive_dir, 'usa-dlyprcp-'+PDYm)
        if not ega_util.check_file(archive_file):
            ega_util.run_shell_command(
                ['wget',
                 'https://'
                 +run_settings_dict['cpc_rain_gauge_ftp']+'/'
                 +run_settings_dict['cpc_rain_gauge_ftp_dir']+'/'
                 +ftp_file]
            )
            ega_util.run_shell_command(
                ['mv', ftp_file, run_file]
            )
            #ega_util.run_shell_command(
            #    ['lftp', '-c', 
            #     'open '+run_settings_dict['cpc_rain_gauge_ftp']+'; '
            #     +'cd '+run_settings_dict['cpc_rain_gauge_ftp_dir']+'; '
            #     +'get '+ftp_file+' -o '+archive_file]
            #)
            if run_settings_dict['SENDARCH'] == 'YES':
                ega_util.copy_file(run_file, archive_file)
                ega_util.check_file(archive_file)
else:
    print(run_settings_dict['OBS']+" not recongized")
    sys.exit(1)

print("\nEND: "+sys.argv[0]+" at "+str(datetime.datetime.today())+"\n")
