import os


def save_in_csv(path, my_file, my_data):
    try:
        my_data.to_csv(os.path.join(path, my_file), encoding='utf-8', index=True)
    except IOError:
        raise IOError("Path {} not Found".format(path))
    except Exception:
        raise Exception("Error while writing in {}".format(os.path.join(path, my_file)))
