
import pandas as pd


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
