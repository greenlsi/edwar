import os

from trial.csvmanage import load_results


def load_sessions(directory):
    devices = os.listdir(directory)
    for device in devices:
        sessions = os.listdir(directory + '/' + device)
        for session in sessions:
            data = load_results(directory + '/' + device + '/' + session)
            if data is not None:
                print(data)
    return


if __name__ == '__main__':
    path = '../data/e4sync'
    load_sessions(path)
