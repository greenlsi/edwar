import configparser
import os
import sys
import pandas as pd

import mysql.connector as sql
from trial.csvmanage import load_results


def connect():
    """
    Function that tries to obtain a connexion object to data base

    """
    # Config data
    conn = None
    cursor = None
    config = configparser.ConfigParser(inline_comment_prefixes="#")

    if not os.path.exists(configFile):
        print("Configuration file {} not found".format(configFile))
        sys.exit(1)

    config.read(configFile)
    try:
        user = config.get("DB", "User")
        pwd = config.get("DB", "Password")
        host = config.get("DB", "Host")
        port = config.get("DB", "Port")
        db = config.get("DB", "DB_name")
    except Exception as err:
        print("\n\t(!) Something went wrong reading {}: {}".format(configFile, err) + "\n\tCheck file ")
        sys.exit(1)
    else:
        if not user or not pwd or not db:
            print("\n\t(!) Something went wrong reading {}: Missing data".format(configFile) + "\n\tCheck file ")
            sys.exit(1)
        else:
            host = host if host else '108.128.85.44'
            port = port if port else 3306

    # Connection test
    try:
        conn = sql.connect(
            host=host,
            user=user,
            passwd=pwd,
            port=port,
            database=db
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
    else:
        cursor.execute("select database();")
        db_name = cursor.fetchone()[0]
        print("You are connected to database: ", db_name)
        print("You have 'features' as table to upload data")
        try:
            cursor.execute('''SELECT table_name FROM INFORMATION_SCHEMA.TABLES
            WHERE table_name='features';''')
            if cursor.fetchone() is None:
                print("\n\t(!) Something went wrong while trying to select table 'features': Table not found")
                disconnect(cursor, conn)
                sys.exit(1)
        except Exception as err:
            print("\n\t(!) Something went wrong trying to select table 'features': {}".format(err))
            disconnect(cursor, conn)
            sys.exit(1)

    finally:
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


def ts_transform(timestamp):
    date_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return date_time


def insert_data(conf_data, values):
    cursor = None
    n = 0
    f = 0
    errors = []
    n_cols = 5
    try:
        conn = sql.connect(
            host=conf_data[0],
            port=conf_data[1],
            user=conf_data[2],
            passwd=conf_data[3],
            database=conf_data[4],
        )
        if conn.is_connected():
            cursor = conn.cursor()
            conn.autocommit = False
    except Exception as err:
        print("\n\t(!) Connection went wrong: {}".format(err))
        sys.exit(1)
    else:
        try:
            cursor.execute('DESCRIBE`features`')
        except Exception as err:
            print("\n\t(!) Something went wrong in insert_data() function while getting columns " +
                  "from table `features`: {}".format(err))
        else:
            tb_columns = [i[0] for i in cursor.fetchall()]
            n_cols = len(tb_columns)
        finally:
            if n_cols != len(values.columns):
                print("\n\t(!) There are not same number of data and columns in table ´features´")
                sys.exit(1)

        # creating column list for insertion
        cols = "`,`".join([str(i) for i in values.columns.tolist()])

        # Insert DataFrame records one by one.
        for i, row in values.iterrows():
            order = "INSERT INTO `features` (`" + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
            try:
                cursor.execute(order, tuple(row))
                # the connection is not autocommitted by default, so we must commit to save our changes
                conn.commit()
                n += 1
            except sql.errors.Error as err:

                errors.append(err)
                f += 1
                conn.rollback()
        if n:
            print(n, "record(s) inserted")
        if f:
            print("(!) %i record(s) could not be inserted" % f)
            print('Errors: ')
            for error in errors:
                print('\t%i- %s' % (errors.index(error), error))
        disconnect(cursor, conn)


def delete_data(conf_data, condition, check=None):
    msg1 = ''
    cursor = None
    try:
        conn = sql.connect(
            host=conf_data[0],
            port=conf_data[1],
            user=conf_data[2],
            passwd=conf_data[3],
            database=conf_data[4],
        )
        if conn.is_connected():
            cursor = conn.cursor()
            conn.autocommit = False
    except Exception as err:
        print("\n\t(!) Connection went wrong: {}".format(err))
    else:
        try:
            msg1 = "DELETE FROM `features` WHERE {}".format(condition)
            cursor.execute(msg1)
            if check != 1:
                conn.commit()
            else:
                a = input("{} record(s) will be deleted. Are you sure? (y/n) ".format(cursor.rowcount))
                if a == 'y':
                    conn.commit()
                    print(cursor.rowcount, "record(s) deleted")
                else:
                    print(cursor.rowcount, "record(s) delete canceled")
                    conn.rollback()
        except Exception as err:
            print("\n\t(!) Something went wrong: {}\n\torder: {}".format(err, msg1))
            conn.rollback()
            return 1

    return 0


def get_user_from_session(conf_data, session_id):
    cursor = None
    try:
        conn = sql.connect(
            host=conf_data[0],
            port=conf_data[1],
            user=conf_data[2],
            passwd=conf_data[3],
            database=conf_data[4],
        )
        if conn.is_connected():
            cursor = conn.cursor()
            conn.autocommit = False
    except Exception as err:
        print("\n\t(!) Connection went wrong: {}".format(err))
    else:
        try:
            cursor.execute('SELECT `patient_id` FROM `e4_sessions` WHERE session_id = %s', (session_id,))
        except Exception as err:
            print("\n\t(!) Something went wrong in get_user_from_session() function while trying to get patient_id " +
                  "from session_id: {}".format(err))
        else:
            result = cursor.fetchone()
            if len(result) > 1:
                print("\n\t(!) Something went wrong in get_user_from_session() function: Multiple patients for one " +
                      "session: session_id {} --> user_ids {}".format(session_id, result))
                sys.exit(1)
            return result[0]
    return None


def prepare_features(conf_data, session_id, feature_id, feature):
    columns = ['patient_id', 'session_id', 'data_type', 'ts', 'value']
    list_update = pd.DataFrame(index=range(0, len(feature)), columns=columns)
    patient_id = get_user_from_session(conf_data, session_id)
    for i in range(0, len(feature)):
        list_update.loc[i, columns] = [patient_id, session_id, feature_id, ts_transform(feature.index[i]),
                                       float(feature.values[i])]
    return list_update


if __name__ == '__main__':
    # provisional
    directory = '../data/ejemplo1'
    results = load_results(directory)[0:100]
    EDA = results['EDA']

    # no provisional
    configFile = "config.ini"

    print('\nWelcome to data base manager')
    connection = connect()
    up_list = prepare_features(connection, '029051', 'EDA', EDA)
    insert_data(connection, up_list)
