import os

from . import configure

__all__ = {
    'structure_cfg',
    'all_cfgs',
    'database_cfg'
}

__structure_ini_default = '''[DEVICES]
Everion = LoaderEverion
E4 = LoaderE4

[VARIABLES EVERION]
gsr = EDA
IBI = IBI
objtemp = TEMP

[FEATURES EVERION]
EDAparser = EDA, SCL, SCR
IBIparser = IBI
TEMPparser = TEMP

[VARIABLES E4]
ACC = ACCx,ACCy,ACCz
EDA = EDA
TEMP = TEMP
IBI = IBI

[FEATURES E4]
IBIparser = IBI
TEMPparser = TEMP
EDAparser = EDA, SCL, SCR
ACCparser = ACCx, ACCy, ACCz
'''


def __host_configuration():
    print('\t--Host Configuration--')
    host = input('Host address: ')
    port = input('Port number: ')
    return host, port


def __user_identification():
    print('\t--User Identification--')
    user = input('User Name: ')
    pwd = input('Password: ')
    return user, pwd


def all_cfgs(settings=configure.Settings(), default=True):
    structure_cfg(settings=settings, default=default)
    database_cfg(settings=settings)


def structure_cfg(settings=configure.Settings(), default=True):
    path = settings.path
    if not os.path.exists(path):
        print("Configuration directory {} not found. New created.".format(path))
        os.mkdir(path)
    structure_ini_file = settings.structureini
    structure_ini_path = os.path.join(path, structure_ini_file)
    if not os.path.exists(structure_ini_path):
        print("Configuration file {} not found. New created.".format(structure_ini_file))
        open(structure_ini_path, "w+")

    if default:
        f = open(structure_ini_path, "w")
        f.write(__structure_ini_default)
        f.close()
    configure.devices(settings)
    

def database_cfg(settings=configure.Settings()):
    path = settings.path
    if not os.path.exists(path):
        print("Configuration directory {} not found. New created.".format(path))
        os.mkdir(path)
    db_ini_file = settings.databaseini
    db_ini_path = os.path.join(path, db_ini_file)
    if not os.path.exists(db_ini_path):
        order = "w+"
        print("Configuration file {} not found. New created.".format(db_ini_file))
    else:
        order = "w"
    f = open(db_ini_path, order)
    f.write(b'8S8aBTETssJ4JL4or2ld/3DmqST1Dx6qDQxsM6SBBIs='.decode('UTF-8'))
    f.close()
    configure.connection_database('', settings)
