import pandas as pd
import mysql.connector as sql

from ..utils.db_connection import connect, disconnect
from ..utils.configuration import edit_connection_parameters, open_session, close_session
from ..errors import *


__all__ = {
    'save_in_db',
    'adapt_features'
}


def _ts_transform(timestamp):
    date_time = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
    return date_time


def adapt_features(data):
    list_table_columns = ['data_type', 'ts', 'value']  # proposed table
    ncols = len(data.columns)
    nrows = len(data)
    list_update = pd.DataFrame(index=range(0, ncols * nrows), columns=list_table_columns)
    n = 0
    for column in data.columns:
        list_update.loc[n * nrows: (n + 1) * nrows, list_table_columns[0]] = [str(column)]*nrows
        list_update.loc[n * nrows: (n + 1) * nrows, list_table_columns[1]] = _ts_transform(data.index)
        list_update.loc[n * nrows: (n + 1) * nrows, list_table_columns[2]] = data[column].values
        n += 1
    list_update1 = [tuple(r) for r in list_update.values]
    return list_update1


def save_in_db(settings, values, pw):
    n_cols = len(values[0])  # values must be list of tuples. len(tuple)=len(table_columns); len(list)=len(data_rows)
    session = open_session(settings, pw=pw)
    host, port, user, pwd, db_name, tb_name = edit_connection_parameters(session)
    close_session(session)
    try:
        conn, cursor = connect(host, port, user, pwd)
    except ConnectionRefusedError:
        raise DatabaseLoginError()
    except ConnectionError:
        raise DatabaseConnectionError()

    try:
        cursor.execute("USE {}".format(db_name))
        cursor.execute('DESCRIBE %s' % tb_name)
    except Exception as err:
        raise DatabaseError("Unexpected error while getting columns in database {} from table {}: {}. "
                            "Impossible to upload data to database.".format(db_name, tb_name, err))
    else:
        tb_columns = [i[0] for i in cursor.fetchall()]
        if n_cols != len(tb_columns):
            raise DatabaseError("There are not same number of data and table columns for table {}. "
                                "Impossible to upload data to database.".format(tb_name))

    # creating column list for insertion
    cols = "`,`".join([str(i) for i in tb_columns])

    # Insert DataFrame records one by one.
    order = "INSERT INTO `{}` (`".format(tb_name) + cols + "`) VALUES (" + "%s," * (n_cols - 1) + "%s)"
    try:
        cursor.executemany(order, values)
        # the connection_database is not autocommitted by default, so we must commit to save our changes
        conn.commit()
    except sql.errors.Error as err:
        conn.rollback()
        raise DatabaseError("Unexpected error in data upload: {}.".format(err))
    finally:
        try:
            disconnect(cursor, conn)
        except ConnectionError:
            pass
