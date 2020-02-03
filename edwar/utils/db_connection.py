import mysql.connector as sql


def connect(host, port, user, pwd):
    """
    Function that tries to obtain a connexion object to data base

    """
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
