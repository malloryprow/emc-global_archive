"""
About:
        This script hold utilies and definitions
        for the EMC global archive python scripts
Author(s):
        Mallory Row (mallory.row@noaa.gov)
History Log:
        November 2021 - Inital version
Command Line Agruments:
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import os
import sys
import datetime
import subprocess
import re
import shutil

def run_shell_command(command):
    """! Run shell command

         Args:
             command - list of agrument entries

         Returns:

    """
    print("--- RUNNING "+' '.join(command))
    if any(mark in ' '.join(command) for mark in ['"', "'", '|', '*']):
        run_command = subprocess.run(
            ' '.join(command), shell=True
        )
    else:
        run_command = subprocess.run(command)
    if run_command.returncode != 0:
        print("ERROR: "+' '.join(run_command.args)+" gave return code "
              +str(run_command.returncode))

def get_PDYm_dict(PDY):
    """! Get dictionary of date and previous days

         Args:
             PDY       - string of date in YYYYmmdd form

         Returns:
             PDYm_dict - dictionary containing 7 days of
                         previous days from PDY (strings
                         in YYYYmmdd)

    """
    PDY_dt = datetime.datetime.strptime(PDY, '%Y%m%d')
    PDYm_dict = {
        'PDYm0': (PDY_dt - datetime.timedelta(days=0)).strftime('%Y%m%d'),
        'PDYm1': (PDY_dt - datetime.timedelta(days=1)).strftime('%Y%m%d'),
        'PDYm2': (PDY_dt - datetime.timedelta(days=2)).strftime('%Y%m%d'),
        'PDYm3': (PDY_dt - datetime.timedelta(days=3)).strftime('%Y%m%d'),
        'PDYm4': (PDY_dt - datetime.timedelta(days=4)).strftime('%Y%m%d'),
        'PDYm5': (PDY_dt - datetime.timedelta(days=5)).strftime('%Y%m%d'),
        'PDYm6': (PDY_dt - datetime.timedelta(days=6)).strftime('%Y%m%d'),
        'PDYm7': (PDY_dt - datetime.timedelta(days=7)).strftime('%Y%m%d')
    }
    print("\nDate Information")
    for PDYm in list(PDYm_dict.keys()):
        print("Using "+PDYm+" as "+PDYm_dict[PDYm])
    print("")
    return PDYm_dict

def get_machine_dict():
    """! Get dictionary of dev, prod, current, and other
        WCOSS2 machines

         Args:

         Returns:
             wcoss2_dict - dictionary containing
                           dev, prod, current, and other
                           WCOSS2 machines
    """
    wcoss2_dict = {}
    wcoss2_config_machine_output = subprocess.run(
        ['cat', '/lfs/h1/ops/prod/config/prodmachinefile'],
        capture_output=True
    ).stdout.decode('utf-8').rstrip().split('\n')
    for config_machine in wcoss2_config_machine_output:
        config = config_machine.split(':')[0]
        machine = config_machine.split(':')[1]
        if config == 'primary':
            wcoss2_dict['PROD'] = machine
        elif config == 'backup':
            wcoss2_dict['DEV'] = machine
    hostname = os.environ['HOSTNAME']
    cactus_match = re.match(re.compile(r"^clogin[0-9]{2}$"), hostname)
    dogwood_match = re.match(re.compile(r"^dlogin[0-9]{2}$"), hostname)
    if cactus_match:
        wcoss2_dict['CURRENT'] = 'cdxfer.wcoss2.ncep.noaa.gov'
        wcoss2_dict['OTHER'] = 'ddxfer.wcoss2.ncep.noaa.gov'
    elif dogwood_match:
        wcoss2_dict['CURRENT'] = 'ddxfer.wcoss2.ncep.noaa.gov'
        wcoss2_dict['OTHER'] = 'cdxfer.wcoss2.ncep.noaa.gov'
    print("\nWCOSS2 machine information...")
    for status in list(wcoss2_dict.keys()):
        print(status+' -> '+wcoss2_dict[status])
    print("")
    return wcoss2_dict

def check_file(file_path):
    """! Check if file exists and is not 0 sized

         Args:
             file_path      - string of full path to
                              file

         Returns:
            file_check_good - boolean of file status

    """
    if os.path.exists(file_path):
        if os.stat(file_path).st_size != 0:
            file_check_good = True
            print("EXISTS "+file_path)
        else:
            file_check_good = False
            print("SIZE 0, REMOVING "+file_path)
            os.remove(file_path)
    else:
        file_check_good = False
        print("DOES NOT EXIST "+file_path)
    return file_check_good

def copy_file(src, dest):
    """! Copy file if on machine locally

         Args:
             src          - string of full path to
                            source file
             dest         - string of full path to
                            destintation file

         Returns:

    """
    if os.path.exists(src):
        if os.stat(src).st_size != 0:
            print("--- COPYING "+src+" TO "+dest)
            shutil.copy2(src, dest)
    else:
        print("--- "+src+" DOES NOT EXIST")
    if os.path.exists(dest):
        if os.stat(dest).st_size == 0:
            print("--- SIZE 0, REMOVING "+dest)
            os.remove(dest)

def link_file(src, dest):
    """! Link file if on machine locally

         Args:
             src          - string of full path to
                            source file
             dest         - string of full path to
                            destintation file

         Returns:

    """
    if os.path.exists(src):
        print("--- LINKING "+src+" TO "+dest)
        os.symlink(src, dest)
    else:
        print("DOES NOT EXIST "+src)
    if os.path.exists(dest):
        if os.stat(dest).st_size == 0:
            print("--- SIZE 0, REMOVING "+dest)
            os.remove(dest)

def convert_grib1_to_grib2(file_grib1, file_grib2, cnvgrib):
    """! Convert file from GRIB1 to GRIB2
         
         Args:
             file_grib1 - string of full path to
                          GRIB1 file
             file_grib2 - string of full path to
                          GRIB2 file
             cnvgrib    - string of full path to
                          cnvgrib executable

         Returns:
         
    """
    run_shell_command(
        [cnvgrib, '-g12', file_grib1, file_grib2]
    )

def convert_grib2_to_grib1(file_grib2, file_grib1, cnvgrib):
    """! Convert file from GRIB2 to GRIB1
         
         Args:
             file_grib2 - string of full path to
                          GRIB2 file
             file_grib1 - string of full path to
                          GRIB1 file
             cnvgrib    - string of full path to
                          cnvgrib executable

         Returns:
         
    """
    run_shell_command(
        [cnvgrib, '-g21', file_grib2, file_grib1]
    )

def regrid_copygb(file_in, file_out, grid, copygb):
    """! Convert file from GRIB2 to GRIB1
         
         Args:
             file_in  - string of full path to
                        in file
             file_out - string of full path to
                        out file
             grid     - string to regrid to
             copygb   - string of full path to
                        copygb executable

         Returns:
         
    """
    run_shell_command(
        [copygb, '-g'+grid, '-x', file_in, file_out]
    )

def set_rstprod_permissions(file_path):
    """! Change files permissions and group
         to rstprod
         
         Args:
             file_path      - string of full path to
                              file
    """
    run_shell_command(['chmod', '750', file_path])
    run_shell_command(['chgrp', 'rstprod', file_path])
