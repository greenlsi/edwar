import configparser
import os
import mysql.connector as sql


def connect():
    """
    Function that tries to obtain a connexion object to data base

    """
    # Config data
    cursor = None
    configFile = "db.ini"
    if not os.path.exists(configFile):
        raise Exception("\n\t(!) Something went wrong: Configuration file {} not found".format(configFile))

    structureFile = "structure.ini"
    if not os.path.exists(structureFile):
        raise Exception("\n\t(!) Something went wrong: Configuration file {} not found".format(structureFile))
    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read(configFile)
    try:
        user = config.get("DB", "User")
        pwd = config.get("DB", "Password")
        host = config.get("DB", "Host")
        port = config.get("DB", "Port")
        db_name = config.get("DB", "DB_name")
        tb_name = config.get("DB", "Tb_name")
    except Exception as err:
        raise Exception("\n\t(!) Something went wrong reading {}: {}".format(configFile, err) +
                        "\n\tCheck file or remove it ")

    # Connection test
    try:
        conn = sql.connect(
            host=host,
            user=user,
            passwd=pwd,
            port=port,
        )
        if conn.is_connected():
            print("\n\tconnection with host {} established".format(host))
            cursor = conn.cursor()
    except sql.errors.Error as err:
        if err.errno == sql.errorcode.ER_ACCESS_DENIED_ERROR:
            raise Exception("\n\t(!) Something is wrong with your user name or password\n")
        else:
            raise Exception("\n\t(!) Connection went wrong: {}\n".format(err))

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
    tb_name = select_table(cursor, tb_name)
    while not tb_name:
        cont += 1
        if cont >= 3:
            disconnect(cursor, conn)
            raise Exception("\n\t(!) Something went wrong: exceeded maximum number of attempts to select a table\n")
        tb_name = select_table(cursor, tb_name)
    print("Table %s selected to upload data" % tb_name)

    config['DB'] = {'Host': host,
                    'Port': port,
                    'User': user,
                    'Password': pwd,
                    'DB_name': db_name,
                    'Tb_name': tb_name}
    with open('db.ini', 'w') as confFile:
        config.write(confFile)

    disconnect(cursor, conn)
    conf_data = [host, port, user, pwd, db_name]
    return conf_data


def disconnect(cursor, conn):
    """
    Function to disconnect  data base

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
        print("\n\t(!) Something went wrong while selecting database {}: {}\n".format(db_name, err))
        db_name = None
    return db_name


def create_table(cursor):
    default_features = ('EDA', 'SCL', 'SCR', 'ACC', 'IBI', 'TEMP')
    tb_name = input('Name of the new table: ')

    print('Default features are {}'.format(default_features))
    if_new_features = input('Do you want to use other features? (if yes, features declared in structure.ini file will '
                            + 'be used) (y/n): ')
    if if_new_features == 'y':
        structureFile = "structure.ini"
        config = configparser.ConfigParser(inline_comment_prefixes="#")
        config.read(structureFile)
        out_modules = config.items(section='FEATURES')
        features = ()
        for module in out_modules:
            features += tuple(module[1].split(', '))

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
        else:
            tb = input('Select table: ')
    try:
        cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_name=%s;", (tb,))
        if cursor.fetchone() is None:
            print("\n\t(!) Something went wrong while trying to select table %s: Table not found\n" % tb)
            tb = None
    except sql.errors.Error as err:
        print("\n\t(!) Something went wrong while trying to select table {}: {}\n".format(tb, err))
        tb = None
    return tb


if __name__ == '__main__':
    print('\nWelcome to data base configurator')
    connect()
