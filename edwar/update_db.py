import configparser
import os
import logging
import pandas as pd
import mysql.connector as sql
from edwar.csvmanage import load_results_e4, downsample_to_1hz


def connect():
    """
    Function that tries to obtain a connexion object to data base

    """
    # Config data
    conn = None
    cursor = None
    config = configparser.ConfigParser(inline_comment_prefixes="#")

    if not os.path.exists(configFile):
        raise Exception("Configuration file {} not found".format(configFile))

    config.read(configFile)
    try:
        user = config.get("DB", "User")
        pwd = config.get("DB", "Password")
        host = config.get("DB", "Host")
        port = config.get("DB", "Port")
        db = config.get("DB", "DB_name")
        tb = config.get("DB", "Tb_name")
    except Exception as err:
        raise Exception("\n\t(!) Something went wrong reading {}: {}".format(configFile, err) + "\n\tCheck file ")
    else:
        if not user or not pwd or not host or not port or not db or not tb:
            raise Exception("\n\t(!) Something went wrong reading {}: Missing data".format(configFile) +
                            "\n\tCheck file ")
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
            logging.info('\n\tconnection with host {} established.\n'.format(host))
            cursor = conn.cursor()
    except sql.errors.Error as err:
        if err.errno == sql.errorcode.ER_ACCESS_DENIED_ERROR:
            raise Exception("\n\t(!) Something is wrong with your user name or password")
        else:
            raise Exception("\n\t(!) Connection went wrong: {}".format(err))
    else:
        cursor.execute("select database();")
        db_name = cursor.fetchone()[0]
        logging.info("You are connected to database: ", db_name)
        logging.info("You have '{}' as table to upload data".format(tb))
        try:
            cursor.execute('''SELECT table_name FROM INFORMATION_SCHEMA.TABLES
            WHERE table_name=%s;''', (tb,))
            if cursor.fetchone() is None:
                disconnect(cursor, conn)
                raise Exception("\n\t(!) Something went wrong while trying to select table '%s': Table not found" % tb)
        except Exception as err:
            disconnect(cursor, conn)
            raise Exception("\n\t(!) Something went wrong trying to select table 'features': {}".format(err))

    finally:
        disconnect(cursor, conn)
    conf_data = [host, port, user, pwd, db_name, tb]
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
        logging.info('Connection could not be closed: {}'.format(err))
    return 1


def ts_transform(timestamp):
    date_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return date_time


def insert_data(conf_data, values):
    cursor = None
    n = 0
    f = 0
    errors = []
    n_cols = len(values.columns)
    tb = conf_data[5]
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
        raise Exception("\n\t(!) Connection went wrong: {}".format(err))
    else:
        try:
            cursor.execute('DESCRIBE %s' % tb)
        except Exception as err:
            raise Exception("\n\t(!) Something went wrong in insert_data() function while getting columns " +
                            "from table `{}`: {}".format(tb, err))
        else:
            tb_columns = [i[0] for i in cursor.fetchall()]
            n_cols = len(tb_columns)
        finally:
            if n_cols != len(values.columns):
                raise Exception("\n\t(!) There are not same number of data and columns in table '%s'" % tb)

        # creating column list for insertion
        cols = "`,`".join([str(i) for i in values.columns.tolist()])

        # Insert DataFrame records one by one.
        for i, row in values.iterrows():
            order = "INSERT INTO `{}` (`".format(tb) + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
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
            logging.info(n, "record(s) inserted")
        if f:
            logging.info("(!) %i record(s) could not be inserted" % f)
            logging.error('Errors: ')
            for error in errors:
                logging.error('\t%i- %s' % (errors.index(error), error))
        disconnect(cursor, conn)


def prepare_features(data):
    tb_columns = ['data_type', 'ts', 'value']
    ncols = len(data.columns)
    nrows = len(data)
    list_update = pd.DataFrame(index=range(0, ncols * nrows), columns=tb_columns)
    n = 0
    for column in data.columns:
        for index in range(0, nrows):
            list_update.loc[n*nrows+index, tb_columns] = [column, ts_transform(data[column].index[index]),
                                                          float(data[column].values[index])]
        n += 1
    return list_update


if __name__ == '__main__':
    # provisional
    directory = '../data/ejemplo1'
    results = load_results_e4(directory)[0][0:100]
    results = downsample_to_1hz(results)
    # not provisional
    configFile = "db.ini"

    logging.info('\nWelcome to data base manager')
    connection = connect()
    up_data = prepare_features(results)
    insert_data(connection, up_data)
