from .utils.rw_ini import Structure


def configure_input(device, configfile='configuration/structure.ini'):
    finished = False
    variables = print_data(device, configfile=configfile)
    while not finished:
        file = input('\nSelect file to configure (press enter to exit): ')
        if not file:
            finished = True
        else:
            if file in variables.keys():
                newfile = input("New name of file '%s' (press enter to keep name, or space to remove it, or write "
                                "exit to go back): " % file)
                while newfile in variables.keys():
                    print("\n\t(!) Something went wrong: File %s already exists\n" % newfile)
                    msg = "New name of file '%s' (press enter to keep name, space to remove it or write exit to " \
                          "go back): " % file
                    newfile = input(msg)
                variables_in_file = variables[file].replace(' ', '').split(',')
                new_variables = list()
            else:
                if file[0] == ' ':
                    print("\n\t(!) Something went wrong: Invalid input %s\n" % file)
                    newfile = 'exit'
                else:
                    create = input("File '%s' not found, do you want to create it? (y/n): " % file)
                    if create == 'y':
                        newfile = None
                    else:
                        newfile = 'exit'
                variables_in_file = list()
                new_variables = list()
            if newfile == ' ':
                todelete = input("File '%s' will be deleted. Are you sure? (y/n): " % file)
                if todelete == 'y':
                    remove_input_file(device, file, configfile=configfile)
                newfile = 'exit'

            if newfile != 'exit':
                for v in variables_in_file:
                    var = None
                    while var is None:
                        var = input(
                            "New name of variable '%s' (press enter to keep name, or space to remove it): " % v)
                        if not var:
                            var = v
                        if var in new_variables:
                            print("\n\t(!) Something went wrong: Variable '%s' already exists\n" % var)
                            var = None
                    if var != ' ':
                        new_variables.append(var)
                nvar = 'sthg'
                while nvar:
                    nvar = input('Name of new variable (press enter to exit): ')
                    if nvar:
                        new_variables.append(nvar)
                edit_input(device, file, configfile=configfile, new_file=newfile, new_variables=new_variables)

            variables = print_data(device, configfile=configfile)


def print_data(device, configfile='configuration/structure.ini', input_device=True):
    if input_device:
        data = get_input_variables(device, configfile)
        if data:
            print("Current configuration of the input for device '%s':" % device)
            print('\n{:<50} {:<3} {:<50}'.format('[FILE]', ' ', '[VARIABLES IN FILE]'))
            for v in data.keys():
                print('{:<50} {:<3} {:<50}'.format(v, '-->', data[v]))
        else:
            print("\n\t(!) No configuration of variables of device '%s' found\n" % device)

    else:
        data = get_output_features(device, configfile)
        if data:
            print("Current configuration of the output for device '%s':" % device)
            print('\n{:<50} {:<3} {:<50}'.format('[PARSER]', ' ', '[FEATURES IN PARSER]'))
            for v in data.keys():
                print('{:<50} {:<3} {:<50}'.format(v, '-->', data[v]))
        else:
            print("\n\t(!) No configuration of features of device '%s' found\n" % device)
    return data


def get_input_variables(device, configfile='configuration/structure.ini'):
    s = Structure(configfile)
    variables = s.variables(device)
    if variables is None:
        s.set_variables(device, None)
    return variables


def edit_input(device, file, configfile='configuration/structure.ini', new_file=None, new_variables=None):
    s = Structure(configfile)
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
    s.set_variable(device, new_file if new_file else file, new_variables1 if new_variables else variables[file])
    s.update_file()


def remove_input_file(device, file, configfile='configuration/structure.ini'):
    s = Structure(configfile)
    s.remove_file(device, file)
    s.update_file()

def remove_all_files(device, configfile='configuration/structure.ini'):
        s = Structure(configfile)
        s.remove_all_files(device)
        s.update_file()

def configure_output(device, configfile='configuration/structure.ini'):
    finished = False
    features = print_data(device, configfile=configfile, input_device=False)
    while not finished:
        parser = input('\nSelect parser to configure (press enter to exit): ')
        if not parser:
            finished = True
        else:
            if parser in features.keys():
                newparser = input("New name of parser '%s' (press enter to keep name, or space to remove it, or write "
                                  "exit to go back): " % parser)
                while newparser in features.keys():
                    print("\n\t(!) Something went wrong: Parser %s already exists\n" % newparser)
                    msg = "New name of parser '%s' (press enter to keep name, space to remove it or write exit to " \
                          "go back): " % parser
                    newparser = input(msg)
                features_in_parser = features[parser].replace(' ', '').split(',')
                new_features = list()
            else:
                if parser[0] == ' ':
                    print("\n\t(!) Something went wrong: Invalid input %s\n" % parser)
                    newparser = 'exit'
                else:
                    create = input("Parser '%s' not found, do you want to create it? (y/n): " % parser)
                    if create == 'y':
                        newparser = None
                    else:
                        newparser = 'exit'
                features_in_parser = list()
                new_features = list()
            if newparser == ' ':
                todelete = input("Parser '%s' will be deleted. Are you sure? (y/n): " % parser)
                if todelete == 'y':
                    remove_parser(device, parser, configfile=configfile)
                newparser = 'exit'

            if newparser != 'exit':
                for v in features_in_parser:
                    ftr = None
                    while ftr is None:
                        ftr = input(
                            "New name of feature '%s' (press enter to keep name, or space to remove it): " % v)
                        if not ftr:
                            ftr = v
                        if ftr in new_features:
                            print("\n\t(!) Something went wrong: Feature '%s' already exists\n" % ftr)
                            ftr = None
                    if ftr != ' ':
                        new_features.append(ftr)
                nftr = 'sthg'
                while nftr:
                    nftr = input('Name of new feature (press enter to exit): ')
                    if nftr:
                        new_features.append(nftr)
                edit_output(device, parser, configfile=configfile, new_parser=newparser, new_features=new_features)

            features = print_data(device, configfile=configfile)


def edit_output(device, parser, configfile='configuration/structure.ini', new_parser=None, new_features=None):
    s = Structure(configfile)
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
    s.set_variable(device, new_parser if new_parser else parser, new_features1 if new_features else features[parser])
    s.update_file()


def get_output_features(device, configfile='configuration/structure.ini'):
    s = Structure(configfile)
    features = s.features(device)
    return features


def remove_parser(device, parser, configfile='configuration/structure.ini'):
    s = Structure(configfile)
    s.remove_parser(device, parser)
    s.update_file()


def remove_all_parsers(device, configfile='configuration/structure.ini'):
    s = Structure(configfile)
    s.remove_all_parsers(device)
    s.update_file()
