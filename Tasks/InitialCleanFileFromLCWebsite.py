import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import tree
from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression
from datetime import datetime


def LCCleanFile(FileOpen):
    #FileOpen = 'LCStats2016Q3.csv'
    #AppData = pd.read_csv(FileOpen, sep = ',', encoding = 'latin-1')
    InitialDF = pd.read_csv(FileOpen, sep=',', na_values=['Nothing'], nrows = 1)
    StringOfCell = str(InitialDF.iloc[0].index.values)
    print(InitialDF.iloc[0].index.values)
    print(type(StringOfCell))
    print(StringOfCell)

    if 'Prospectus' in StringOfCell:
        print('Contains Prospectus text')
        AppData = pd.read_csv(FileOpen, sep=',', skiprows= [0], na_values=['Nothing'], index_col ='id')
        AppData.drop(AppData.index[-2:], inplace = True)
        AppData.to_csv(FileOpen, sep = ',')
    else:
        print('File works')


