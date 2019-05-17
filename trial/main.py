from trial import csvmanage as cm
from trial import graph as gp

EDA = cm.load_results('../data/ejemplo/EDA.csv',1)
HR  = cm.load_results('../data/ejemplo/HR.csv',1)
TEMP= cm.load_results('../data/ejemplo/TEMP.csv',1)
print(TEMP)
# gp.printGraph(EDA,HR,TEMP)
