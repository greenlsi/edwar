import configparser
import os
import sys

import mysql.connector as sql

from trial.csvmanage import get_input


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
        index = int(get_input('Select database (0, 1, 2, ..): '))
        while index >= i:
            index = int(get_input('\n\t(!) Something went wrong. Select number between 0 and {}: '.format(i - 1)))
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
    cursor.execute("SHOW TABLES")
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


def finish(cursor):
    fail = disconnect(cursor)
    if not fail:
        sys.exit(0)


if __name__ == '__main__':
    Help = '''\ncommand show to see list of tables in database selected\ncommand create to create table
command delete to delete table\ncommand exit to terminate program\n'''
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
                if 'delete' in cmd:
                    table = delete_table(mycursor, database, Tables)
                    correct = 1
                if 'help' in cmd:
                    correct = 1
                    print(Help)
                if not correct:
                    print('wrong command, print help if needed')
