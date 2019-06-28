import configparser
import os
import sys

import mysql.connector as sql

from trial.csvmanage import get_input, load_results


def timestamp_tranform(timestamp):
    date_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return date_time


def connect(user, pwd, host='108.128.85.44', port=3306):
    """
    Function that tries to obtain a connexion object to data base

    Parameters
    ----------
    user : string
    pwd : string

    Optional Parameters
    -------------------
    host : string
    port : int

    Returns
    -------
        mydb object that represents connexion to data base

    Exception
    ---------
        None if exceptions happen

    """
    try:

        mydb = sql.connect(
            host=host,
            user=user,
            passwd=pwd,
            port=port,
        )
        return mydb
    except sql.errors.Error as err:
        if err.errno == sql.errorcode.ER_ACCESS_DENIED_ERROR:
            print("\n\t(!) Something is wrong with your user name or password")
        else:
            print("\n\t(!) Something went wrong: {}".format(err))
        sys.exit(1)


def disconnect(cursor):
    """
    Function to disconnect  data base

    Parameters
    ----------
    cursor : cursor object

    """
    try:
        cursor.close()
        return 0
    except sql.Error as err:
        print('Connexion could not be closed: {}'.format(err))
    return 1


def configuration_connexion():
    conf = configparser.ConfigParser()
    print('\t--Configuration--')
    host = get_input('Host address (press enter to leave default value): ')
    port = get_input('Port number (press enter to leave default value): ')
    print('\t--Identification--')
    user = get_input('User Name: ')
    pwd = get_input('Password: ')
    conf['DB'] = {'Host': host + '  # leave blank to use default value',
                  'Port': port + '  # leave blank to use default value',
                  'User': user,
                  'Password': pwd}
    with open('config.ini', 'w') as confFile:
        conf.write(confFile)

    return host, port, user, pwd


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

    a = get_input('\nDo you want to use another database? (if yes you will create a new one) (y/n): ')
    if a == 'y':
        db_name = get_input('Name of the new database: ')
        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(db_name))
            db = db_name
        except sql.errors.Error as err:
            if err.errno == sql.errorcode.ER_DBACCESS_DENIED_ERROR:
                print("\n\t(!) Permission denied")
            else:
                print("\n\t(!) Something went wrong: {}".format(err))
    else:
        while db is None:
            db_selected = get_input('Select database: ')
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
    if db:
        try:
            cursor.execute("USE {}".format(db))
            print('{} selected'.format(db))
        except Exception as err:
            print("\n\t(!) Something went wrong: {}".format(err))

    return db


def show_tables(cursor, db, to_print):
    if to_print:
        print('Tables in {}'.format(db))
    try:
        cursor.execute("SHOW TABLES")
    except Exception as err:
        print("\n\t(!) Something went wrong: {}".format(err))
    tables = []
    i = 0
    for x in cursor:
        if to_print:
            print('{}. {}'.format(i, x[0]))
        tables.append(x[0])
        i += 1
    return tables


def delete_table(cursor, db, tables):
    index = None
    while index is None:
        tb = get_input('\nSelect table to delete: ')
        if not tb:
            print('delete canceled')
            return 0
        else:
            try:
                index = int(tb)
                tb = tables[index]
            except ValueError:
                try:
                    index = tables.index(tb)

                except ValueError:
                    print("\n\t(!) Table not found")
                else:
                    a = get_input('{} selected. Are you sure you want to delete it? (y/n): '.format(tables[index]))
                    if a == 'y':
                        try:
                            cursor.execute("DROP TABLE IF EXISTS {}".format(tables[index]))
                            print('table {} deleted from {}'.format(tables[index], db))
                        except Exception as err:
                            print("\n\t(!) Something went wrong: {}".format(err))
                    else:
                        print('delete canceled')
            else:
                a = get_input('{} selected. Are you sure you want to delete it? (y/n): '.format(tables[index]))
                if a == 'y':
                    try:
                        cursor.execute("DROP TABLE IF EXISTS {}".format(tables[index]))
                        print('table {} deleted from {}'.format(tables[index], db))
                    except Exception as err:
                        print("\n\t(!) Something went wrong: {}".format(err))
                else:
                    print('delete canceled')
    return 0


def create_table(cursor, db):
    tb = None
    tb_name = get_input('Name of the new table: ')
    if not tb_name:
        return 0
    try:
        cursor.execute('''CREATE TABLE `{}` (
                       `patient_id` varchar(9) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
                       `session_id` varchar(8) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
                       `data_type` enum('EDA','SCL','SCR','') CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
                        `ts` datetime NOT NULL,
                        `value` float NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=latin1;'''.format(tb_name))
        cursor.execute(
            '''ALTER TABLE `features` ADD CONSTRAINT `patient_session_fk` 
            FOREIGN KEY (`patient_id`,`session_id`) REFERENCES `e4_sessions` (`patient_id`, `session_id`) 
            ON DELETE CASCADE ON UPDATE CASCADE''')
        tb = tb_name
        print('table {} created in {}'.format(tb, db))
    except sql.errors.Error as err:
        print("\n\t(!) Something went wrong: {}".format(err))

    return tb


def insert(cursor, conn, tb, values):
    columns = '('
    count = 0
    try:
        cursor.execute("DESCRIBE {}".format(tb))
        for x in cursor:
            columns += (x[0] + ', ')
            count += 1
        new = list(columns)
        new[-2] = ')'
        new[-1] = ''
        columns = ''.join(new)
    except Exception as err:
        print("\n\t(!) Something went wrong: {}".format(err))
        return 1
    # print(columns)
    msg = "\n\t(!) Something went wrong: {} values but table {} has {} columns".format(len(values[0]), tb, count)
    if len(values[0]) != count:
        print(msg)
        return 1
    msg1 = ''
    try:
        if len(values)-1:
            msg1 = "INSERT INTO {} {} VALUES {}".format(tb, columns, values)
            cursor.executemany(msg1)
        else:
            msg1 = "INSERT INTO {} {} VALUES {}".format(tb, columns, values[0])
            cursor.execute(msg1)
    except Exception as err:
        print("\n\t(!) Something went wrong: {}\n\torder: {}".format(err, msg1))
        return 1

    conn.commit()

    print(cursor.rowcount, "record(s) inserted.")
    return 0


def delete(cursor, conn, tb, condition):
    msg1 = ''
    try:
        msg1 = "DELETE FROM {} WHERE {}".format(tb, condition)
        cursor.execute(msg1)
    except Exception as err:
        print("\n\t(!) Something went wrong: {}\n\torder: {}".format(err, msg1))
        return 1
    a = get_input("{} record(s) will be deleted. Are you sure? (y/n)".format(cursor.rowcount))
    if a == 'y':
        conn.commit()
        print(cursor.rowcount, "record(s) deleted")
    else:
        print(cursor.rowcount, "record(s) delete canceled")
        cursor.execute("ROLLBACK")

    return 0


def insert_features(cursor, conn, values):
    tb = 'features'
    if type(values) is not list:
        print("\n\t(!) Something went wrong: parameter values in function insert_features must be a list")
        return 1
    if len(values) != 5:
        print("\n\t(!) Something went wrong: parameter values in function insert_features must be a list")
    if values[2] != 'EDA' or 'SCL' or 'SCR':
        print("\n\t(!) Something went wrong: element data_type in values must be EDA, SCL or SCR")
        return 1
    values[3] = timestamp_tranform(values[3])


def finish(cursor):
    fail = disconnect(cursor)
    if not fail:
        sys.exit(0)


if __name__ == '__main__':
    directory = '../data/ejemplo1'
    EDA = load_results(directory)[0:100]
    Help = "\ncommand show to see list of tables in database selected\ncommand create to create table \ncommand " \
           "drop to delete table\ncommand exit to terminate program\n "
    finished = 0
    database = None
    print('\nWelcome to data base manager')

    # Config data
    configFile = "config.ini"
    if not os.path.exists(configFile):
        print("The configuration file {} does not exist.".format(configFile))
        sys.exit(1)
    else:
        config = configparser.ConfigParser(inline_comment_prefixes="#")
        config.read(configFile)
        Host = config.get("DB", "Host")
        Port = config.get("DB", "Port")
        User = config.get("DB", "User")
        Pass = config.get("DB", "Password")
        if not User or not Pass:
            Host, Port, User, Pass = configuration_connexion()

        if not Host:
            if not Port:
                connection = connect(User, Pass)
            else:
                connection = connect(User, Pass, port=Port)
        else:
            if not Port:
                connection = connect(User, Pass, host=Host)
            else:
                connection = connect(User, Pass, host=Host, port=Port)

    if connection is not None:
        mycursor = connection.cursor()
        table = None
        while database is None:
            database = select_database(mycursor)
        if database:
            while 1:
                correct = 0
                Tables = show_tables(mycursor, database, 0)
                cmd = get_input('CMD: ')
                if 'exit' in cmd:
                    finish(mycursor)
                    correct = 1
                if 'show' in cmd:
                    show_tables(mycursor, database, 1)
                    correct = 1
                if 'create' in cmd:
                    table = create_table(mycursor, database)
                    correct = 1
                if 'drop' in cmd:
                    table = delete_table(mycursor, database, Tables)
                    correct = 1
                if 'insert' in cmd:
                    insert(mycursor, connection, 'features', [('MG0319029', '029051', 0, 0, 0)])
                    correct = 1
                if 'delete' in cmd:
                    delete(mycursor, connection, 'features', "ts = '0000-00-00 00:00:00'")
                    correct = 1
                if 'help' in cmd:
                    correct = 1
                    print(Help)
                if not correct:
                    print('wrong command, print help if needed')
