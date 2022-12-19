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
#run_settings_dict['copernicus_ghrsst_median_ftp'] = 'ftp://nrt.cmems-du.eu'
#run_settings_dict['copernicus_ghrsst_median_ftp_dir'] = ('Core/SST_GLO_SST_L4_'
#                                                        +'NRT_OBSERVATIONS_010'
#                                                        +'_005/METOFFICE-GLO-'
#                                                        +'SST-L4-NRT-OBS-GMPE-V3')
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
    ccpa_accum24hr_prod_dir = os.path.join(
        run_settings_dict['COMROOT'], 'verf_precip',
        run_settings_dict['verf_precip_ver']
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
            obs_run_dir, 'ccpa.'+PDYm+'12.24h'
        )
        archive_file = os.path.join(
            obs_archive_dir, 'ccpa.'+PDYm+'12.24h'
        )
        source_file = os.path.join(
            ccpa_accum24hr_prod_dir, 'precip.'+PDYm, 'ccpa.'+PDYm+'12.24h'
        )
        if not ega_util.check_file(archive_file):
            ega_util.copy_file(source_file, run_file)
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
            run_file = os.path.join(
                obs_run_dir, 'ccpa.hrap.'+PDYm+valid_hr+'.6h'
            ) 
            archive_file = os.path.join(
                obs_archive_dir, 'ccpa.hrap.'+PDYm+valid_hr+'.6h'
            )
            source_file = os.path.join(
                ccpa_accum6hr_prod_dir, 'ccpa.'+PDYm, valid_hr,
                'ccpa.t'+valid_hr+'z.06h.hrap.conus.gb2'
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
    G004_grid_file = os.path.join(run_settings_dict['HOMEemc_global_archive'],
                                  'fix', 'cdo_grids', 'G004.grid')
    osi_saf_prod_dir = '/lfs/h1/ops/dev/dcom'
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        PDYm_dt = datetime.datetime.strptime(PDYm, '%Y%m%d')
        PDYm_m12hr_dt = PDYm_dt + datetime.timedelta(hours=-12)
        PDYm_m1_dt = PDYm_dt + datetime.timedelta(hours=-24)
        PDYm_m6_dt = PDYm_dt + datetime.timedelta(hours=-144)
        PDYm_m7_dt = PDYm_dt + datetime.timedelta(hours=-168)
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        print("In run directory: "+obs_run_dir)
        # Daily File
        daily_run_file = os.path.join(
            obs_run_dir, 'osi_saf.multi.'
            +PDYm_m1_dt.strftime('%Y%m%d')+'00to'
            +PDYm+'00_G004.nc'
        )
        daily_archive_file = os.path.join(
            obs_archive_dir, 'osi_saf.multi.'
            +PDYm_m1_dt.strftime('%Y%m%d')+'00to'
            +PDYm+'00_G004.nc'
        )
        daily_tmp_file = os.path.join(
            obs_run_dir, 'tmp_osi_saf.multi.'
            +PDYm_m1_dt.strftime('%Y%m%d')+'00to'
            +PDYm+'00_G004.nc'
        )
        if not ega_util.check_file(daily_archive_file):
            for hem in ['nh', 'sh']:
                source_hem_file = os.path.join(
                    osi_saf_prod_dir, PDYm_m12hr_dt.strftime('%Y%m%d'), 
                    'seaice', 'osisaf',
                    'ice_conc_'+hem+'_polstere-100_multi_'
                    +PDYm_m12hr_dt.strftime('%Y%m%d')+'1200.nc'
                )
                tmp_hem_file = os.path.join(
                    obs_run_dir,
                    'osi_saf.multi.'+hem+'.'
                    +PDYm_m1_dt.strftime('%Y%m%d')+'00to'
                    +PDYm+'00.nc'
                )
                tmp_hem_G004_file = os.path.join(
                    obs_run_dir,
                    'osi_saf.multi.'+hem+'.'
                    +PDYm_m1_dt.strftime('%Y%m%d')+'00to'
                    +PDYm+'00_G004.nc'
                )
                if not ega_util.check_file(tmp_hem_file):
                    ega_util.copy_file(source_hem_file, tmp_hem_file)
                if ega_util.check_file(tmp_hem_file):
                    ega_util.run_shell_command(
                        ['cdo', 'remapbil,'+G004_grid_file,
                         tmp_hem_file, tmp_hem_G004_file]
                    )
                if hem == 'nh':
                    tmp_nh_G004_file = tmp_hem_G004_file
                elif hem == 'sh':
                    tmp_sh_G004_file = tmp_hem_G004_file
            if ega_util.check_file(tmp_nh_G004_file) \
                    and ega_util.check_file(tmp_sh_G004_file):
                nh_data = netcdf.Dataset(tmp_nh_G004_file)
                nh_lat = nh_data.variables['lat'][:]
                nh_lon = nh_data.variables['lon'][:]
                nh_ice_conc = nh_data.variables['ice_conc'][:]
                nh_ice_conc_unfiltered = (
                    nh_data.variables['ice_conc_unfiltered'][:]
                )
                nh_time = nh_data.variables['time'][:]
                nh_time_bnds = nh_data.variables['time_bnds'][:]
                sh_data = netcdf.Dataset(tmp_sh_G004_file)
                sh_lat = sh_data.variables['lat'][:]
                sh_lon = sh_data.variables['lon'][:]
                sh_ice_conc = sh_data.variables['ice_conc'][:]
                sh_ice_conc_unfiltered = (
                    sh_data.variables['ice_conc_unfiltered'][:]
                )
                sh_time = sh_data.variables['time'][:]
                sh_time_bnds = sh_data.variables['time_bnds'][:]
                if os.path.exists(daily_tmp_file):
                    os.remove(daily_tmp_file)
                merged_data = netcdf.Dataset(daily_tmp_file, 'w',
                                             format='NETCDF3_CLASSIC')
                for attr in nh_data.ncattrs():
                    if attr == 'history':
                        merged_data.setncattr(
                            attr, nh_data.getncattr(attr)+' '
                            +sh_data.getncattr(attr)
                        )
                    elif attr == 'southernmost_latitude':
                        merged_data.setncattr(attr, '-90')
                    elif attr == 'area':
                        merged_data.setncattr(attr, 'Global')
                    else:
                        merged_data.setncattr(
                            attr, nh_data.getncattr(attr)
                        )
                for dim in list(nh_data.dimensions.keys()):
                    merged_data.createDimension(
                        dim, len(nh_data.dimensions[dim])
                    )
                for var in ['time', 'time_bnds', 'lat', 'lon']:
                    merged_var = merged_data.createVariable(
                        var, nh_data.variables[var].datatype,
                        nh_data.variables[var].dimensions
                    )
                    for k in nh_data.variables[var].ncattrs():
                        merged_var.setncatts(
                            {k: nh_data.variables[var].getncattr(k)}
                        )
                    if var == 'time':
                        merged_var[:] = (
                            nh_data.variables[var][:]
                            + 43200
                        )
                    else:
                        merged_var[:] = nh_data.variables[var][:]
                for var in ['ice_conc', 'ice_conc_unfiltered', 'masks',
                            'confidence_level', 'status_flag',
                            'total_uncertainty', 'smearing_uncertainty',
                            'algorithm_uncertainty']:
                    merged_var = merged_data.createVariable(
                        var, nh_data.variables[var].datatype,
                        ('lat', 'lon')
                    )
                    for k in nh_data.variables[var].ncattrs():
                        if k == 'long_name':
                            merged_var.setncatts(
                                {k: nh_data.variables[var].getncattr(k)\
                                 .replace('northern hemisphere', 'globe')}
                            )
                        else:
                            merged_var.setncatts(
                                {k: nh_data.variables[var].getncattr(k)}
                            )
                    merged_var_vals = np.ma.masked_equal(
                        np.vstack((sh_data.variables[var][0,:180,:],
                                   nh_data.variables[var][0,180:,:]))
                    ,nh_data.variables[var]._FillValue)
                    merged_var[:] = merged_var_vals
                merged_data.close()
                if ega_util.check_file(daily_tmp_file):
                    ega_util.copy_file(daily_tmp_file, daily_run_file)
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(daily_run_file, daily_archive_file)
                    ega_util.check_file(daily_archive_file)
        # Weekly File
        weekly_run_file = os.path.join(
            obs_run_dir,
            'osi_saf.multi.'
            +PDYm_m7_dt.strftime('%Y%m%d')+'00to'
            +PDYm+'00_G004.nc'
        )
        weekly_archive_file = os.path.join(
            obs_archive_dir, 
            'osi_saf.multi.'
            +PDYm_m7_dt.strftime('%Y%m%d')+'00to'
            +PDYm+'00_G004.nc'
        )
        weekly_tmp_file = os.path.join(
            obs_run_dir,
            'tmp_osi_saf.multi.'
            +PDYm_m7_dt.strftime('%Y%m%d')+'00to'
            +PDYm+'00_G004.nc'
        )
        if not ega_util.check_file(weekly_archive_file):
            weekly_daily_file_list = []
            PDYm_m_dt = PDYm_m7_dt
            while PDYm_m_dt <= PDYm_m1_dt:
                daily_archive_file = os.path.join(
                    obs_archive_dir, 'osi_saf.multi.'
                    +PDYm_m_dt.strftime('%Y%m%d')+'00to'
                    +(PDYm_m_dt + datetime.timedelta(days=1))\
                    .strftime('%Y%m%d')+'00_G004.nc'
                )
                if os.path.exists(daily_archive_file):
                    weekly_daily_file_list.append(daily_archive_file)
                PDYm_m_dt = PDYm_m_dt + datetime.timedelta(days=1)
            weekly_daily_file_list = weekly_daily_file_list[::-1]
            if len(weekly_daily_file_list) >= 4:
                ncea_cmd_list = ['ncea']
                for daily_file in weekly_daily_file_list:
                    ncea_cmd_list.append(daily_file)
                ncea_cmd_list.append('-o')
                ncea_cmd_list.append(weekly_tmp_file)
                ega_util.run_shell_command(ncea_cmd_list)
                if ega_util.check_file(weekly_tmp_file):
                    weekly_data = netcdf.Dataset(weekly_tmp_file, 'a',
                                                 format='NETCDF3_CLASSIC')
                    weekly_data.setncattr(
                        'start_date', PDYm_m7_dt.strftime('%Y-%m-%d %H:%M:%S')
                    )
                    osi_saf_date_since_dt = datetime.datetime.strptime(
                        '1978-01-01 00:00:00','%Y-%m-%d %H:%M:%S'
                    )
                    weekly_data.variables['time_bnds'][:] = [
                        (PDYm_m7_dt - osi_saf_date_since_dt).total_seconds(),
                        weekly_data.variables['time_bnds'][:][0][1]
                    ]
                    weekly_data.close()
                if ega_util.check_file(weekly_tmp_file):
                    ega_util.copy_file(weekly_tmp_file, weekly_run_file)
                if run_settings_dict['SENDARCH'] == 'YES':
                    ega_util.copy_file(weekly_run_file, weekly_archive_file)
                    ega_util.check_file(weekly_archive_file)
            else:
                print("Not enough file to make "+weekly_archive_file
                      +": "+' '.join(weekly_daily_file_list))
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
# ghrsst_median - GHRSST Multi-Product Ensemble SST
elif run_settings_dict['OBS']  == 'ghrsst_median':
    ghrsst_median_prod_dir = '/lfs/h1/ops/dev/dcom'
    for PDYm_key in list(PDYm_dict.keys()):
        PDYm = PDYm_dict[PDYm_key]
        obs_run_dir = os.path.join(base_obs_run_dir, PDYm)
        if not os.path.exists(obs_run_dir):
            print("Making directory "+obs_run_dir)
            os.makedirs(obs_run_dir)
        os.chdir(obs_run_dir)
        PDYm_dt = datetime.datetime.strptime(PDYm, '%Y%m%d')
        PDYm_YYYY = PDYm_dt.strftime('%Y')
        PDYm_mm = PDYm_dt.strftime('%m')
        PDYm_m1_dt = PDYm_dt - datetime.timedelta(hours=24)
        PDYm_m1_YYYY = PDYm_m1_dt.strftime('%Y')
        PDYm_m1_mm = PDYm_m1_dt.strftime('%m')
        PDYm_m1 = PDYm_m1_dt.strftime('%Y%m%d')
        prod_file = os.path.join(ghrsst_median_prod_dir,
                                 PDYm_m1, 'validation_data', 'marine',
                                 'ghrsst', PDYm_m1+'120000-'
                                 +'UKMO-L4_GHRSST-SSTfnd-GMPE-GLOB-'
                                 +'v03.0-fv03.0.nc')
        ftp_file = os.path.join(PDYm_m1+'120000-'
                                +'UKMO-L4_GHRSST-SSTfnd-GMPE-GLOB-'
                                +'v03.0-fv03.0.nc')
        run_file = os.path.join(obs_run_dir,
                                'UKMO-L4_GHRSST-SSTfnd-GMPE-GLOB_valid'
                                +PDYm_m1_dt.strftime('%Y%m%d')+'00to'
                                +PDYm+'00.nc')
        archive_file = os.path.join(obs_archive_dir,
                                    'UKMO-L4_GHRSST-SSTfnd-GMPE-GLOB_valid'
                                    +PDYm_m1_dt.strftime('%Y%m%d')+'00to'
                                    +PDYm+'00.nc')
        tmp_file = os.path.join(obs_run_dir, ftp_file)
        if not ega_util.check_file(archive_file):
            #ega_util.run_shell_command(
            #    ['wget', '--ftp-user=mrow', '--ftp-password=EMCvpppg2022',
            #    os.path.join(run_settings_dict['copernicus_ghrsst_median_ftp'],
            #                 run_settings_dict['copernicus_ghrsst_median_ftp_dir'],
            #                 PDYm_m1_YYYY, PDYm_m1_mm, ftp_file)
            #    ]
            #)
            ega_util.copy_file(prod_file, tmp_file)
            if ega_util.check_file(tmp_file):
                ghrsst_median_data = netcdf.Dataset(ftp_file, 'a',
                                                    format='NETCDF3_CLASSIC')
                ghrsst_median_date_since_dt = datetime.datetime.strptime(
                    '1981-01-01 00:00:00','%Y-%m-%d %H:%M:%S'
                )
                ghrsst_median_data['time'][:] = (
                    ghrsst_median_data['time'][:][0]
                    + 43200
                )
                ghrsst_median_data.close()
                ega_util.copy_file(tmp_file, run_file)
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
