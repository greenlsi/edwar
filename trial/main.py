import csvmanage as cm
import graph as gp

EDA = cm.load_results('ejemplo/EDA.csv',0)
HR  = cm.load_results('ejemplo/HR.csv',0)
TEMP= cm.load_results('ejemplo/TEMP.csv',0)

gp.printGraph(EDA,HR,TEMP)
