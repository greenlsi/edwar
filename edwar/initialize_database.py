import os
import mysql.connector as sql

from .utils.rw_ini import DataBase, Structure


__all__ = {
    'connect',
    'test_connect',
    'select_database',
    'select_table'
}


def test_connect(host, port, user, pwd):
    try:
        conn = sql.connect(
            host=host,
            user=user,
            passwd=pwd,
            port=port,
        )
        if conn.is_connected():
            cursor = conn.cursor()
        else:
            raise ConnectionError("(!) Connection went wrong: cursor could not be created")
    except sql.errors.Error as err:
        if err.errno == sql.errorcode.ER_ACCESS_DENIED_ERROR:
            raise ConnectionRefusedError("(!) Something is wrong with your user name or password")
        else:
            raise ConnectionError("(!) Connection went wrong: {}".format(err))
    else:
        return conn, cursor


def connect():
    """
    Function that tries to obtain a connexion object to data base

    """
    # Config data
    config_file = "db.ini"
    if not os.path.exists(config_file):
        raise FileNotFoundError("(!) Something went wrong: Configuration file {} not found".format(config_file))

    structure_file = "structure.ini"
    if not os.path.exists(structure_file):
        raise FileNotFoundError("(!) Something went wrong: Configuration file {} not found".format(structure_file))

    d = DataBase()

    user, pwd = d.user()
    if (user or pwd) is None:
        raise ValueError("(!) Something went wrong: Missing user identification")
    host, port = d.host()
    if (host or port) is None:
        raise ValueError("(!) Something went wrong: Missing connection parameters")
    db_name, tb_name = d.database(), d.table()

    # Connection test
    conn, cursor = test_connect(host, port, user, pwd)

    print('\n\t--Database Selection--')
    cont = 0
    db_name = select_database(cursor, db_name)
    while not db_name:
        cont += 1
        if cont >= 3:
            disconnect(cursor, conn)
            raise Exception("\n\t(!) Something went wrong: exceeded maximum number of attempts to select a database\n")
        db_name = select_database(cursor, db_name)
    print("Database %s selected to upload data" % db_name)

    print('\n\t--Table Selection--')
    cont = 0
    tb_name, default_function = select_table(cursor, tb_name)
    while not tb_name:
        cont += 1
        if cont >= 3:
            disconnect(cursor, conn)
            raise Exception("\n\t(!) Something went wrong: exceeded maximum number of attempts to select a table\n")
        tb_name = select_table(cursor, tb_name)
    print("Table {} selected to upload data".format(tb_name))

    d.set_user(user, pwd)
    d.set_host(host, port)
    d.set_database(db_name)
    d.set_table(tb_name)
    d.update_file()

    disconnect(cursor, conn)
    return host, port, user, pwd, db_name, tb_name


def disconnect(cursor, conn):
    """
    Function to _disconnect  data base

    Parameters
    ----------
    cursor : cursor object
    conn: connector object

    """
    try:
        if conn.is_connected():
            cursor.close()
            conn.close()
        return 0
    except sql.Error as err:
        print('Connection could not be closed: {}'.format(err))
    return 1


def select_database(cursor, db_name=None):
    if not db_name:
        a = input('Do you want to use a new database? (y/n): ')
        try:
            if a == 'y':
                db_name = input('Name of the new database: ')
                cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(db_name))
            else:
                db_name = input('Select database: ')
        except sql.errors.Error as err:
            if err.errno == sql.errorcode.ER_DBACCESS_DENIED_ERROR:
                print("\n\t(!) Permission denied to create database\n")
            else:
                print("\n\t(!) Something went wrong while creating database {}: {}\n".format(db_name, err))
            db_name = None
        except Exception as err:
            print("\n\t(!) Something went wrong in select_database(): {}\n".format(err))
            db_name = None

    try:
        cursor.execute("USE {}".format(db_name))
    except sql.errors.Error as err:
        print("\n\t(!) Something went wrong while selecting database '{}': {}\n".format(db_name, err))
        db_name = None
    return db_name


def create_table(cursor):
    default_features = ('EDA', 'ACCx', 'ACCy', 'ACCz', 'IBI', 'TEMP')
    tb_name = input('Name of the new table: ')

    print('Default features are {}'.format(default_features))
    if_new_features = input('Do you want to use other features? (if yes, features declared for a given device' +
                            'in configuration file will be used) (y/n): ')
    if if_new_features == 'y':
        s = Structure()
        print('\nDevices: ')
        for d in s.devices().keys():
            print('\t-%s' % d)
        device = input("For which device do you want to create table '%s'?: " % tb_name)
        while device not in s.devices().keys():
            print("\n\t(!) Something went wrong while selecting device '{}': device not found\n".format(device))
            device = input("For which device do you want to create table '%s'?: " % tb_name)
        out_modules = s.features(device)
        features = ()
        for module in out_modules:
            features += tuple(module[1].replace(' ', '').split(','))

    else:
        features = default_features

    try:
        cursor.execute('''CREATE TABLE {} (
                       `data_type` enum{} CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
                       `ts` datetime NOT NULL,
                       `value` float NOT NULL,
                       PRIMARY KEY (`data_type`, `ts`)) 
                       ENGINE=InnoDB DEFAULT CHARSET=latin1;'''.format(tb_name, features))
        print("table {} created".format(tb_name))
    except sql.errors.Error as err:
        print("\n\t(!) Something went wrong while creating table {}: {}\n".format(tb_name, err))
        return None
    return tb_name


def select_table(cursor, tb=None):
    header_needed = ('data_type', 'ts', 'value')
    if not tb:
        a = input('Table header must contain {}\nDo you want to create a new table? (y/n): '.format(header_needed))
        if a == 'y':
            tb = create_table(cursor)
            default = True
        else:
            tb = input('Select table: ')
            default = False
    else:
        default = False

    try:
        cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_name=%s;", (tb,))
        if cursor.fetchone() is None:
            print("\n\t(!) Something went wrong while trying to select table %s: Table not found\n" % tb)
            tb = None
    except sql.errors.Error as err:
        print("\n\t(!) Something went wrong while trying to select table {}: {}\n".format(tb, err))
        tb = None
    return tb, default


function = '''
import pandas as pd


def _ts_transform(timestamp):
    date_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return date_time


def adapt_features(data):
    list_table_columns = ['data_type', 'ts', 'value']
    ncols = len(data.columns)
    nrows = len(data)
    list_update = pd.DataFrame(index=range(0, ncols * nrows), columns=list_table_columns)
    n = 0
    for column in data.columns:
        for index in range(0, nrows):
            list_update.loc[n * nrows + index, list_table_columns] = [column, _ts_transform(data[column].index[index]),
                                                                      float(data[column].values[index])]
        n += 1
    return list_update
'''
personalized_function = '''
def adapt_features(data):
    "your code goes here"  # TODO
'''


if __name__ == '__main__':
    print('\nWelcome to data base configurator')
    connect()
