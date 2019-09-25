import configparser
import os
import sys
import mysql.connector as sql


def connect():
    """
    Function that tries to obtain a connexion object to data base

    """
    # Config data
    cursor = None
    config = configparser.ConfigParser(inline_comment_prefixes="#")

    if not os.path.exists(configFile):
        print("Configuration file {} not found. New {} created".format(configFile, configFile))
        config['DB'] = {'Host': '  # leave blank to use default value',
                        'Port': '  # leave blank to use default value',
                        'User': '',
                        'Password': '',
                        'DB_name': ''}
        with open('config.ini', 'w') as confFile:
            config.write(confFile)

    config.read(configFile)
    try:
        user = config.get("DB", "User")
        pwd = config.get("DB", "Password")
        host = config.get("DB", "Host")
        port = config.get("DB", "Port")
        db = config.get("DB", "DB_name")
    except Exception as err:
        print("\n\t(!) Something went wrong reading {}: {}".format(configFile, err) + "\n\tCheck file or remove it ")
        sys.exit(1)

    if not user or not pwd:
        user, pwd, host, port = configuration_connexion()
    host = host if host else '108.128.85.44'
    port = port if port else 3306

    # Connection test
    try:
        conn = sql.connect(
            host=host,
            user=user,
            passwd=pwd,
            port=port,
        )
        if conn.is_connected():
            print('\n\tconnection with host {} established.\n'.format(host))
            cursor = conn.cursor()
    except sql.errors.Error as err:
        if err.errno == sql.errorcode.ER_ACCESS_DENIED_ERROR:
            print("\n\t(!) Something is wrong with your user name or password")
            sys.exit(1)
        else:
            print("\n\t(!) Connection went wrong: {}".format(err))
            sys.exit(1)

    cont1 = 0
    while not db:
        db = select_database(cursor)
        cont1 += 1
        if cont1 >= 3:
            print("\n\t(!) Something went wrong: exceeded maximum number of attempts to select a database")
            disconnect(cursor, conn)
            sys.exit(1)
    disconnect(cursor, conn)

    try:
        conn = sql.connect(
            host=host,
            user=user,
            passwd=pwd,
            port=port,
            database=db
        )
        if conn.is_connected():
            cursor = conn.cursor()
    except Exception as err:
        print("\n\t(!) Something went wrong trying to select database {}: {}".format(db, err))
        disconnect(cursor, conn)
        sys.exit(1)
    else:
        cursor.execute("select database();")
        db_name = cursor.fetchone()[0]
        print("You are connected to database: ", db_name)

    tb = None
    cont = 0
    while tb is None:
        tb = select_table(cursor)
        cont += 1
        if cont1 >= 3:
            print("\n\t(!) Something went wrong: exceeded maximum number of attempts to select a database")
            disconnect(cursor, conn)
            sys.exit(1)

    print("Table features configured to upload data ")
    try:
        cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_name='features';")
        if cursor.fetchone() is None:
            print("\n\t(!) Something went wrong while trying to select table features: Table not found")
            disconnect(cursor, conn)
            sys.exit(1)
    except Exception as err:
        print("\n\t(!) Something went wrong while trying to select table features: {}".format(err))
        disconnect(cursor, conn)
        sys.exit(1)

    config['DB'] = {'Host': '{}  # leave blank to use default value'.format(host),
                    'Port': '{}  # leave blank to use default value'.format(port),
                    'User': user,
                    'Password': pwd,
                    'DB_name': db_name}
    with open('config.ini', 'w') as confFile:
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


def configuration_connexion():
    print('\t--Configuration--')
    host = input('Host address (press enter to leave default value): ')
    port = input('Port number (press enter to leave default value): ')
    print('\t--Identification--')
    user = input('User Name: ')
    pwd = input('Password: ')

    return user, pwd, host, port


def select_database(cursor):
    print('\t--Database Selection--')
    cursor.execute("SHOW DATABASES")
    i = 0
    databases = []
    db = None
    print('\nDatabases in host:')
    for x in cursor:
        print('{}. {}'.format(i, x[0]))
        databases.append(x[0])
        i += 1
    if len(databases) == 0:
        print('\nNo databases, you have to create one')
        a = 'y'
    else:
        a = input('\nDo you want to use another database? (if yes you will create a new one) (y/n): ')
    if a == 'y':
        db_name = input('Name of the new database: ')
        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(db_name))
            db = db_name
        except sql.errors.Error as err:
            if err.errno == sql.errorcode.ER_DBACCESS_DENIED_ERROR:
                print("\n\t(!) Permission denied to create database")
            else:
                print("\n\t(!) Something went wrong while creating database: {}".format(err))
    else:
        if len(databases) == 1:
            db = databases[0]
        else:
            while db is None:
                db_selected = input('Select database: ')
                try:
                    index = int(db_selected)
                    if index >= i:
                        print('\n\t(!) Something went wrong. Select number between 0 and {}: '.format(i - 1))
                    else:
                        db = databases[index]
                except ValueError:
                    try:
                        index = databases.index(db_selected)
                    except ValueError:
                        print("\n\t(!) Database not found")
                    else:
                        db = databases[index]

    return db


def show_tables(cursor, to_print):
    tables1 = []
    cursor.execute("select database();")
    db = cursor.fetchone()[0]
    try:
        if to_print:
            print('\nTables in {}:'.format(db))
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for tb in tables:
            if to_print:
                print('{}. {}'.format(tables.index(tb), tb[0]))
            tables1.append(tb[0])
    except Exception as err:
        print("\n\t(!) Something went wrong in show_tables(): {}".format(err))

    return tables1


def create_table(cursor):
    features = {}

    print('\nDefault features are {}'.format(header_needed))
    if_new_features = input('Do you want to use more features? (if yes you will create more) (y/n): ')
    if if_new_features == 'y':
        i = 0
        feature = 'feature'
        while feature:
            i = i + 1
            feature = input('\nName Feature%i (press enter to finish): ' % i)
            if feature:
                datatype = None
                while datatype is None:
                    datatype = input('Type (`v` varchar/`d` datetime/`f` float): ')
                    if datatype == 'v':
                        datatype = 'varchar(20) CHARACTER SET latin1 COLLATE latin1_spanish_ci'
                    elif datatype == 'd':
                        datatype = 'datetime'
                    elif datatype == 'f':
                        datatype = 'float'
                    else:
                        print("\n\t(!) Something went wrong while selecting data type: Must be varchar or datetime"
                              + " or float")
                        datatype = None

                    features.update({feature: datatype})

    try:
        cursor.execute('''CREATE TABLE features (
                       `patient_id` varchar(9) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
                       `session_id` varchar(8) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
                       `data_type` enum('EDA','SCL','SCR','') CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
                       `ts` datetime NOT NULL,
                       `value` float NOT NULL,
                       PRIMARY KEY (`session_id`,`data_type`, `ts`)) 
                       ENGINE=InnoDB DEFAULT CHARSET=latin1;''')
        print("\ntable 'features' created")
    except sql.errors.Error as err:
        print("\n\t(!) Something went wrong while creating table 'features': {}".format(err))
        return None
    else:
        try:
            cursor.execute(
                '''ALTER TABLE features ADD CONSTRAINT
                FOREIGN KEY (`patient_id`,`session_id`) REFERENCES `e4_sessions` (`patient_id`, `session_id`)
                ON DELETE CASCADE ON UPDATE CASCADE''')
        except sql.errors.Error as err:
            print("\n\t(!) Something went wrong while trying to connect features `patient_id` and `session_id` of table"
                  + " 'features' to table `e4_sessions`: {}".format(err))

        if features:
            order = ''
            for feature in features.keys():
                try:
                    order = '''ALTER TABLE features ADD {} {}'''.format(feature, features[feature])
                    cursor.execute("ALTER TABLE features ADD {} {}".format(feature, features[feature]))
                except sql.errors.Error as err:
                    print("\n\t(!) Something went wrong while executing {}: {}".format(order, err))
                    delete_table(cursor)
                    return None
    return 'features'


def select_table(cursor):
    usable_tables = []
    table_selected = None
    tb = None
    tables = show_tables(cursor, 1)
    try:
        for tb in tables:
            cursor.execute('''SELECT column_name, data_type 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE table_name = %s;''',  (tb,))
            header = dict(cursor.fetchall())
            if set(header.keys()).intersection(header_needed) == header_needed:
                if header['ts'] == 'datetime' and header['value'] == 'float':
                    usable_tables.append(tb)

    except sql.errors.Error as err:
        print("\n\t(!) Something went wrong while reading header of table {}: {}".format(tb, err))

    else:
        print('\nUsable tables: ')
        if len(usable_tables) == 0:
            print("\nNo tables available to save program data, so you have to create a new one"
                  "\n(Header must contain {} fields)".format(header_needed))
            a = 'y'
        else:
            for x in usable_tables:
                print('{}. {}'.format(usable_tables.index(x), x))
            a = input('\nDo you want to use another table? (if yes you will create a new one) (y/n): ')

        if a == 'y':
            if 'features' in usable_tables:
                print('\n\t(!) Something went wrong: a table named features already exists')
                b = input('\nDo you want to remove it? (y/n): ')
                if b == 'y':
                    delete_table(cursor)
                else:
                    return None
            table_selected = create_table(cursor)
        else:
            if len(usable_tables) == 1:
                table_selected = usable_tables[0]
                if table_selected != 'features':
                    table_selected = rename_table(cursor, table_selected, usable_tables)
            else:
                while table_selected is None:
                    table_selected = input('Select table: ')
                    try:
                        index = int(table_selected)
                        if index > len(usable_tables) - 1:
                            print('\n\t(!) Something went wrong. Select number between 0 and {}: '.format(
                                len(usable_tables) - 1))
                            table_selected = None
                        else:
                            table_selected = usable_tables[index]
                            if table_selected != 'features':
                                table_selected = rename_table(cursor, table_selected, usable_tables)
                    except ValueError:
                        try:
                            index = usable_tables.index(table_selected)
                        except ValueError:
                            print("\n\t(!) Table not found")
                            table_selected = None
                        else:
                            table_selected = usable_tables[index]
                            if table_selected != 'features':
                                print('Table name must be features, so table %s will be renamed' % table_selected)
                                if 'features' in usable_tables:
                                    if table_selected != 'features':
                                        table_selected = rename_table(cursor, table_selected, usable_tables)

    return table_selected


def rename_table(cursor, tb, usable_tables):
    print('Table name must be features, so table %s will be renamed' % tb)
    if 'features' in usable_tables:
        print('\n\t(!) Something went wrong: a table named features already exists')
        b = input('\nDo you want to remove it? (y/n): ')
        if b == 'y':
            delete_table(cursor)
        else:
            return None
    try:
        cursor.execute("ALTER TABLE %s RENAME TO features" % tb)
    except sql.errors.Error as err:
        print("\n\t(!) Something went wrong while renaming table {}: {}".format(tb, err))
        sys.exit(1)
    else:
        print("table %s renamed successfully to 'features'" % tb)
        return 'features'


def delete_table(cursor):
    try:
        cursor.execute("DROP TABLE IF EXISTS features")
        print('table features deleted')
    except Exception as err:
        print("\n\t(!) Something went wrong while deleting table features: {}".format(err))
        return


if __name__ == '__main__':
    configFile = "config.ini"
    header_needed = ['patient_id', 'session_id', 'data_type', 'ts', 'value']
    print('\nWelcome to data base configurator')
    connect()
    sys.exit(0)
