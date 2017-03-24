import numpy as np
import pandas as pd
from datetime import datetime
import datetime as dt
import re


#PURPOSE:
#   To Convert LC Data Files to Useable Files with IRR information

#Typical Run Time: 

#TO DO LIST
#   Figure Out Loan Purpose dictionary
#   Convert ZIP & State to MSA
#   Convert State to Integer
#   Convert negative credit history lengths' earliest credit history to 19xx instead of 20xx

#Assign filename: file
def ProcessCombinedFiles(ApplicationDataLocation = 'C:/Users/gcole/Documents/LendingClub/CleanedLCData/LCStatsAll.csv', OutputFile = 'C:/Users/gcole/Documents/LendingClub/CleanedLCData/LCStatsAll_Cleaned.csv', WPS_OutputFile = 'C:/Users/gcole/Documents/LendingClub/CleanedLCData/LCStatsAll_WPS_Cleaned.csv', minimal_data_limit = 0.5):
    startTime = datetime.now()
    #import file: data
    AppData = pd.read_csv(ApplicationDataLocation, sep = ',', na_values=['Nothing'], index_col ='id', parse_dates = True, encoding = 'latin-1')

    AppData = AppData[[x for x in AppData.columns if not re.search('^Unnamed',x)]]
    Divide_By_Income = ['avg_cur_bal', 'bc_open_to_buy', 'funded_amnt', 'installment', 'revol_bal', 'tot_cur_bal', 'tot_hi_cred_lim', 'total_bal_ex_mort', 'total_bc_limit', 'total_il_high_credit_limit', 'total_rev_hi_lim']
    ToGetDummies = ['grade', 'home_ownership', 'pymnt_plan', 'verification_status',]

    minimal_data = []
    for i in AppData.columns:
        pct_nan = AppData[i].isnull().sum() / len(AppData[i])
        if (pct_nan >= minimal_data_limit):
            minimal_data.append(i)
            
    AppData = AppData[list(set(AppData.columns) - set(minimal_data))]
    #Making Dates for Issue Date Usable
    AppData['Begin']= AppData['issue_d'].str.extract(r'(^\w+)')
    AppData['End']= AppData['issue_d'].str.extract(r'(\w+$)')
    AppData['Month'] = np.where(AppData['Begin'].str.contains(r'^\D'),AppData['Begin'],AppData['End'])
    AppData['Year'] = np.where(AppData['Begin'].str.contains(r'^\d'),np.where(AppData['Begin'].str.contains(r'\d{4}'),AppData['Begin'].str.extract(r'(\d{2}$)'),AppData['Begin']),np.where(AppData['End'].str.contains(r'\d{4}'),AppData['End'].str.extract(r'(\d{2}$)'),AppData['End']))
    AppData['Year'] = AppData.Year.map(int)
    AppData['Year'] = AppData.Year.map("{:02}".format)
    AppData['test'] = AppData.Month + '-' + AppData.Year.map(str)
    AppData['issue_d'] = pd.to_datetime(AppData['test'], format = '%b-%y')
    AppData.drop(['Begin', 'End', 'Month', 'Year', 'test'], inplace = True, axis = 1)

    #Making Dates for Earliest Credit Line Usable
    AppData['Begin']= AppData['earliest_cr_line'].str.extract(r'(^\w+)')
    AppData['End']= AppData['earliest_cr_line'].str.extract(r'(\w+$)')
    AppData['Month'] = np.where(AppData['Begin'].str.contains(r'^\D'),AppData['Begin'],AppData['End'])
    AppData['Year'] = np.where(AppData['Begin'].str.contains(r'^\d'),np.where(AppData['Begin'].str.contains(r'\d{4}'),AppData['Begin'].str.extract(r'(\d{2}$)'),AppData['Begin']),np.where(AppData['End'].str.contains(r'\d{4}'),AppData['End'].str.extract(r'(\d{2}$)'),AppData['End']))
    AppData['Year'] = AppData.Year.map(int)
    AppData['Year'] = AppData.Year.map("{:02}".format)
    AppData['test'] = AppData.Month + '-' + AppData.Year.map(str)
    AppData['earliest_cr_line'] = pd.to_datetime(AppData['test'], format = '%b-%y')
    AppData.drop(['Begin', 'End', 'Month', 'Year', 'test'], inplace = True, axis = 1)

    #Remove ' months' from term
    AppData['term'] = AppData['term'].str.replace(r'\D+', '').astype('int')
    #convert interest rate to a number
    AppData['int_rate'] = AppData['int_rate'].str.replace(r'\%+', '').astype('float')
    #Remove 'non numbers' from employment length
    AppData['emp_length'] = AppData['emp_length'].str.replace(r'\D+', '')
    #Remove xx's from zip code
    AppData['zip_code'] = AppData['zip_code'].str.replace(r'\D+', '')
    #Create Length of Credit History
    AppData['Length_CR_Hist'] = ((AppData['issue_d'] - AppData['earliest_cr_line']) / np.timedelta64(1, 'D')).astype(int)
    #convert Revolving Utilization to a number
    AppData['revol_util'] = AppData['revol_util'].str.replace(r'\%+', '').astype('float')

    #Create AdjDTI = (Current DTI * Monthly Income + LC Loan Payment) / Monthly Income 
    AppData['AdjDTI'] = ((AppData['dti']/100) * (AppData['annual_inc'] / 12) + AppData['installment']) / (AppData['annual_inc'] / 12)
    #Current Debt to Gross Income (Includes Funded LC Loan)
    AppData['Curr_Debt_to_Gross_Inc'] = (AppData['tot_cur_bal'] + AppData['funded_amnt'])*100 / AppData['annual_inc']
    #Worst Debt to Gross Income (Includes Funded LC Loan)
    AppData['Worst_Debt_to_Gross_Inc'] = (AppData['tot_cur_bal'] + AppData['funded_amnt'] + (AppData['tot_hi_cred_lim'] - AppData['total_bal_ex_mort']))*100 / AppData['annual_inc']
    
    for item in Divide_By_Income:
        colname = item + '_DivIncome'
        AppData[colname] = AppData[item] / AppData['annual_inc']
    
    #Vintage by Year & YearMonth
    AppData['YearVintage'] = AppData['issue_d'].dt.year
    AppData['YearMonthVintage'] = AppData['issue_d'].dt.strftime('%Y%m')
    
    for item in ToGetDummies:
        temp_df = pd.get_dummies(AppData[item], prefix = item)
        del AppData[item]
        AppData = AppData.join(temp_df)
        del temp_df
    
    AppData.to_csv(OutputFile, sep = ',')
    
    WPSData = AppData[['emp_title']]
    WPSData.to_csv(WPS_OutputFile, sep=',')
    RunTime = (datetime.now() - startTime).total_seconds()
    return RunTime
