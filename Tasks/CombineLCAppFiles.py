import numpy as np
import pandas as pd
from datetime import datetime
import os
import re


#This Combines All Initial Lending Club Data
#Typical Run Time: 4 minutes

def TestGetFiles(BaseDir = 'C:/Users/gcole/Documents/LendingClub/CleanedLCData/'):
    ListOfFiles = []
    for file in os.listdir(BaseDir):
        if re.match('LCStats\d{4}.+\.csv', file) is not None:
            ListOfFiles.append(os.path.join(BaseDir, file))
    print(ListOfFiles)


def CombineFiles(BaseDir = 'C:/Users/gcole/Documents/LendingClub/CleanedLCData/'):
    startTime = datetime.now()
    ListOfFiles = []
    for file in os.listdir(BaseDir):
        if re.match('LCStats\d{4}.{,}\.csv', file) is not None:
            ListOfFiles.append(os.path.join(BaseDir, file))
    #AppData = pd.read_csv(FileOpen, sep = ',', encoding = 'latin-1')
    #InitialDF = pd.read_csv(FileOpen, sep=',', na_values=['Nothing'], nrows = 1)
    FullFile_df = pd.DataFrame()
    TempFile_df = pd.DataFrame()

    for files in ListOfFiles :
        #print(files)
        TempFile_df = pd.read_csv(files, sep=',', na_values=['Nothing'], index_col ='id', encoding = 'latin-1')
        FullFile_df = pd.concat([FullFile_df, TempFile_df])

    AllFiles = BaseDir + 'LCStatsAll.csv'
    
    FullFile_df.to_csv(AllFiles, sep= ',')
    print(datetime.now() - startTime)
