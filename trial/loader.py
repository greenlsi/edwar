import os
import sys
import zipfile

from trial.csvmanage import load_results


def load_sessions(directory):
    sessions = []
    devices = os.listdir(directory)
    for device in devices:
        sessions = os.listdir(directory + '/' + device)
        for session in sessions:
            zfile = zipfile.ZipFile(directory + '/' + device + '/' + session)
            files = read_zip_file(zfile)
            if all(x in files for x in ['ACC.csv', 'EDA.csv', 'TEMP.csv', 'HR.csv']):
                load_results(zfile.open('EDA.csv'))
    return sessions


def read_zip_file(zfile):
    ifile_list = []
    for finfo in zfile.namelist():
        ifile = zfile.open(finfo)
        ifile_list.append(ifile.name)
    return ifile_list


if __name__ == '__main__':
    path = '../data/e4sync'
    load_sessions(path)
