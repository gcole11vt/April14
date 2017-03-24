import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from contextlib import suppress
from datetime import datetime

#This File looks throught the PaymentHistory File and calculates chargeoff & recovery rate
#Typical Run Time: 45 seconds
#Note, Loading the file takes ~45 seconds
#This File works properly
    #Key Assumptions
        #Charge-Offs = Recovery = last payment
        #Currently Late = $0 last payment
        #Current = Ending Balance Last Payment
        
        

def ChargeOffs(PaymentHistoryFile = 'C:/Users/gcole/Documents/LendingClub/PaymentHistoryData/PaymentHistoryData_Raw_Investor.csv', BaseFileDirectory = 'C:/Users/gcole/Documents/LendingClub/PaymentHistoryData/', testing = False):
    startTime = datetime.now()

    fields = ['LOAN_ID', 'PERIOD_END_LSTAT', 'MOB', 'PBAL_BEG_PERIOD_INVESTORS', 'PCO_RECOVERY_INVESTORS']
    if(testing == True):
        data = pd.read_csv(PaymentHistoryFile, sep = ',', na_values=['Nothing'], usecols=fields, nrows = 1000)
    else:
        data = pd.read_csv(PaymentHistoryFile, sep = ',', na_values=['Nothing'], usecols=fields)
    ChargedOff_subset = data['PERIOD_END_LSTAT'] == 'Charged Off'
    df_ChargedOff = data.loc[ChargedOff_subset]
    df_ChargedOff.index = df_ChargedOff['LOAN_ID']
    del df_ChargedOff['LOAN_ID']
    df_ChargedOff['PCO_RECOVERY_INVESTORS'].fillna(0, inplace = True)
    df_ChargedOff['Recovery_Rate'] = df_ChargedOff['PCO_RECOVERY_INVESTORS'] / df_ChargedOff['PBAL_BEG_PERIOD_INVESTORS']
    MeanChargeOff = df_ChargedOff['Recovery_Rate'].mean()
    MedianChargeOff = df_ChargedOff['Recovery_Rate'].median()
    df_ChargeOffFile = df_ChargedOff[['MOB', 'Recovery_Rate']]
    FileForCSV = BaseFileDirectory + 'ChargeOffResults.csv'
    df_ChargeOffFile.to_csv(FileForCSV, sep = ',')
    RunTime = (datetime.now() - startTime).total_seconds()
    return (MeanChargeOff, MedianChargeOff, RunTime)
