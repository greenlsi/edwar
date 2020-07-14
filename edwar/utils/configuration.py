from .rw_ini import Structure, DataBase


def edit_device(settings, device: str, new_device: str = None, new_loader: str = None):
    s = Structure(settings)
    dev = s.devices()
    try:
        loader = dev[device]
    except KeyError:
        loader = None
    try:
        variables = s.variables(device)
        features = s.features(device)
    except Exception:
        variables = dict()
        features = dict()
    s.remove_device(device)
    s.set_device(new_device if new_device else device, new_loader if new_loader else loader)
    s.set_variables(new_device if new_device else device, variables)
    s.set_features(new_device if new_device else device, features)
    s.update_file()


def get_devices(settings):
    s = Structure(settings)
    dev = s.devices()
    return dev


def remove_device(settings, device: str):
    s = Structure(settings)
    s.remove_device(device)
    s.update_file()


def edit_input(settings, device: str, file: str, new_file: str = None, new_variables: list = None):
    s = Structure(settings)
    variables = s.variables(device)
    new_variables1 = str()
    if new_variables:
        for nv in new_variables:
            new_variables1 += nv + ','
        new_variables1 = new_variables1[:-1]
    if file:
        s.remove_file(device, file)
    s.set_variable(device, new_file if new_file else file, new_variables1 if new_variables else variables[file])
    s.update_file()


def get_input_variables(settings, device):
    s = Structure(settings)
    variables = s.variables(device)
    locked = dict()
    working = dict()
    for v in variables.keys():
        if v[0] == '.':
            locked.update({v[1:]: variables[v]})
        else:
            working.update({v: variables[v]})
    variables1 = working.copy()
    variables1.update(locked)
    return variables1, working, locked


def remove_input_file(settings, device, file):
    s = Structure(settings)
    s.remove_file(device, file)
    s.update_file()


def remove_all_files(settings, device):
    s = Structure(settings)
    s.remove_all_files(device)
    s.update_file()


def lock_file(settings, device, parser):
    s = Structure(settings)
    s.lock_file(device, parser)
    s.update_file()


def lock_all_files(settings, device):
    fi, wo, lo = get_input_variables(settings, device)
    for f in wo.keys():
        lock_file(settings, device, f)


def unlock_file(settings, device, file):
    s = Structure(settings)
    s.unlock_file(device, file)
    s.update_file()


def unlock_all_files(settings, device):
    fi, wo, lo = get_input_variables(settings, device)
    for f in lo.keys():
        unlock_file(settings, device, f)


def get_output_features(settings, device):
    s = Structure(settings)
    features = s.features(device)
    locked = dict()
    working = dict()
    if not features:
        s.set_features(device, dict())
    else:
        for f in features.keys():
            if f[0] == '.':
                locked.update({f[1:]: features[f]})
            else:
                working.update({f: features[f]})
    features1 = working.copy()
    features1.update(locked)
    return features1, working, locked


def edit_output(settings, device: str, parser: str, new_parser: str = None, new_features: list = None):
    s = Structure(settings)
    features = s.features(device)
    s.remove_parser(device, parser)
    new_features1 = str()
    if new_features:
        for nv in new_features:
            new_features1 += nv + ','
        new_features1 = new_features1[:-1]
    s.set_feature(device, new_parser if new_parser else parser, new_features1 if new_features else features[parser])
    s.update_file()


def remove_parser(settings, device, parser):
    s = Structure(settings)
    s.remove_parser(device, parser)
    s.update_file()


def remove_all_parsers(settings, device):
    s = Structure(settings)
    s.remove_all_parsers(device)
    s.update_file()


def lock_parser(settings, device, parser):
    s = Structure(settings)
    s.lock_module(device, parser)
    s.update_file()


def lock_all_parsers(settings, device):
    pa, wo, lo = get_output_features(settings, device)
    for p in wo.keys():
        lock_parser(settings, device, p)


def unlock_parser(settings, device, parser):
    s = Structure(settings)
    s.unlock_module(device, parser)
    s.update_file()


def unlock_all_parsers(settings, device):
    pa, wo, lo = get_output_features(settings, device)
    for p in lo.keys():
        unlock_parser(settings, device, p)


def edit_connection_parameters(session, host=None, port=None, user=None, password=None, database=None,
                               table=None):
    h, p, u, pwd, db, tb = get_connection_parameters(session)
    h = host if host else h
    p = port if port else p
    u = user if user else u
    pwd = password if password else pwd
    db = database if database else db
    tb = table if table else tb
    session.set_host(h, p)
    session.set_user(u, pwd)
    session.set_database(db)
    session.set_table(tb)
    return h, p, u, pwd, db, tb


def get_connection_parameters(session):
    h, p = session.host()
    u, pwd = session.user()
    db = session.database()
    tb = session.table()
    return h, p, u, pwd, db, tb


def open_session(settings, pw=''):
    d = DataBase(settings, pw)
    return d


def close_session(session):
    session.update_file()


def check_password(settings, pw):
    close_session(open_session(settings, pw))
