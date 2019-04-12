#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import sys
import os
from trial import csvmanage as cm
from trial import graph as gp

# directory = sys.argv[1]

directory = cm.get_user_input('Introduce path al directorio de resultados:\n')

EDA = cm.load_results(directory + '/EDA.csv', 0)
HR = cm.load_results(directory + '/HR.csv', 0)
TEMP = cm.load_results(directory + '/TEMP.csv', 0)

gp.printGraph(EDA, HR, TEMP)

