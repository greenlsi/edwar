from .utils.rw_ini import Structure
from .utils.rw_ini import DataBase
from .initialize_database import test_connect, connect


def devices():
    finished = False
    while not finished:
        print('\n\t--Device Configuration--')
        dev = print_devices()
        device = input("\nName of device (press 'enter' to exit): ")
        if not device:
            finished = True
        else:
            if device in dev.keys():
                msg = "New name of device '%s' (press 'enter' to keep name, 'space' to remove it or type 'back' to " \
                      "go back): " % device
                newdevice = input(msg)
                while newdevice in dev.keys():
                    print("\n\t(!) Something went wrong: Device %s already exists\n" % newdevice)
                    newdevice = input(msg)
                load_function = dev[device]
            else:
                if device[0] == ' ':
                    print("\n\t(!) Something went wrong: Invalid input '%s'\n" % device)
                    newdevice = 'back'
                else:
                    if not dev:
                        create = 'y'
                    else:
                        create = input("Device '%s' not found, do you want to create it? (y/n): " % device)
                    if create == 'y':
                        newdevice = None
                    else:
                        newdevice = 'back'
                load_function = None
            if newdevice == ' ':
                todelete = input("Device '%s' will be deleted. Are you sure? (y/n): " % device)
                if todelete == 'y':
                    remove_device(device)
                newdevice = 'back'

            if newdevice != 'back':
                if load_function:
                    msg = "New function loader (press 'enter' to keep the current function %s): " % load_function
                    new_load_function = input(msg)
                    if new_load_function and (new_load_function[0] == ' ' or new_load_function[0] == '.'):
                        print("\n\t(!) Something went wrong: Invalid input '%s'\n" % new_load_function)
                        new_load_function = None
                else:
                    msg = "New function loader (press 'enter' to exit): "
                    new_load_function = input(msg)
                    if new_load_function and (new_load_function[0] == ' ' or new_load_function[0] == '.'):
                        print("\n\t(!) Something went wrong: Invalid input '%s'\n" % new_load_function)
                        new_load_function = None

                edit_device(device, new_device=newdevice, new_loader=new_load_function)
                input_files(newdevice if newdevice else device)
                parsers(newdevice if newdevice else device)


def edit_device(device, new_device=None, new_loader=None):
    s = Structure()
    dev = s.devices()
    try:
        loader = dev[device]
    except KeyError:
        loader = None
    if new_device and not isinstance(new_device, str):
        raise TypeError("Parameter 'new_device' expected to be type 'string'")
    if new_loader and not isinstance(new_loader, str):
        raise TypeError("Parameter 'new_loader' expected to be type 'string'")
    try:
        variables = s.variables(device)
        features = s.features(device)
    except KeyError:
        variables = dict()
        features = dict()
    s.remove_device(device)
    s.set_device(new_device if new_device else device, new_loader if new_loader else loader)
    s.set_variables(new_device if new_device else device, variables)
    s.set_features(new_device if new_device else device, features)
    s.update_file()


def print_devices():
    dev = get_devices()
    if dev:
        print("\nCurrent registered devices:")
        print('\n{:<50} {:<3} {:<50}'.format('[DEVICE]', ' ', '[LOAD FUNCTION]'))
        for v in dev.keys():
            print('{:<50} {:<3} {:<50}'.format(v, '-->', dev[v]))
    else:
        print("\n\t(!) No devices found\n")
    return dev


def get_devices():
    s = Structure()
    dev = s.devices()
    return dev


def remove_device(device):
    s = Structure()
    s.remove_device(device)
    s.update_file()


def input_files(device):
    print('\n\t--Input Configuration--')
    finished = False
    while not finished:
        variables = print_data(device)
        file = input('\nName of file to extract data (press enter to exit): ')
        if not file:
            finished = True
        else:
            if file in variables.keys():
                msg = "New name of file '%s' (press 'enter' to keep name, 'space' to remove it or type 'back' to " \
                      "go back): " % file
                newfile = input(msg)
                while newfile in variables.keys():
                    print("\n\t(!) Something went wrong: File %s already exists\n" % newfile)
                    newfile = input(msg)
                variables_in_file = variables[file].replace(' ', '').split(',')
                new_variables = list()
            else:
                if file[0] == ' ':
                    print("\n\t(!) Something went wrong: Invalid input '%s'\n" % file)
                    newfile = 'back'
                else:
                    if not variables:
                        create = 'y'
                    else:
                        create = input("File '%s' not found, do you want to create it? (y/n): " % file)
                    if create == 'y':
                        newfile = None
                    else:
                        newfile = 'back'
                variables_in_file = list()
                new_variables = list()
            if newfile == ' ':
                todelete = input("File '%s' will be deleted. Are you sure? (y/n): " % file)
                if todelete == 'y':
                    remove_input_file(device, file)
                newfile = 'back'

            if newfile != 'back':
                for v in variables_in_file:
                    var = None
                    while not var:
                        var = input(
                            "New name of variable '%s' (press 'enter' to keep name, or 'space' to remove it): " % v)
                        if not var:
                            var = v
                        if var in new_variables:
                            print("\n\t(!) Something went wrong: Variable '%s' already exists\n" % var)
                            var = None
                    if var[0] != ' ' and var[0] != '.':
                        new_variables.append(var)
                    else:
                        print("\n\t(!) Something went wrong: Invalid input '%s'\n" % var)
                nvar = 'sthg'
                cont = 0
                while nvar:
                    cont += 1
                    nvar = input("Name of new variable %i ('press' enter to exit): " % cont)
                    if nvar:
                        new_variables.append(nvar)
                edit_input(device, file, new_file=newfile, new_variables=new_variables)


def print_data(device, input_device=True):
    if input_device:
        data = get_input_variables(device)
        if data:
            print("\nCurrent configuration of the input for device '%s':" % device)
            print('\n{:<50} {:<3} {:<50}'.format('[FILE]', ' ', '[VARIABLES IN FILE]'))
            for v in data.keys():
                print('{:<50} {:<3} {:<50}'.format(v, '-->', data[v]))
        else:
            print("\n\t(!) No configuration of variables of device '%s' found\n" % device)

    else:
        data = get_output_features(device)
        if data:
            print("\nCurrent configuration of the output for device '%s':" % device)
            print('\n{:<50} {:<3} {:<50}'.format('[PARSER]', ' ', '[FEATURES IN PARSER]'))
            for v in data.keys():
                print('{:<50} {:<3} {:<50}'.format(v, '-->', data[v]))
        else:
            print("\n\t(!) No configuration of features of device '%s' found\n" % device)
    return data


def get_input_variables(device):
    s = Structure()
    variables = s.variables(device)
    if variables is None:
        s.set_variables(device, None)
    return variables


def edit_input(device, file, new_file=None, new_variables=None):
    s = Structure()
    variables = s.variables(device)
    new_variables1 = str()
    if new_file is not None and not isinstance(new_file, str):
        raise TypeError("Parameter 'new_file' expected to be type 'string'")
    if new_variables:
        if isinstance(new_variables, list) and all(isinstance(nv, str) for nv in new_variables):
            for nv in new_variables:
                new_variables1 += nv + ','
            new_variables1 = new_variables1[:-1]
        else:
            raise TypeError("Parameter 'new_variables' expected to be type 'list of strings'")
    s.remove_file(device, file)
    s.set_variable(device, new_file if new_file else file, new_variables1 if new_variables else variables[file])
    s.update_file()


def remove_input_file(device, file):
    s = Structure()
    s.remove_file(device, file)
    s.update_file()


def remove_all_files(device):
    s = Structure()
    s.remove_all_files(device)
    s.update_file()


def parsers(device):
    finished = False
    print('\n\t--Output Configuration--')
    while not finished:
        features = print_data(device, input_device=False)
        parser = input("\nName of parser to process data (press 'enter' to exit): ")
        if not parser:
            finished = True
        else:
            if parser in features.keys():
                msg = "New name of parser '%s' (press 'enter' to keep name, 'space' to remove it or type 'back'" \
                      "to go back): " % parser
                newparser = input(msg)
                while newparser in features.keys():
                    print("\n\t(!) Something went wrong: Parser %s already exists\n" % newparser)
                    newparser = input(msg)
                features_in_parser = features[parser].replace(' ', '').split(',')
                new_features = list()
            else:
                if parser[0] == ' ':
                    print("\n\t(!) Something went wrong: Invalid input %s\n" % parser)
                    newparser = 'back'
                else:
                    if not features:
                        create = 'y'
                    else:
                        create = input("Parser '%s' not found, do you want to create it? (y/n): " % parser)
                    if create == 'y':
                        newparser = None
                    else:
                        newparser = 'back'
                features_in_parser = list()
                new_features = list()
            if newparser == ' ':
                todelete = input("Parser '%s' will be deleted. Are you sure? (y/n): " % parser)
                if todelete == 'y':
                    remove_parser(device, parser)
                newparser = 'back'

            if newparser != 'back':
                for v in features_in_parser:
                    ftr = None
                    while ftr is None:
                        ftr = input(
                            "New name of feature '%s' (press 'enter' to keep name, or 'space' to remove it): " % v)
                        if not ftr:
                            ftr = v
                        if ftr in new_features:
                            print("\n\t(!) Something went wrong: Feature '%s' already exists\n" % ftr)
                            ftr = None
                    if ftr[0] != ' ' or ftr[0] != '.':
                        new_features.append(ftr)
                    else:
                        print("\n\t(!) Something went wrong: Invalid input '%s'\n" % ftr)
                nftr = 'sthg'
                cont = 0
                while nftr:
                    cont += 1
                    nftr = input("Name of new feature %i (press 'enter' to exit): " % cont)
                    if nftr:
                        new_features.append(nftr)
                edit_output(device, parser, new_parser=newparser, new_features=new_features)


def edit_output(device, parser, new_parser=None, new_features=None):
    s = Structure()
    features = s.features(device)
    s.remove_parser(device, parser)
    new_features1 = str()
    if new_parser is not None and not isinstance(new_parser, str):
        raise TypeError("Parameter 'new_file' expected to be type 'string'")
    if new_features:
        if isinstance(new_features, list) and all(isinstance(nv, str) for nv in new_features):
            for nv in new_features:
                new_features1 += nv + ','
            new_features1 = new_features1[:-1]
        else:
            raise TypeError("Parameter 'new_variables' expected to be type 'list of strings'")
    s.set_feature(device, new_parser if new_parser else parser, new_features1 if new_features else features[parser])
    s.update_file()


def get_output_features(device):
    s = Structure()
    features = s.features(device)
    return features


def remove_parser(device, parser):
    s = Structure()
    s.remove_parser(device, parser)
    s.update_file()


def remove_all_parsers(device):
    s = Structure()
    s.remove_all_parsers(device)
    s.update_file()


def connection():
    print('\n\t--Database Configuration--')
    print_connection_parameters()
    h, p, u, pwd, db, tb = None, None, None, None, None, None
    ans = input('\nDo you want to edit them? (y/n): ')
    if ans == 'y':
        h, p, u, pwd, db, tb = __ask_connection_parameters()
    host, port, user, password, database, table = edit_connection(h, p, u, pwd, db, tb)
    ans = input('\nDo you want to test connection with the current parameters? (y/n): ')
    if ans == 'y':
        finished = False
        while not finished:
            try:
                print("\n...Executing Test...")
                conn, cursor = test_connect(host, port, user, password)
            except ConnectionRefusedError:
                print("\n\t(!) Something is wrong with your user name or password\n")
                ans = input("Do you want to edit them again? (y/n): ")
                if ans == 'y':
                    u = input("User name (press 'enter' to keep current name): ")
                    pwd = input("Password (press 'enter' to keep current password): ")
                    host, port, user, password, database, table = edit_connection(h, p, u, pwd, db, tb)
                else:
                    finished = True
            except ConnectionError:
                print("\n\t(!) Connection went wrong\n")
                ans = input("Do you want to edit connection parameters again? (y/n): ")
                if ans == 'y':
                    h, p, u, pwd, db, tb = __ask_connection_parameters()
                    host, port, user, password, database, table = edit_connection(h, p, u, pwd, db, tb)
                else:
                    finished = True
            else:
                print("\nTest passed!")
                finished = True
                connect()


def __ask_connection_parameters():
    h = input("Host address (press 'enter' to keep current address): ")
    p = input("Port number (press 'enter' to keep current number): ")
    u = input("User name (press 'enter' to keep current name): ")
    pwd = input("Password (press 'enter' to keep current password): ")
    db = input("Database name (press 'enter' to keep current name): ")
    tb = input("Table name (press 'enter' to keep current name): ")
    return h, p, u, pwd, db, tb


def edit_connection(host=None, port=None, user=None, password=None, database=None, table=None):
    d = DataBase()
    h, p = d.host()
    h = host if host else h
    p = port if port else p
    d.set_host(h, p)
    u, pwd = d.user()
    u = user if user else u
    pwd = password if password else pwd
    d.set_user(u, pwd)
    db = database if database else d.database()
    d.set_database(db)
    tb = table if table else d.table()
    d.set_table(tb)
    d.update_file()
    return h, p, u, pwd, db, tb


def print_connection_parameters():
    host, port, user, password, database, table = edit_connection()
    print("\nCurrent configuration of the connection to database")
    print('\n{:<50} {:<3} {:<50}'.format('[OPTION]', ' ', '[VALUE]'))
    print('{:<50} {:<3} {:<50}'.format('HOST', '-->', host if host else 'Not Configured'))
    print('{:<50} {:<3} {:<50}'.format('PORT', '-->', port if port else 'Not Configured'))
    print('{:<50} {:<3} {:<50}'.format('USER', '-->', user if user else 'Not Configured'))
    print('{:<50} {:<3} {:<50}'.format('PASSWORD', '-->', password if password else 'Not Configured'))
    print('{:<50} {:<3} {:<50}'.format('DATABASE', '-->', database if database else 'Not Configured'))
    print('{:<50} {:<3} {:<50}'.format('TABLE', '-->', table if table else 'Not Configured'))
    return host, port, user, password, database, table
