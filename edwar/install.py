import os
import sys

from . import initialize_database as idb
from . import configure

__all__ = {
    'structure_configfile',
    'all_configfiles',
    'database_configfile'
}

structure_ini_default = '''[DEVICES]
E4 = LoaderE4
Everion = LoaderEverion

[VARIABLES EVERION] # to read input files
bop_1533550392847_VitalSign_gsr_5b2cc93e71b0710100a724db_1533160800_1533247259 = EDA
bop_1533550392847_VitalSign_hr_5b2cc93e71b0710100a724db_1533160800_1533247259 = HR

[VARIABLES E4]
EDA = EDA
IBI = IBI
TEMP = TEMP
ACC = ACCx, ACCy, ACCz

[FEATURES EVERION] # to write output in database (data_type)
eda_parser = EDA, SCL, SCR
acc_parser = ACCx, ACCy, ACCz
ibi_parser = IBI
temp_parser = TEMP

[FEATURES E4]
eda_parser = EDA, SCL, SCR
acc_parser = ACCx, ACCy, ACCz
ibi_parser = IBI
temp_parser = TEMP
'''

database_ini_default = '''[DB]
Host = 
Port = 
User = 
Password = 
DB_name = 
tb_name = 
'''


def _host_configuration():
    print('\t--Host Configuration--')
    host = input('Host address: ')
    port = input('Port number: ')
    return host, port


def _user_identification():
    print('\t--User Identification--')
    user = input('User Name: ')
    pwd = input('Password: ')
    return user, pwd


def all_configfiles(default=True):
    structure_configfile(default)
    database_configfile()


def structure_configfile(default=True):
    path = 'configuration'
    if not os.path.exists(path):
        os.mkdir(path)
    structure_ini_file = "structure.ini"
    structure_ini_path = os.path.join(path, structure_ini_file)
    if not os.path.exists(structure_ini_path):
        print("Configuration file {} not found. New {} created".format(structure_ini_file, structure_ini_file))
        open(structure_ini_path, "w+")

    if default:
        f = open(structure_ini_path, "w")
        f.write(structure_ini_default)
        f.close()
    configure.devices()
    

def database_configfile():
    path = 'configuration'
    if not os.path.exists(path):
        os.mkdir(path)
    db_ini_file = "database.ini"
    db_ini_path = os.path.join(path, db_ini_file)
    if not os.path.exists(db_ini_path):
        print("Configuration file {} not found. New {} created".format(db_ini_file, db_ini_file))
        f = open(db_ini_path, "w+")
        f.write(database_ini_default)
        f.close()
    configure.connection()
