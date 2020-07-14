import os
import mysql.connector as sql

from .utils import db_connection as db
from .utils import configuration as conf
from .utils import Settings
from .utils.user_input import check_binary_answer, check_answer
from .loaders.loaders import __enum__

__all__ = {
    'settings_location',
    'devices',
    'data_files',
    'parsers',
    'connection_database'
}


def settings_location(path=None, databaseini=None, structureini=None):
    s = Settings(path, databaseini, structureini)
    return s


def devices(settings=Settings()):
    finished = False
    while not finished:
        print('\n\t\t--Device Configuration--')
        dev = print_devices(settings)
        device = check_answer("Name of device to configure (press 'enter' to exit): ", option_list=[''])
        if not device:
            finished = True
        else:
            if device in dev.keys():
                msg = "New name of device '{}' (press 'enter' to keep name, type 'r' to remove it or 'b' to " \
                      "go back): ".format(device)
                newdevice = check_answer(msg, out_list=dev.keys(), option_list=['', 'r', 'b'])
                load_function = dev[device]
            else:
                create = check_binary_answer("Device '{}' not found, ".format(device) +
                                             "do you want to create it? (y/N): ")
                if create == 'y':
                    newdevice = device
                else:
                    newdevice = 'b'
                load_function = None
            if newdevice == 'r':
                todelete = check_binary_answer("Device '{}' will be deleted. Are you sure? (y/N): ".format(device))
                if todelete == 'y':
                    conf.remove_device(settings, device)
                newdevice = 'b'

            if newdevice != 'b':
                new_load_function = 'invalid'
                while new_load_function == 'invalid':
                    print('Available loaders: ')
                    loaders = __enum__
                    if loaders:
                        for p in loaders:
                            print('\t-{}'.format(p))
                        msg = "New function loader (press 'enter' to keep the current loader '{}'): ". \
                            format(load_function)
                        msg1 = "If your loader is not listed, leave 'None' as value of current loader."
                        new_load_function = check_answer(msg, in_list=loaders, option_list=[''],
                                                         extra_info_not_found=msg1)

                    else:
                        print("\n\t(!) No loaders found.\n")
                        new_load_function = None

                conf.edit_device(settings, device, new_device=newdevice, new_loader=new_load_function)
                data_files(newdevice if newdevice else device, settings)
                parsers(newdevice if newdevice else device, settings)


def print_devices(settings=Settings()):
    dev = conf.get_devices(settings)
    if dev:
        maxlendev = 0
        maxlenload = 0
        for d in dev.keys():
            maxlendev = max(maxlendev, len(d))
            maxlenload = max(maxlenload, len(dev[d]))
        header1 = 'DEVICES'
        header2 = 'LOAD FUNCTION'
        maxlendev = max(maxlendev, len(header1)) + 2
        maxlenload = max(maxlenload, len(header2)) + 2
        table_format = '| {:^' + str(maxlendev) + '}| {:^' + str(maxlenload) + '}|'
        sep = '+' + '-' * (maxlendev + 1) + '+' + '-' * (maxlenload + 1) + '+'
        print("\nCurrent installed devices:\n")
        print(sep)
        print(table_format.format('DEVICE', 'LOAD FUNCTION'))
        print(sep)
        for v in dev.keys():
            print(table_format.format(v, dev[v]))
        print(sep)
    else:
        print("\n\t(!) No devices found.\n")
    return dev


def data_files(device, settings=Settings()):
    print('\n\t\t--Input Configuration--')
    finished = False
    while not finished:
        variables, v_working, v_locked = print_data(device, settings=Settings())
        file = check_answer("Name of file to extract data (press 'enter' to exit): ", option_list=[''])
        if not file:
            finished = True
        else:
            msg = "New name of file '{}' (press 'enter' to keep name, type 'r' to remove it or 'b' to " \
                  "go back): ".format(file)
            if file in variables.keys():
                newfile = check_answer(msg, out_list=variables.keys(), option_list=['', 'r', 'b'])
                variables_in_file = variables[file].replace(' ', '').split(',')
                new_variables = list()
                if file in v_locked.keys():
                    file = '.' + file
                    newfile = '.' + newfile
            else:
                create = check_binary_answer("File '{}' not found, do you want to create it? (y/N): ".format(file))
                if create == 'y':
                    newfile = file
                    file = None
                else:
                    newfile = 'b'
                variables_in_file = list()
                new_variables = list()

            # OPTION LIST: r:remove; b:do nothing, so go back; else:make changes
            if newfile == 'r':
                todelete = check_binary_answer("File '{}' will be deleted. "
                                               "Are you sure? (y/N): ".format(file[1:] if file[0] == '.' else file))
                if todelete == 'y':
                    conf.remove_input_file(settings, device, file)
                newfile = 'b'

            if newfile != 'b':
                # edit existing variables
                for v in variables_in_file:
                    msg = "New name of variable '{}' (press 'enter' to keep name, or type 'r' to remove it): ".format(v)
                    var = check_answer(msg, out_list=new_variables, substitute_dict={'': v}, option_list=['r'])
                    if var != 'r':
                        new_variables.append(var)

                # add new variables
                nvar = 'sthg'
                cont = 0
                while nvar:
                    cont += 1
                    msg = "Name of new variable {} (press 'enter' to exit): ".format(cont)
                    nvar = check_answer(msg, out_list=new_variables, option_list=[''])
                    if nvar:
                        new_variables.append(nvar)
                conf.edit_input(settings, device, file, new_file=newfile, new_variables=new_variables)


def print_data(device, settings=Settings(), input_device=True):
    if input_device:
        da, wo, lo = conf.get_input_variables(settings, device)
        print("\nCurrent configuration of the input files for device '{}':\n".format(device))
        if da:
            maxlenobj = 0
            maxlencontent = 0
            for d in da.keys():
                maxlenobj = max(maxlenobj, len(d))
                maxlencontent = max(maxlencontent, len(da[d]))
            header1 = 'FILE'
            header2 = 'INPUT VARIABLES'
            maxlenobj = max(maxlenobj, len(header1)) + 2
            maxlencontent = max(maxlencontent, len(header2)) + 2
            table_format = '| {:^' + str(maxlenobj) + '}| {:^' + str(maxlencontent) + '}|'
            sep = '+' + '-' * (maxlenobj + 1) + '+' + '-' * (maxlencontent + 1) + '+'
            sep1 = '|{:=^' + str((maxlenobj + maxlencontent + 3)) + '}|'
            sep2 = '+' + '=' * (maxlenobj + maxlencontent + 3) + '+'
            print(sep)
            print(table_format.format(header1, header2))
            if wo:
                print(sep2)
                print(sep1.format(' Selected Files '))
                print(sep2)
                for v in wo.keys():
                    print(table_format.format(v, wo[v]))
            if lo:
                print(sep2)
                print(sep1.format(' Locked Files '))
                print(sep2)
                for v in lo.keys():
                    print(table_format.format(v, lo[v]))
            print(sep)
        else:
            print("\t(!) No configuration of input files for device '{}' found.\n".format(device))

    else:
        da, wo, lo = conf.get_output_features(settings, device)
        print("\nCurrent configuration of the output for device '{}':".format(device))
        if da:
            maxlenobj = 0
            maxlencontent = 0
            for d in da.keys():
                maxlenobj = max(maxlenobj, len(d))
                maxlencontent = max(maxlencontent, len(da[d]))
            header1 = 'PARSER'
            header2 = 'OUTPUT VARIABLES'
            maxlenobj = max(maxlenobj, len(header1)) + 2
            maxlencontent = max(maxlencontent, len(header2)) + 2
            table_format = '| {:^' + str(maxlenobj) + '}| {:^' + str(maxlencontent) + '}|'
            sep = '+' + '-' * (maxlenobj + 1) + '+' + '-' * (maxlencontent + 1) + '+'
            sep1 = '|{:=^' + str((maxlenobj + maxlencontent + 3)) + '}|'
            sep2 = '+' + '=' * (maxlenobj + maxlencontent + 3) + '+'
            print(sep)
            print(table_format.format(header1, header2))
            if wo:
                print(sep2)
                print(sep1.format(' Selected Parsers '))
                print(sep2)
                for v in wo.keys():
                    print(table_format.format(v, wo[v]))
            if lo:
                print(sep2)
                print(sep1.format(' Locked Parsers '))
                print(sep2)
                for v in lo.keys():
                    print(table_format.format(v, lo[v]))
            print(sep)
        else:
            print("\t(!) No configuration of parsers for device '{}' found.\n".format(device))
    return da, wo, lo


def parsers(device, settings=Settings()):
    finished = False
    print('\n\t\t--Output Configuration--')
    while not finished:
        features, f_working, f_locked = print_data(device, settings=settings, input_device=False)
        parser = check_answer("\nName of parser to process data (press 'enter' to exit): ", option_list=[''],
                              not_an_option_list=[' '])
        if not parser:
            finished = True
        else:
            msg = "New name of parser '{}' (press 'enter' to keep name, type 'r' to remove it or 'b' " \
                  "to go back): ".format(parser)
            if parser in features.keys():
                newparser = check_answer(msg, out_list=features.keys(), option_list=['', 'r', 'b'],
                                         not_an_option_list=[' '])
                features_in_parser = features[parser].replace(' ', '').split(',')
                new_features = list()
                if parser in f_locked.keys():
                    parser = '.' + parser
                    newparser = '.' + newparser
            else:
                msg = "Parser '{}' not found, do you want to create it? (y/N): ".format(parser)
                create = check_binary_answer(msg)
                if create == 'y':
                    newparser = None
                else:
                    newparser = 'b'
                features_in_parser = list()
                new_features = list()

            # OPTION LIST: r:remove; b:do nothing, so go back; else:make changes
            if newparser == 'r':
                todelete = check_binary_answer("Parser '{}' will be deleted. Are "
                                               "you sure? (y/N): ".format(parser[1:] if parser[0] == '.' else parser))
                if todelete == 'y':
                    conf.remove_parser(settings, device, parser)
                newparser = 'b'

            if newparser != 'b':
                # edit existing features
                for f in features_in_parser:
                    msg = "New name of feature '{}' (press 'enter' to keep name, or type 'r' to remove it): ".format(f)
                    ftr = check_answer(msg, out_list=new_features, substitute_dict={'': f}, option_list=['r'])
                    if ftr != 'r':
                        new_features.append(ftr)

                # add new features
                nftr = 'sthg'
                cont = 0
                while nftr:
                    cont += 1
                    nftr = check_answer("Name of new feature {} (press 'enter' to exit): ".format(cont),
                                        out_list=new_features, option_list=[''])
                    if nftr:
                        new_features.append(nftr)
                conf.edit_output(settings, device, parser, new_parser=newparser, new_features=new_features)
    print("\nDevice '{}' successfully configured!".format(device))


def files_lock(device=None, settings=Settings()):
    print('\n\t\t--Input Interface--')
    dev = conf.get_devices(settings)
    if not dev:
        raise SystemError("(!) No device installed found: Run 'edwar.configure.devices()' to configure it.")
    if device is not None:
        if device not in dev.keys():
            raise ValueError("(!) Something went wrong: Device '{}' not found.".format(device))
        else:
            pass
    else:
        print_devices(settings)
        device = check_answer("\nSelect device (press 'enter' to exit): ", in_list=dev.keys(), option_list=[''])
        if not device:
            return

    while 1:
        all_files, f_working, f_locked = print_data(device, settings, True)
        file = check_answer("\nSelect file to configure (press 'enter' to exit): ", in_list=all_files.keys(),
                            option_list=[''])
        if not file:
            return device
        else:
            if file in f_working.keys():
                a = check_binary_answer("File '{}' will be locked, are you sure? (y/N): ".format(file))
                if a == 'y':
                    conf.lock_file(settings, device, file)
            else:
                a = check_binary_answer("File '{}' will be unlocked, are you sure? (y/N): ".format(file))
                if a == 'y':
                    conf.unlock_file(settings, device, file)


def parsers_lock(device=None, settings=Settings()):
    print('\n\t\t--Output Interface--')
    dev = conf.get_devices(settings)
    if not dev:
        raise SystemError("(!) No device installed found: Run 'edwar.configure.devices()' to configure it.")
    if device is not None:
        if device not in dev.keys():
            raise ValueError("(!) Something went wrong: Device '{}' not found.".format(device))
        else:
            pass
    else:
        print_devices(settings)
        device = check_answer("\nSelect device (press 'enter' to exit): ", in_list=dev.keys(), option_list=[''])
        if not device:
            return

    while 1:
        all_parsers, p_working, p_locked = print_data(device, settings, False)
        parser = check_answer("\nSelect parser to configure (press 'enter' to exit): ", in_list=all_parsers.keys(),
                              option_list=[''])
        if not parser:
            return device
        else:
            if parser in p_working.keys():
                a = check_binary_answer("Parser '{}' will be locked, are you sure? (y/N): ".format(parser))
                if a == 'y':
                    conf.lock_parser(settings, device, parser)
            else:
                a = check_binary_answer("Parser '{}' will be unlocked, are you sure? (y/N): ".format(parser))
                if a == 'y':
                    conf.unlock_parser(settings, device, parser)


def connection_database(password=None, settings=Settings()):
    print('\n\t\t--Database Server Connection--')
    # Config data
    config_file = os.path.join(settings.path, settings.databaseini)
    if not os.path.exists(config_file):
        raise FileNotFoundError("(!) Something went wrong: Configuration file '{}' not found.".format(config_file))

    structure_file = os.path.join(settings.path, settings.structureini)
    if not os.path.exists(structure_file):
        raise FileNotFoundError("(!) Something went wrong: Configuration file '{}' not found.".format(structure_file))

    if password is None:
        password = check_answer("Password of your database user: ", password=True)
    session = conf.open_session(settings, password)
    h, p, u, pwd = print_connection_parameters(session)
    db_name, tb_name = None, None
    ans = check_binary_answer('\nDo you want to edit them? (y/N): ')
    if ans == 'y':
        h, p, u, pwd = ask_connection_parameters()
    host, port, user, password, database, table = conf.edit_connection_parameters(session, h, p, u, pwd, db_name,
                                                                                  tb_name)
    if host and port and user and password:
        ans = check_binary_answer('\nTest connection to database needed for database configuration.\n' +
                                  'Do you want to do it with the current parameters? (y/N): ')
    else:
        ans = 'n'
    if ans == 'y':
        finished = False
        while not finished:
            try:
                print("\n...Executing Connection Test...")
                # Connection test
                db.connect(host, port, user, password)
            except ConnectionRefusedError:
                print("\n\t(!) Something is wrong with your user name or password.\n")
                ans = check_binary_answer("Do you want to reedit them? (y/N): ")
                if ans == 'y':
                    u = check_answer("User name (press 'enter' to keep current name): ")
                    pwd = check_answer("Password (press 'enter' to keep current password): ", password=True)
                    host, port, user, password, database, table = conf.edit_connection_parameters(session, h, p, u, pwd,
                                                                                                  db_name, tb_name)
                else:
                    finished = True
            except ConnectionError:
                print("\n\t(!) Connection went wrong.\n")
                ans = check_binary_answer("Do you want to reedit connection parameters? (y/N): ")
                if ans == 'y':
                    h, p, u, pwd = ask_connection_parameters()
                    host, port, user, password, database, table = conf.edit_connection_parameters(session, h, p, u, pwd,
                                                                                                  db_name, tb_name)
                else:
                    finished = True
            else:
                print("\nConnection test passed!")
                finished = True
                print('\n\t--Database Configuration--')
                db_name, tb_name = print_database_parameters(session)
                ans1 = check_binary_answer('\nDo you want to edit them? (y/N): ')
                if ans1 == 'y':
                    conn, cursor = db.connect(host, port, user, password)
                    db_selected = select_database(cursor, db_name)
                    tb_selected = None
                    if db_selected:
                        tb_selected = select_table(settings, cursor, tb_name)

                    conf.edit_connection_parameters(session, host=host, port=port, user=user, password=pwd,
                                                    database=db_selected if db_selected else db_name,
                                                    table=tb_selected if tb_selected else tb_name)

                    db.disconnect(cursor, conn)
    conf.close_session(session)


def ask_connection_parameters():
    h = check_answer("Host address (press 'enter' to keep current address): ")
    p = check_answer("Port number (press 'enter' to keep current number): ")
    u = check_answer("User name (press 'enter' to keep current name): ")
    pwd = check_answer("Password (press 'enter' to keep current password): ", password=True)
    return h, p, u, pwd


def print_connection_parameters(session):
    host, port, user, password, database, table = conf.get_connection_parameters(session)
    maxlenobj = 10
    maxlencontent = max(len(host), len(port), len(password), len(user), 14) + 2
    table_format = '| {:^' + str(maxlenobj) + '}| {:^' + str(maxlencontent) + '}|'
    sep = '+' + '-' * (maxlenobj + 1) + '+' + '-' * (maxlencontent + 1) + '+'
    print("\nCurrent database connection parameters:\n")
    print(sep)
    print(table_format.format('OPTION', 'VALUE'))
    print(sep)
    print(table_format.format('HOST', host if host else 'Not Configured'))
    print(table_format.format('PORT', port if port else 'Not Configured'))
    print(table_format.format('USER', user if user else 'Not Configured'))
    print(table_format.format('PASSWORD', 'Configured' if password else 'Not Configured'))
    print(sep)

    return host, port, user, password


def print_database_parameters(session):
    host, port, user, password, database, table = conf.get_connection_parameters(session)
    maxlenobj = 10
    maxlencontent = max(len(database), len(table), 14) + 2
    table_format = '| {:^' + str(maxlenobj) + '}| {:^' + str(maxlencontent) + '}|'
    sep = '+' + '-' * (maxlenobj + 1) + '+' + '-' * (maxlencontent + 1) + '+'
    print("\nCurrent database configuration:\n")
    print(sep)
    print(table_format.format('OPTION', 'VALUE'))
    print(sep)
    print(table_format.format('DATABASE', database if database else 'Not Configured'))
    print(table_format.format('TABLE', table if table else 'Not Configured'))
    print(sep)

    return database, table


def select_database(cursor, db_name=None):
    db_selected = None
    while not db_selected:
        if db_name:
            msg = "Database name (press 'enter' to keep current name '{}'): ".format(db_name)
            substitute_dict = {'': db_name}
            option_list = []
        else:
            msg = "Database name (press 'enter' to exit): "
            substitute_dict = {}
            option_list = ['']
        db_name = check_answer(msg, substitute_dict=substitute_dict, option_list=option_list)

        if db_name:
            try:
                cursor.execute("USE {}".format(db_name))
            except sql.errors.Error as err2:
                print("\n\t(!) Something went wrong while selecting database '{}': {}.\n".format(db_name, err2))
                a = check_binary_answer('Do you want to create it? (y/N): ')
                if a == 'y':
                    try:
                        cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(db_name))
                    except sql.errors.Error as err:
                        if err.errno == sql.errorcode.ER_DBACCESS_DENIED_ERROR:
                            print("\n\t(!) Permission denied to create database.\n")
                        else:
                            print("\n\t(!) Something went wrong while creating database '{}': {}.\n".format(db_name,
                                                                                                            err))
                        db_name = None
                    except Exception as err1:
                        print("\n\t(!) Something went wrong while selecting database: {}.\n".format(err1))
                        db_name = None
                    else:
                        db_selected = db_name
                        print("Database '{}' successfully created to upload data.".format(db_name))
                else:
                    db_name = None
            else:
                print("Database '{}' successfully selected to upload data.".format(db_name))
                db_selected = db_name
        else:
            return None
    return db_selected


def create_table(settings, cursor, tb=None):
    default_features = ('EDA', 'ACCx', 'ACCy', 'ACCz', 'IBI', 'TEMP')
    tb_name = check_answer("Name of the new table (press 'enter' to keep current name '{}'): ".format(tb),
                           substitute_dict={'': tb})

    print('Default features are {}'.format(default_features))
    if_new_features = check_binary_answer("Do you want to use other features? (if yes, features declared for a given "
                                          + "configuration's device will be used) (y/N): ")
    if if_new_features == 'y':
        devs = print_devices(settings)
        if not devs:
            ans = check_binary_answer("Only default features {} can be used. ".format(default_features) +
                                      "Do you want to create table '{}' anyway? (y/N): ".format(tb_name))
            if ans == 'y':
                features = default_features
            else:
                return None
        else:
            device = check_answer("From which device configuration do you want to extract the features? (press "
                                  "'enter' to exit): ", in_list=devs.keys(), option_list=[''])
            if not device:
                return None
            out_modules, wo, lo = conf.get_output_features(settings, device)
            features = tuple()
            for feature in out_modules.values():
                features += tuple(feature.replace(' ', '').split(','))
    else:
        features = default_features

    try:
        cursor.execute('''CREATE TABLE {} (
                       `data_type` enum{} CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
                       `ts` datetime(6) NOT NULL,
                       `value` float NOT NULL,
                       PRIMARY KEY (`data_type`, `ts`)) 
                       ENGINE=InnoDB DEFAULT CHARSET=latin1;'''.format(tb_name, features))
        print("Table '{}' created.".format(tb_name))
    except sql.errors.Error as err:
        print("\n\t(!) Something went wrong while creating table '{}': {}.\n".format(tb_name, err))
        return None
    return tb_name


def select_table(settings, cursor, tb_name=None):
    tb_selected = None
    header_needed = ('data_type', 'ts', 'value')
    while not tb_selected:
        print('\nTable header should contain a header with {}. If not, a custom function is '.format(header_needed) +
              'required to adapt data to the given database table.')
        if tb_name:
            msg = "Table name (press 'enter' to keep current name '{}'): ".format(tb_name)
            substitute_dict = {'': tb_name}
            option_list = []
        else:
            msg = "Table name (press 'enter' to exit): "
            substitute_dict = {}
            option_list = ['']
        tb_name = check_answer(msg, substitute_dict=substitute_dict, option_list=option_list)
        if tb_name:
            try:
                cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_name=%s;", (tb_name,))
                if cursor.fetchone() is None:
                    print("\n\t(!) Something went wrong while trying to select table '{}': ".format(tb_name) +
                          "Table not found\n")
                    a = check_binary_answer('Do you want to create a new one? (y/N): ')
                    if a == 'y':
                        tb_selected = create_table(settings, cursor, tb_name)
                else:
                    tb_selected = tb_name
            except sql.errors.Error as err:
                print("\n\t(!) Something went wrong while trying to select table '{}': {}\n".format(tb_name, err))
                a = check_binary_answer('Do you want to create a new one? (y/N): ')
                if a == 'y':
                    tb_selected = create_table(settings, cursor, tb_name)
            tb_name = None
        else:
            return None
    print("Table '{}' successfully selected to upload data.".format(tb_selected))
    return tb_selected
