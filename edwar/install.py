import configparser
import os
import sys

from . import file_loader as fl
from . import init_db as idb

__all__ = {
    'structure_configfile',
    'all_ini',
    'db_configfile'
}

structure_ini_default = '''[DEVICE]

[VARIABLES EVERION] # to read input files
bop_1533550392847_VitalSign_gsr_5b2cc93e71b0710100a724db_1533160800_1533247259 = EDA
bop_1533550392847_VitalSign_hr_5b2cc93e71b0710100a724db_1533160800_1533247259 = HR

[VARIABLES E4]
EDA = EDA
IBI = IBI
TEMP = TEMP
ACC = ACCx, ACCy, ACCz

[FEATURES EVERION] # to write output in database (data_type)
eda_module = EDA, SCL, SCR
acc_module = ACCx, ACCy, ACCz
ibi_module = IBI
temp_module = TEMP

[FEATURES E4]
eda_module = EDA, SCL, SCR
acc_module = ACCx, ACCy, ACCz
ibi_module = IBI
temp_module = TEMP
'''


def _configuration_structure(structureini_file):
    config1 = configparser.ConfigParser(inline_comment_prefixes="#", allow_no_value=True)
    config1.optionxform = str
    if not os.path.exists(structureini_file):
        print("Configuration file {} not found. New {} created".format(structureini_file, structureini_file))
        config1.add_section('DEVICE')
        with open(structureini_file, 'w') as confFile:
            config1.write(confFile)

    config1.read(structureini_file)

    # DEVICE SECTION
    try:
        device = config1.options(section='DEVICE')
        if len(device) > 0:
            device = device[0]
    except Exception as err:
        raise Exception('Error while accesing to section DEVICE of {}: {}'.format(structureini_file, err))
    try:
        load_function = config1.get(section='DEVICE', option=device)
    except configparser.NoOptionError:
        load_function = None
    while not device:
        print('\n\t--Device Selection--')
        device = input('Device (E4, Everion or other): ')
        if device == 'E4':
            load_function = 'loader_e4'
        elif device == 'Everion':
            load_function = 'loader_everion'
    if not load_function:
        print('Select from list a function to load data')
        load_function = input('{}: '.format(fl.__all__))
    while load_function not in fl.__all__:
        print("\n\t(!) Something went wrong: function %s not found\n" % load_function +
              "Select from list a function to load data")
        load_function = input('{}: '.format(fl.__all__))
    config1['DEVICE'] = {device: load_function}

    # VARIABLES SECTION
    variables_from_device = 'VARIABLES ' + device.upper()
    try:
        variables = config1.items(section=variables_from_device)
    except configparser.NoSectionError:
        variables = list()
    except Exception as err:
        raise Exception('Error while accessing to {}: {}'.format(variables_from_device, err))

    if not variables:
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


def all_ini():
    structure_configfile()
    db_configfile()


def structure_configfile(default=True):
    structure_ini_file = "structure.ini"
    if default:
        f = open(structure_ini_file, "w")
        f.write(structure_ini_default)
        f.close()
    _configuration_structure(structure_ini_file)
    

def db_configfile():
    dbini_file = "db.ini"
    config2 = configparser.ConfigParser(inline_comment_prefixes="#")
    if not os.path.exists(dbini_file):
        print("Configuration file {} not found. New {} created".format(dbini_file, dbini_file))
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
