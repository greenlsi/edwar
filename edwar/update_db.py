import configparser
import os
import logging
import mysql.connector as sql


def _connect():
    """
    Function that tries to obtain a connexion object to data base

    """
    # Config data
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
                _disconnect(cursor, conn)
                raise Exception("\n\t(!) Something went wrong while trying to select table '%s': Table not found" % tb)
        except Exception as err:
            _disconnect(cursor, conn)
            raise Exception("\n\t(!) Something went wrong trying to select table 'features': {}".format(err))
    return conn, cursor, tb


def _disconnect(cursor, conn):
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
        logging.info('Connection could not be closed: {}'.format(err))
    return 1


def insert_data(values):
    n = 0
    f = 0
    errors = []
    n_cols = len(values.columns)
    conn, cursor, tb = _connect()
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
    _disconnect(cursor, conn)


if __name__ == '__main__':
    # provisional
    from edwar.file_loader import e4 as cm

    try:
        from .data_to_db_adapter import adapt_features
    except ImportError:
        raise ImportError('File data_to_db_adapter not found. Run init_db.py to generate it')
    directory = '../data/ejemplo1'
    results = cm.load_files(directory)[0][0:100]
    results = cm.downsample_to_1hz(results)
    # not provisional
    configFile = "db.ini"

    logging.info('\nWelcome to data base manager')
    up_data = adapt_features(results)
    insert_data(up_data)
