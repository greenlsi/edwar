import mysql.connector as sql
import pandas as pd

from ..utils.db_connection import connect, disconnect
from ..utils.configuration import edit_connection_parameters


__all__ = {
    'save_in_db',
    'adapt_features'
}


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


def save_in_db(settings, values):
    n = 0
    f = 0
    errors = []
    n_cols = len(values.columns)
    host, port, user, pwd, db_name, tb_name = edit_connection_parameters(settings)
    conn, cursor, tb = connect(host, port, user, pwd)
    try:
        cursor.execute('DESCRIBE %s' % tb)
    except Exception as err:
        raise Exception("\n\t(!) Something went wrong in save_in_db() function while getting columns " +
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
            # the connection_database is not autocommitted by default, so we must commit to save our changes
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
