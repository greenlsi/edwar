import os
import sys

from . import initialize_database as idb
from .utils.rw_ini import Structure

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


def _configuration_structure(structureini_file):
    s = Structure(structureini_file)

    # DEVICE SECTION
    devices = s.devices()
    device = None
    print('\n\t--Device Section--')
    if len(devices) == 0:
        ans = 'y'
    else:
        print('Available devices:')
        for dev in devices.keys():
            print('\t-%s' % dev)
        ans = input('Do you want to create a new device (y/n): ')
    if ans == 'y':
        device = input('Name of new device: ')
        s.set_device(device, '*')

    while not device:
        device = input('Select device to configure: ')
        if device not in devices.keys():
            print("\n\t(!) Something went wrong: Device %s not found\n" % device)
            device = None

    # VARIABLES SECTION
    variables = s.variables(device)

    print('\n\t--Variable Selection--')
    print('From every file select which variables will be used')
    new_variables = dict()
    file = 'file'
    n = 0
    while file:
        n += 1
        file = input('File %i name (without extension, e.g. .csv) to open (Press enter to exit): ' % n)
        if file:
            i = 0
            variable = 'variable'
            variables_set = set()
            variables_per_file = ''
            while variable:
                i += 1
                variable = input('Variable %i (Press enter to finish): ' % i)
                if variable:
                    if variable in variables_set:
                        print("\n\t(!) Something went wrong: Variable {} already declared\n".format(variable))
                        i -= 1
                    else:
                        variables_set.add(variable)
                        if variables_per_file:
                            variables_per_file += ','
                        variables_per_file += variable
                elif not variable and i == 1:
                    print("\n\t(!) Something went wrong: At least one variable per file is expected\n")
                    variable = 'variable'
                    i = 0
            new_variables[file] = variables_per_file
        config1[variables_from_device] = new_variables

    # FEATURES SECTION
    features_from_module = 'FEATURES ' + device.upper()
    try:
        features = config1.items(section=features_from_module)
    except configparser.NoSectionError:
        features = list()
    except Exception as err:
        raise Exception('Error while accessing to {}: {}'.format(features_from_module, err))

    if not features:
        print('\n\t--Feature Selection--')
        print('From every python module select which features will be output')
        new_features = dict()
        module = 'module'
        n = 0
        while module:
            n += 1
            module = input('Module %i name to use (Press enter to exit): ' % n)
            if module:
                i = 0
                feature = 'feature'
                features_set = set()
                features_per_module = ''
                while feature:
                    i += 1
                    feature = input('Feature %i (Press enter to finish): ' % i)
                    if feature:
                        if feature in features_set:
                            print("\n\t(!) Something went wrong: Feature {} already declared\n".format(feature))
                            i -= 1
                        else:
                            features_set.add(feature)
                            if features_per_module:
                                features_per_module += ','
                            features_per_module += feature
                    elif not feature and i == 1:
                        print("\n\t(!) Something went wrong: At least one feature per module is expected\n")
                        feature = 'feature'
                        i = 0
                new_features[module] = features_per_module
        config1[features_from_module] = new_features
    with open(structureini_file, 'w') as confFile:
        config1.write(confFile)


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


def all_configfiles():
    structure_configfile()
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
    _configuration_structure(structure_ini_path)
    

def database_configfile():
    path = 'configuration'
    if not os.path.exists(path):
        os.mkdir(path)
    db_ini_file = "database.ini"
    db_ini_path = os.path.join(path, db_ini_file)
    if not os.path.exists(db_ini_path):
        print("Configuration file {} not found. New {} created".format(db_ini_file, db_ini_file))
        config2['DB'] = {'Host': '',
                         'Port': '',
                         'User': '',
                         'Password': '',
                         'DB_name': '',
                         'tb_name': ''}
        with open('db.ini', 'w') as confFile:
            config2.write(confFile)

    config2.read(dbini_file)

    try:
        user = config2.get("DB", "User")
        pwd = config2.get("DB", "Password")
        host = config2.get("DB", "Host")
        port = config2.get("DB", "Port")
        db = config2.get("DB", "DB_name")
        tb = config2.get("DB", "tb_name")
    except Exception as err:
        print("\n\t(!) Something went wrong reading {}: {}".format(dbini_file, err) + "\n\tCheck file or remove it ")
        sys.exit(1)

    if not user or not pwd:
        host, port = _host_configuration()

    if not user or not pwd:
        user, pwd = _user_identification()

    finished = False
    tries = 0
    while not finished:
        try:
            idb.test_connect(host, port, user, pwd)
            finished = True
            print("\n\tconnection with host {} established".format(host))
        except IOError:
            print('\n\t(!) Connection went wrong\n' +
                  '\tConnection parameters must be reconfigured\n')
            host, port = _host_configuration()
            finished = False
        except ValueError:
            print('\n\t(!) Something is wrong with your user name or password\n' +
                  '\tIdentification parameters must be reconfigured\n')
            user, pwd = _user_identification()
            finished = False
        tries += 1
        if tries > 5:
            raise Exception("\n\t(!) Something went wrong: exceeded maximum number of attempts to connect " +
                            "to database\n")

    config2['DB'] = {'Host': host,
                     'Port': port,
                     'User': user,
                     'Password': pwd,
                     'DB_name': db,
                     'tb_name': tb}

    with open('db.ini', 'w') as confFile:
        config2.write(confFile)

    idb.connect()
