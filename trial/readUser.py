import subprocess
import sys
import os
from trial import csvmanage as cm
from trial import graphp as gp

# dir = sys.argv[1]

user = cm.get_user_input('Introduce directorio del usuario:\n')


def search(SOURCEDIR):
    # define the ls command
    ls = subprocess.Popen(["ls", "-p", SOURCEDIR+"."],
                          stdout=subprocess.PIPE,
                         )

    # define the grep command: search directories (files that end with /)
    grep = subprocess.Popen(["grep", "-e", "/$"],
                            stdin=ls.stdout,
                            stdout=subprocess.PIPE,
                            )

    # define the grep2 command: remove directories type __name__
    grep2 = subprocess.Popen(["grep", "-v", "__"],
                            stdin=grep.stdout,
                            stdout=subprocess.PIPE,
                            )

    # read from the end of the pipe (stdout)
    endOfPipe = grep2.stdout
    directories = list()
    # list the directories line by line
    for line in endOfPipe:
        directories.append(line.decode('utf-8').replace('\n',''))
    return directories


def search1(SOURCEDIR):
    # define the ls command
    ls = subprocess.Popen(["ls", "-p", SOURCEDIR+"."],
                          stdout=subprocess.PIPE,
                         )

    # define the grep command: search files (files that dont end with /)
    grep = subprocess.Popen(["grep", "-v", "/$"],
                            stdin=ls.stdout,
                            stdout=subprocess.PIPE,
                            )

    # define the grep2 command: remove directories type __name__
    grep2 = subprocess.Popen(["grep", "-v", "__"],
                            stdin = grep.stdout,
                            stdout = subprocess.PIPE,
                            )

    # read from the end of the pipe (stdout)
    end_of_pipe = grep2.stdout
    directories = list()
    # list the directories line by line
    for line in end_of_pipe:
        directories.append(line.decode('utf-8').replace('\n',''))
    return directories


directories = search(os.path.expanduser('~/empatica/' + user + '/basals/'))
resultsf = {}

for raw in directories:
    results = search1(os.path.expanduser('~/empatica/'+user + '/basals/'+raw+'Dataexport/'))
    if 'EDA.csv' in results:
        if 'TEMP.csv' in results:
            if 'HR.csv' in results:
                EDA = cm.load_results(os.path.expanduser('~/empatica/'+user+'/basals/'+raw+'Dataexport/EDA.csv'), 0)
                HR = cm.load_results(os.path.expanduser('~/empatica/'+user+'/basals/'+raw+'Dataexport/HR.csv'), 0)
                TEMP = cm.load_results(os.path.expanduser('~/empatica/'+user+'/basals/'+raw+'Dataexport/TEMP.csv'), 0)
                resultsf.update({raw: [EDA, HR, TEMP]})
# directories=search("empatica/MG4018009/")
# if 'basals/' in directories:
#     print('ok')
# else:
#     print('ko')
if not resultsf:
    print("No se encontraron ficheros EDA.csv, HR.csv, TEMP.csv en fichero dataexport para usuario {}".format(user))
else:
    gp.printGraph(resultsf)
