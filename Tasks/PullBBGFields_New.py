import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from contextlib import suppress
from datetime import datetime
import re
from urllib.request import urlretrieve, urlopen, Request
import requests
from bs4 import BeautifulSoup
import xlrd
import openpyxl
import math

startTime = datetime.now()

#PURPOSE: CREATE EXCEL FILE WITH BLOOMBERG PULLS FOR annual DATA
#TYPICAL RUN-TIME: <20 SECONDS

#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------
#   FUNCTIONS
#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------

def CreateBBGPullFile(List_of_Tickers, basefilepath, sector, numperiods, columnFile, periodtype = 'Annual'):
    """Create an Excel File That Retrieves Fundamental Data for a list of companies"""
    Dict_Row = defaultdict(list)
    #Get Desired Columns for data base
    #FileForColumns = "BloombergData\Desired_BBG_Columns.csv"
    BBG_DesiredColumns = pd.read_csv(columnFile, sep = ',')
    BBG_Columns = np.array(BBG_DesiredColumns['Desired_BBG_Columns'])
    Headers = BBG_Columns
    periodtypestring=periodtype
    print(periodtype)
    if(periodtype == 'Annual'):
        periodtype = 'Y'
    else:
        periodtype = 'Q'

    #Create rows in DataFrame
    for ticker in List_of_Tickers:
        for i in range(0, numperiods):
            Dict_Row[str(str(i) + 'F' + periodtype + '_' + ticker)].append(ticker)
            Dict_Row[str(str(i) + 'F' + periodtype + '_' + ticker)].append(str('-' + str(i) + 'F'+ periodtype))
            #for field in BBG_Columns.items()
            for field in BBG_Columns:
                Dict_Row[str(str(i) + 'F' + periodtype + '_' + ticker)].append(str('=BDP(\"' + ticker + ' EQUITY\", \"' + field + '\", \"FA_ADJUSTED\", \"GAAP\", \"EQY_FUND_RELATIVE_PERIOD\", \"' + str('-' + str(i) + 'F' + periodtype) + '\")'))
    #Create DataFrame, must be transposed
    temp_df = pd.DataFrame(Dict_Row).T
    temp_df.columns = np.hstack(['Ticker', 'Relative Fiscal Period', Headers])

    if(periodtype == 'Q'):
        periodtypestring = 'Quarter'
    else:
        periodtypestring = 'Annual'

    #WriteExcelFile
    ExcelFile = basefilepath + 'BBG_' + sector + periodtypestring + '.xlsx'
    print(ExcelFile)
    writer = pd.ExcelWriter(ExcelFile)
    temp_df.to_excel(writer, 'Sheet1')
    writer.save()
    del Dict_Row


def CreateUpdateFile(ExistingDF, TickerList, Periods_to_Pull, Year_or_Quarterly = 'Y', filepathfor_Excel= "BloombergData\\", UpdateColumnsFile = "BloombergData\Desired_BBG_Columns.csv"):
    ExistingDF['LATEST_PERIOD_END_DT_FULL_RECORD'] = pd.to_datetime(ExistingDF['LATEST_PERIOD_END_DT_FULL_RECORD'], errors='coerce')   
    TickerList['MRQ'] = pd.to_datetime(TickerList['MRQ'], errors='coerce')   
    TickerList['MRY'] = pd.to_datetime(TickerList['MRY'], errors='coerce')   
    if(Year_or_Quarterly == 'Q'):
        temp_Original = ExistingDF[ExistingDF['Relative Fiscal Period'] == '-0FQ'].copy()
        periodtype='Quarterly'
    else:
        temp_Original = ExistingDF[ExistingDF['Relative Fiscal Period'] == '-0FY'].copy()
        periodtype = 'Annual'
    temp_Original = pd.merge(temp_Original, TickerList, how='left', on = 'Ticker')
    temp_Original['LATEST_PERIOD_END_DT_FULL_RECORD'] = temp_Original['LATEST_PERIOD_END_DT_FULL_RECORD'].fillna(0)
    temp_Original['MRQ'] = temp_Original['MRQ'].fillna(0)
    temp_Original['MRY'] = temp_Original['MRY'].fillna(0)
    if(Year_or_Quarterly == 'Q'):
        temp_Original['ComparePeriods'] = (temp_Original['MRQ'] == temp_Original['LATEST_PERIOD_END_DT_FULL_RECORD'])
    else:
        temp_Original['ComparePeriods'] = (temp_Original['MRY'] == temp_Original['LATEST_PERIOD_END_DT_FULL_RECORD'])
    Update = temp_Original[temp_Original['ComparePeriods'] == False]
    lenUpdate = len(Update['Ticker'].unique())
    CreateBBGPullFile(Update['Ticker'], filepathfor_Excel, 'Update', Periods_to_Pull[Year_or_Quarterly], UpdateColumnsFile, periodtype)
    return lenUpdate


def retrievefile(InputFileName, CalcFunction = 'Normal'):
    inputFile = InputFileName + '.xlsx'
    outputFile = InputFileName + '.csv'
    xl = pd.ExcelFile(inputFile)
    temp_df = xl.parse('Sheet1')
    temp_df = GC_Calculation_Columns(temp_df, CalcFunction)
    temp_df.to_csv(outputFile, sep = ',')
    return temp_df

def UpdateWithExcel(OriginalDFCSVFile, UpdatedExcelFile, CalcFunction = 'Normal'):
    xl = pd.ExcelFile(UpdatedExcelFile)
    temp_df = xl.parse('Sheet1')
    temp_df = GC_Calculation_Columns(temp_df, CalcFunction)
    updateList = temp_df['Ticker'].unique()
    temp_Original = pd.read_csv(OriginalDFCSVFile, sep = ',', index_col = 0)
    temp_Original[temp_Original['Ticker'].isin(updateList)] = np.nan
    temp_Original.update(temp_df)
    temp_Original.to_csv(OriginalDFCSVFile, sep = ',')
    
    
    
    
def GC_Calculation_Columns(temp_df, CalcFunction = 'Normal'):
    #EBITDA Calc: Differs from BBG EBITDA b/c mine starts w/ pre-tax income and backs out interest & D&A compared to BBG starts w/ operating profit and backs out D&A
    temp_df['InterestExpense'] = temp_df[['IS_NET_INTEREST_EXPENSE', 'IS_INT_EXPENSE', 'CF_ACT_CASH_PAID_FOR_INT_DEBT']].max(axis=1)
    temp_df['GC_EBITDA'] = temp_df['PRETAX_INC'] + temp_df['InterestExpense'] + temp_df['CF_DEPR_AMORT']
    #Adjusted EBITDA Calc: GC_EBITDA + Merger Related Expenses + Asset Disposal Costs + Extinguishment of Debt + Asset Write-Downs + Goodwill Impairment + Intangible Impairment + Sale of Business + Restructuring Expenses
    if(CalcFunction == 'REIT'):
        List_to_set = ['CF_EFFECT_FOREIGN_EXCHANGES','CF_NET_CASH_DISCONT_OPS_OPER', 'CF_OTHER_FINANCING_ACT_EXCL_FX', 'OTHER_INVESTING_ACT_DETAILED', 'NET_CHG_IN_LT_INVEST_DETAILED', 'CF_NET_CASH_DISCONTINUED_OPS_INV', 'CF_NET_CASH_DISCONTINUED_OPS_FIN', 'DISP_FXD_&_INTANGIBLES_DETAILED', 'CF_NT_CSH_RCVD_PD_FOR_ACQUIS_DIV', 'BS_CURR_RENTAL_EXPENSE', 'IS_MERGER_ACQUISITION_EXPENSE', 'IS_GAIN_LOSS_DISPOSAL_ASSETS', 'IS_IMPAIRMENT_ASSETS', 'IS_IMPAIRMENT_GOODWILL_INTANGIBL', 'IS_IMPAIR_OF_INTANG_ASSETS', 'IS_G_L_ON_EXT_DBT_OR_SETTLE_DBT', 'IS_SALE_OF_BUSINESS', 'IS_RESTRUCTURING_EXPENSES', 'CF_DISP_FIX_ASSET', 'CF_CAP_EXPEND_PRPTY_ADD', 'CF_PRPTY_IMPRV']
    else:
        List_to_set = ['CF_EFFECT_FOREIGN_EXCHANGES','CF_NET_CASH_DISCONT_OPS_OPER', 'CF_OTHER_FINANCING_ACT_EXCL_FX', 'OTHER_INVESTING_ACT_DETAILED', 'NET_CHG_IN_LT_INVEST_DETAILED', 'CF_NET_CASH_DISCONTINUED_OPS_INV', 'CF_NET_CASH_DISCONTINUED_OPS_FIN', 'DISP_FXD_&_INTANGIBLES_DETAILED', 'CF_NT_CSH_RCVD_PD_FOR_ACQUIS_DIV', 'BS_CURR_RENTAL_EXPENSE', 'IS_MERGER_ACQUISITION_EXPENSE', 'IS_GAIN_LOSS_DISPOSAL_ASSETS', 'IS_IMPAIRMENT_ASSETS', 'IS_IMPAIRMENT_GOODWILL_INTANGIBL', 'IS_IMPAIR_OF_INTANG_ASSETS', 'IS_G_L_ON_EXT_DBT_OR_SETTLE_DBT', 'IS_SALE_OF_BUSINESS', 'IS_RESTRUCTURING_EXPENSES']
    temp_df = SetListToZero(temp_df, List_to_set)
    temp_df['GC_ADJ_EBITDA'] = temp_df['GC_EBITDA'] + temp_df['IS_MERGER_ACQUISITION_EXPENSE'] + temp_df['IS_GAIN_LOSS_DISPOSAL_ASSETS'] + temp_df['IS_IMPAIRMENT_ASSETS'] + temp_df['IS_IMPAIRMENT_GOODWILL_INTANGIBL'] + temp_df['IS_IMPAIR_OF_INTANG_ASSETS'] + temp_df['IS_G_L_ON_EXT_DBT_OR_SETTLE_DBT'] + temp_df['IS_SALE_OF_BUSINESS']+ temp_df['IS_RESTRUCTURING_EXPENSES']
    temp_df['GC_EBITDAR'] = temp_df['GC_EBITDA'] + temp_df['BS_CURR_RENTAL_EXPENSE']
    temp_df['GC_ADJ_EBITDAR'] = temp_df['GC_ADJ_EBITDA'] + temp_df['BS_CURR_RENTAL_EXPENSE']
    temp_df['FCF_Impairments'] = temp_df['IS_IMPAIRMENT_GOODWILL_INTANGIBL'] + temp_df['IS_IMPAIRMENT_ASSETS'] + temp_df['IS_IMPAIR_OF_INTANG_ASSETS']
    temp_df['FCF_OtherCFfromOperations'] = temp_df['CF_CASH_FROM_OPER'] - (temp_df['GC_EBITDA'] + temp_df['InterestExpense'] - temp_df['IS_INC_TAX_EXP'] - temp_df['IS_TOT_CASH_PFD_DVD'] + temp_df['FCF_Impairments'] + temp_df['CF_NET_CASH_DISCONT_OPS_OPER'] + temp_df['CF_CHNG_NON_CASH_WORK_CAP'])
    if(CalcFunction == 'REIT'):
        temp_df['FCF_CapEx'] = temp_df['CF_PRPTY_IMPRV'] + temp_df['CF_CAP_EXPEND_PRPTY_ADD']
        temp_df['FCF_MaintenanceCapEx'] = temp_df['CF_PRPTY_IMPRV']
        temp_df['FCF_GrowthCapEx'] = temp_df['CF_CAP_EXPEND_PRPTY_ADD']
    else:
        temp_df['FCF_CapEx'] = temp_df['ACQUIS_FXD_&_INTANG_DETAILED']
    #Calculations to Get FCF: temp_df['GC_EBITDA'] + temp_df['InterestExpense'] - temp_df['IS_INC_TAX_EXP'] - temp_df['IS_TOT_CASH_PFD_DVD'] + temp_df['FCF_Impairments'] + temp_df['FCF_OtherCFfromOperations'] + temp_df['FCF_CapEx'] + temp_df['CF_CHNG_NON_CASH_WORK_CAP']

    if(CalcFunction == 'REIT'):
        temp_df['FCF_AcquisitionsAndDivestitures'] = temp_df['DISP_FXD_&_INTANGIBLES_DETAILED'] + temp_df['CF_NT_CSH_RCVD_PD_FOR_ACQUIS_DIV']+ temp_df['CF_DISP_FIX_ASSET']
    else:
        temp_df['FCF_AcquisitionsAndDivestitures'] = temp_df['DISP_FXD_&_INTANGIBLES_DETAILED'] + temp_df['CF_NT_CSH_RCVD_PD_FOR_ACQUIS_DIV']
    temp_df['FCF_OtherDiscontinued'] = temp_df['CF_NET_CASH_DISCONTINUED_OPS_INV'] + temp_df['CF_NET_CASH_DISCONTINUED_OPS_FIN']
    temp_df['FCF_OtherNonOperations'] = temp_df['NET_CHG_IN_LT_INVEST_DETAILED'] + temp_df['OTHER_INVESTING_ACT_DETAILED'] + temp_df['CF_OTHER_FINANCING_ACT_EXCL_FX']
    if(CalcFunction == 'REIT'):
        temp_df['FCF_OtherInvestingCF'] = temp_df['CF_CASH_FROM_INV_ACT'] - (temp_df['NET_CHG_IN_LT_INVEST_DETAILED'] + temp_df['OTHER_INVESTING_ACT_DETAILED'] + temp_df['ACQUIS_FXD_&_INTANG_DETAILED'] + temp_df['CF_NT_CSH_RCVD_PD_FOR_ACQUIS_DIV'] + temp_df['DISP_FXD_&_INTANGIBLES_DETAILED'] + temp_df['CF_NET_CASH_DISCONTINUED_OPS_INV'] + temp_df['CHANGE_IN_INVESTMENTS_REIT'] + temp_df['CHANGE_IN_NOTES_REIT'] + temp_df['CF_CHANGE_IN_LOANS'] + temp_df['DEC_INC_RE_INT'])
    else:
        temp_df['FCF_OtherInvestingCF'] = temp_df['CF_CASH_FROM_INV_ACT'] - (temp_df['NET_CHG_IN_LT_INVEST_DETAILED'] + temp_df['OTHER_INVESTING_ACT_DETAILED'] + temp_df['ACQUIS_FXD_&_INTANG_DETAILED'] + temp_df['CF_NT_CSH_RCVD_PD_FOR_ACQUIS_DIV'] + temp_df['DISP_FXD_&_INTANGIBLES_DETAILED'] + temp_df['CF_NET_CASH_DISCONTINUED_OPS_INV'])
    temp_df['FCF_OtherFinancingCF'] = temp_df['CFF_ACTIVITIES_DETAILED'] - (temp_df['CF_DVD_PAID'] + temp_df['PROC_FR_REPAYMNTS_BOR_DETAILED'] + temp_df['PROC_FR_REPURCH_EQTY_DETAILED'] + temp_df['CF_OTHER_FINANCING_ACT_EXCL_FX'] + temp_df['CF_NET_CASH_DISCONTINUED_OPS_FIN'])

    temp_df['FCF_ErrorCheck'] = temp_df['CF_NET_CHNG_CASH'] - (temp_df['GC_EBITDA'] + temp_df['InterestExpense'] - temp_df['IS_INC_TAX_EXP'] - temp_df['IS_TOT_CASH_PFD_DVD'] + temp_df['FCF_Impairments'] + temp_df['CF_NET_CASH_DISCONT_OPS_OPER'] + temp_df['CF_CHNG_NON_CASH_WORK_CAP'] + temp_df['FCF_OtherCFfromOperations'] + temp_df['FCF_CapEx'] + temp_df['FCF_AcquisitionsAndDivestitures'] + temp_df['FCF_OtherDiscontinued'] +temp_df['CF_DVD_PAID'] + temp_df['PROC_FR_REPAYMNTS_BOR_DETAILED'] + temp_df['PROC_FR_REPURCH_EQTY_DETAILED'] + temp_df['FCF_OtherNonOperations'] + temp_df['CF_EFFECT_FOREIGN_EXCHANGES'] + temp_df['FCF_OtherInvestingCF'] + temp_df['FCF_OtherFinancingCF'])
    temp_df['BroadErrorCheck'] = temp_df['CF_NET_CHNG_CASH'] - (temp_df['CF_CASH_FROM_OPER'] + temp_df['CF_CASH_FROM_INV_ACT'] + temp_df['CFF_ACTIVITIES_DETAILED'] + temp_df['CF_EFFECT_FOREIGN_EXCHANGES'])
    temp_df['FCF_ChangeInCash'] = temp_df['GC_EBITDA'] + temp_df['InterestExpense'] - temp_df['IS_INC_TAX_EXP'] - temp_df['IS_TOT_CASH_PFD_DVD'] + temp_df['FCF_Impairments'] + temp_df['FCF_OtherCFfromOperations'] + temp_df['FCF_CapEx'] + temp_df['CF_NET_CASH_DISCONT_OPS_OPER'] + temp_df['CF_CHNG_NON_CASH_WORK_CAP'] + temp_df['FCF_OtherCFfromOperations'] + temp_df['FCF_AcquisitionsAndDivestitures'] + temp_df['FCF_OtherDiscontinued'] + temp_df['CF_DVD_PAID'] + temp_df['PROC_FR_REPAYMNTS_BOR_DETAILED'] + temp_df['PROC_FR_REPURCH_EQTY_DETAILED'] + temp_df['FCF_OtherNonOperations'] + temp_df['CF_EFFECT_FOREIGN_EXCHANGES']

    temp_df['AdjustedFCF'] = temp_df['CF_CASH_FROM_OPER'] + temp_df['FCF_CapEx'] - temp_df['CF_NET_CASH_DISCONT_OPS_OPER']
    temp_df['FCF_TaxRate'] = 0.35
    temp_df['FCF_TaxBenefitOfInterest'] = temp_df['FCF_TaxRate'] * temp_df['InterestExpense']
    temp_df['UnleveragedFCF'] = temp_df['AdjustedFCF'] + temp_df['InterestExpense'] - temp_df['FCF_TaxBenefitOfInterest']


    temp_df['RentalExpenseToDebtMultiple'] = 8

    if(CalcFunction == 'REIT'):
        temp_df['AdjustedFCF_Maintenance'] = temp_df['CF_CASH_FROM_OPER'] + temp_df['FCF_MaintenanceCapEx'] - temp_df['CF_NET_CASH_DISCONT_OPS_OPER']
        temp_df['UnleveragedFCF_Maintenance'] = temp_df['AdjustedFCF'] + temp_df['InterestExpense'] - temp_df['FCF_TaxBenefitOfInterest']
        temp_df['TotalDebt'] = temp_df['SHORT_AND_LONG_TERM_DEBT']
        temp_df['TotalDebt_PensionAdj'] = temp_df['SHORT_AND_LONG_TERM_DEBT'] + temp_df['PENSION_LIABILITIES']
        temp_df['NetDebt_PensionAdj'] = temp_df['NET_DEBT'] + temp_df['PENSION_LIABILITIES']
        temp_df['TotalDebt_RentAdj'] = temp_df['SHORT_AND_LONG_TERM_DEBT'] + (temp_df['RentalExpenseToDebtMultiple']*temp_df['BS_CURR_RENTAL_EXPENSE'])
        temp_df['NetDebt_RentAdj'] = temp_df['NET_DEBT'] + (temp_df['RentalExpenseToDebtMultiple']*temp_df['BS_CURR_RENTAL_EXPENSE'])
        temp_df['TotalDebt_to_AdjEBITDAR'] = temp_df['TotalDebt_RentAdj'] / temp_df['GC_ADJ_EBITDAR']
        temp_df['NetDebt_to_AdjEBITDAR'] = temp_df['NetDebt_RentAdj'] / temp_df['GC_ADJ_EBITDAR']

        temp_df['TotalLeverage'] = temp_df['SHORT_AND_LONG_TERM_DEBT'] / temp_df['GC_EBITDA']
        temp_df['NetLeverage'] = temp_df['NET_DEBT'] / temp_df['GC_EBITDA']
        temp_df['TotalLeverageAdj'] = temp_df['SHORT_AND_LONG_TERM_DEBT'] / temp_df['GC_ADJ_EBITDA']
        temp_df['SecuredLeverageAdj'] = temp_df['BS_MORTGAGE_&_OTHER_SECURED_DEBT'] / temp_df['GC_ADJ_EBITDA']
        temp_df['NetLeverageAdj'] = temp_df['NET_DEBT'] / temp_df['GC_ADJ_EBITDA']
        temp_df['AdjEBITDA_to_Interest'] = temp_df['GC_ADJ_EBITDA'] / temp_df['InterestExpense']
        temp_df['TotalDebt_to_FCF'] = temp_df['SHORT_AND_LONG_TERM_DEBT'] / temp_df['AdjustedFCF']


    else:
        temp_df['TotalDebt'] = temp_df['BS_LT_BORROW'] + temp_df['BS_ST_BORROW']
        temp_df['TotalDebt_PensionAdj'] = temp_df['TotalDebt'] + temp_df['PENSION_LIABILITIES']
        temp_df['NetDebt_PensionAdj'] = temp_df['NET_DEBT'] + temp_df['PENSION_LIABILITIES']
        temp_df['TotalDebt_RentAdj'] = temp_df['TotalDebt'] + (temp_df['RentalExpenseToDebtMultiple']*temp_df['BS_CURR_RENTAL_EXPENSE'])
        temp_df['NetDebt_RentAdj'] = temp_df['NET_DEBT'] + (temp_df['RentalExpenseToDebtMultiple']*temp_df['BS_CURR_RENTAL_EXPENSE'])
        temp_df['TotalDebt_to_AdjEBITDAR'] = temp_df['TotalDebt_RentAdj'] / temp_df['GC_ADJ_EBITDAR']
        temp_df['NetDebt_to_AdjEBITDAR'] = temp_df['NetDebt_RentAdj'] / temp_df['GC_ADJ_EBITDAR']

        temp_df['TotalLeverage'] = temp_df['TotalDebt'] / temp_df['GC_EBITDA']
        temp_df['NetLeverage'] = temp_df['NET_DEBT'] / temp_df['GC_EBITDA']
        temp_df['TotalLeverageAdj'] = temp_df['TotalDebt'] / temp_df['GC_ADJ_EBITDA']
        temp_df['NetLeverageAdj'] = temp_df['NET_DEBT'] / temp_df['GC_ADJ_EBITDA']
        temp_df['AdjEBITDA_to_Interest'] = temp_df['GC_ADJ_EBITDA'] / temp_df['InterestExpense']
        temp_df['TotalDebt_to_FCF'] = temp_df['TotalDebt'] / temp_df['AdjustedFCF']

    temp_df['CFfromOps_to_NetIncome'] = temp_df['CF_CASH_FROM_OPER'] / temp_df['EARN_FOR_COMMON']
    temp_df['FCF_to_NetIncome']= temp_df['AdjustedFCF'] / temp_df['EARN_FOR_COMMON']
    temp_df['CapEx_to_AdjEBITDA']= -temp_df['FCF_CapEx'] / temp_df['GC_ADJ_EBITDA']
    temp_df['CapEx_to_Sales']= -temp_df['FCF_CapEx'] / temp_df['SALES_REV_TURN']

    if(CalcFunction == 'REIT'):
        temp_df['MaintenanceCapEx_to_AdjEBITDA']= -temp_df['FCF_CapExMaintenance'] / temp_df['GC_ADJ_EBITDA']
        temp_df['GrowthCapEx_to_AdjEBITDA']= -temp_df['FCF_CapExGrowth'] / temp_df['GC_ADJ_EBITDA']
   
    return(temp_df)


def GC_Calculation_Columns_REIT(temp_df):
    #EBITDA Calc: Differs from BBG EBITDA b/c mine starts w/ pre-tax income and backs out interest & D&A compared to BBG starts w/ operating profit and backs out D&A
    temp_df['InterestExpense'] = temp_df[['IS_NET_INTEREST_EXPENSE', 'IS_INT_EXPENSE', 'CF_ACT_CASH_PAID_FOR_INT_DEBT']].max(axis=1)
    temp_df['GC_EBITDA'] = temp_df['PRETAX_INC'] + temp_df['InterestExpense'] + temp_df['CF_DEPR_AMORT']
    #Adjusted EBITDA Calc: GC_EBITDA + Merger Related Expenses + Asset Disposal Costs + Extinguishment of Debt + Asset Write-Downs + Goodwill Impairment + Intangible Impairment + Sale of Business + Restructuring Expenses
    temp_df = SetListToZero(temp_df, List_to_set)
    temp_df['GC_ADJ_EBITDA'] = temp_df['GC_EBITDA'] + temp_df['IS_MERGER_ACQUISITION_EXPENSE'] + temp_df['IS_GAIN_LOSS_DISPOSAL_ASSETS'] + temp_df['IS_IMPAIRMENT_ASSETS'] + temp_df['IS_IMPAIRMENT_GOODWILL_INTANGIBL'] + temp_df['IS_IMPAIR_OF_INTANG_ASSETS'] + temp_df['IS_G_L_ON_EXT_DBT_OR_SETTLE_DBT'] + temp_df['IS_SALE_OF_BUSINESS']+ temp_df['IS_RESTRUCTURING_EXPENSES']
    temp_df['GC_EBITDAR'] = temp_df['GC_EBITDA'] + temp_df['BS_CURR_RENTAL_EXPENSE']
    temp_df['GC_ADJ_EBITDAR'] = temp_df['GC_ADJ_EBITDA'] + temp_df['BS_CURR_RENTAL_EXPENSE']
    temp_df['FCF_Impairments'] = temp_df['IS_IMPAIRMENT_GOODWILL_INTANGIBL'] + temp_df['IS_IMPAIRMENT_ASSETS'] + temp_df['IS_IMPAIR_OF_INTANG_ASSETS']
    temp_df['FCF_OtherCFfromOperations'] = temp_df['CF_CASH_FROM_OPER'] - (temp_df['GC_EBITDA'] + temp_df['InterestExpense'] - temp_df['IS_INC_TAX_EXP'] - temp_df['IS_TOT_CASH_PFD_DVD'] + temp_df['FCF_Impairments'] + temp_df['CF_NET_CASH_DISCONT_OPS_OPER'] + temp_df['CF_CHNG_NON_CASH_WORK_CAP'])
    temp_df['FCF_CapEx'] = temp_df['CF_PRPTY_IMPRV'] + temp_df['CF_CAP_EXPEND_PRPTY_ADD']
    temp_df['FCF_MaintenanceCapEx'] = temp_df['CF_PRPTY_IMPRV']
    temp_df['FCF_GrowthCapEx'] = temp_df['CF_CAP_EXPEND_PRPTY_ADD']
    #Calculations to Get FCF: temp_df['GC_EBITDA'] + temp_df['InterestExpense'] - temp_df['IS_INC_TAX_EXP'] - temp_df['IS_TOT_CASH_PFD_DVD'] + temp_df['FCF_Impairments'] + temp_df['FCF_OtherCFfromOperations'] + temp_df['FCF_CapEx'] + temp_df['CF_CHNG_NON_CASH_WORK_CAP']

    temp_df['FCF_AcquisitionsAndDivestitures'] = temp_df['DISP_FXD_&_INTANGIBLES_DETAILED'] + temp_df['CF_NT_CSH_RCVD_PD_FOR_ACQUIS_DIV']+ temp_df['CF_DISP_FIX_ASSET']
    temp_df['FCF_OtherDiscontinued'] = temp_df['CF_NET_CASH_DISCONTINUED_OPS_INV'] + temp_df['CF_NET_CASH_DISCONTINUED_OPS_FIN']
    temp_df['FCF_OtherNonOperations'] = temp_df['NET_CHG_IN_LT_INVEST_DETAILED'] + temp_df['OTHER_INVESTING_ACT_DETAILED'] + temp_df['CF_OTHER_FINANCING_ACT_EXCL_FX']
    temp_df['FCF_OtherInvestingCF'] = temp_df['CF_CASH_FROM_INV_ACT'] - (temp_df['NET_CHG_IN_LT_INVEST_DETAILED'] + temp_df['OTHER_INVESTING_ACT_DETAILED'] + temp_df['ACQUIS_FXD_&_INTANG_DETAILED'] + temp_df['CF_NT_CSH_RCVD_PD_FOR_ACQUIS_DIV'] + temp_df['DISP_FXD_&_INTANGIBLES_DETAILED'] + temp_df['CF_NET_CASH_DISCONTINUED_OPS_INV'] + temp_df['CHANGE_IN_INVESTMENTS_REIT'] + temp_df['CHANGE_IN_NOTES_REIT'] + temp_df['CF_CHANGE_IN_LOANS'] + temp_df['DEC_INC_RE_INT'])
    temp_df['FCF_OtherFinancingCF'] = temp_df['CFF_ACTIVITIES_DETAILED'] - (temp_df['CF_DVD_PAID'] + temp_df['PROC_FR_REPAYMNTS_BOR_DETAILED'] + temp_df['PROC_FR_REPURCH_EQTY_DETAILED'] + temp_df['CF_OTHER_FINANCING_ACT_EXCL_FX'] + temp_df['CF_NET_CASH_DISCONTINUED_OPS_FIN'])

    temp_df['FCF_ErrorCheck'] = temp_df['CF_NET_CHNG_CASH'] - (temp_df['GC_EBITDA'] + temp_df['InterestExpense'] - temp_df['IS_INC_TAX_EXP'] - temp_df['IS_TOT_CASH_PFD_DVD'] + temp_df['FCF_Impairments'] + temp_df['CF_NET_CASH_DISCONT_OPS_OPER'] + temp_df['CF_CHNG_NON_CASH_WORK_CAP'] + temp_df['FCF_OtherCFfromOperations'] + temp_df['FCF_CapEx'] + temp_df['FCF_AcquisitionsAndDivestitures'] + temp_df['FCF_OtherDiscontinued'] +temp_df['CF_DVD_PAID'] + temp_df['PROC_FR_REPAYMNTS_BOR_DETAILED'] + temp_df['PROC_FR_REPURCH_EQTY_DETAILED'] + temp_df['FCF_OtherNonOperations'] + temp_df['CF_EFFECT_FOREIGN_EXCHANGES'] + temp_df['FCF_OtherInvestingCF'] + temp_df['FCF_OtherFinancingCF'])
    temp_df['BroadErrorCheck'] = temp_df['CF_NET_CHNG_CASH'] - (temp_df['CF_CASH_FROM_OPER'] + temp_df['CF_CASH_FROM_INV_ACT'] + temp_df['CFF_ACTIVITIES_DETAILED'] + temp_df['CF_EFFECT_FOREIGN_EXCHANGES'])
    temp_df['FCF_ChangeInCash'] = temp_df['GC_EBITDA'] + temp_df['InterestExpense'] - temp_df['IS_INC_TAX_EXP'] - temp_df['IS_TOT_CASH_PFD_DVD'] + temp_df['FCF_Impairments'] + temp_df['FCF_OtherCFfromOperations'] + temp_df['FCF_CapEx'] + temp_df['CF_NET_CASH_DISCONT_OPS_OPER'] + temp_df['CF_CHNG_NON_CASH_WORK_CAP'] + temp_df['FCF_OtherCFfromOperations'] + temp_df['FCF_AcquisitionsAndDivestitures'] + temp_df['FCF_OtherDiscontinued'] + temp_df['CF_DVD_PAID'] + temp_df['PROC_FR_REPAYMNTS_BOR_DETAILED'] + temp_df['PROC_FR_REPURCH_EQTY_DETAILED'] + temp_df['FCF_OtherNonOperations'] + temp_df['CF_EFFECT_FOREIGN_EXCHANGES']

    temp_df['AdjustedFCF'] = temp_df['CF_CASH_FROM_OPER'] + temp_df['FCF_CapEx'] - temp_df['CF_NET_CASH_DISCONT_OPS_OPER']
    temp_df['AdjustedFCF_Maintenance'] = temp_df['CF_CASH_FROM_OPER'] + temp_df['FCF_MaintenanceCapEx'] - temp_df['CF_NET_CASH_DISCONT_OPS_OPER']
    temp_df['FCF_TaxRate'] = 0.35
    temp_df['FCF_TaxBenefitOfInterest'] = temp_df['FCF_TaxRate'] * temp_df['InterestExpense']
    temp_df['UnleveragedFCF'] = temp_df['AdjustedFCF'] + temp_df['InterestExpense'] - temp_df['FCF_TaxBenefitOfInterest']
    temp_df['UnleveragedFCF_Maintenance'] = temp_df['AdjustedFCF'] + temp_df['InterestExpense'] - temp_df['FCF_TaxBenefitOfInterest']

    temp_df['RentalExpenseToDebtMultiple'] = 8
    temp_df['TotalDebt'] = temp_df['SHORT_AND_LONG_TERM_DEBT']
    temp_df['TotalDebt_PensionAdj'] = temp_df['SHORT_AND_LONG_TERM_DEBT'] + temp_df['PENSION_LIABILITIES']
    temp_df['NetDebt_PensionAdj'] = temp_df['NET_DEBT'] + temp_df['PENSION_LIABILITIES']
    temp_df['TotalDebt_RentAdj'] = temp_df['SHORT_AND_LONG_TERM_DEBT'] + (temp_df['RentalExpenseToDebtMultiple']*temp_df['BS_CURR_RENTAL_EXPENSE'])
    temp_df['NetDebt_RentAdj'] = temp_df['NET_DEBT'] + (temp_df['RentalExpenseToDebtMultiple']*temp_df['BS_CURR_RENTAL_EXPENSE'])
    temp_df['TotalDebt_to_AdjEBITDAR'] = temp_df['TotalDebt_RentAdj'] / temp_df['GC_ADJ_EBITDAR']
    temp_df['NetDebt_to_AdjEBITDAR'] = temp_df['NetDebt_RentAdj'] / temp_df['GC_ADJ_EBITDAR']

    temp_df['TotalLeverage'] = temp_df['SHORT_AND_LONG_TERM_DEBT'] / temp_df['GC_EBITDA']
    temp_df['NetLeverage'] = temp_df['NET_DEBT'] / temp_df['GC_EBITDA']
    temp_df['TotalLeverageAdj'] = temp_df['SHORT_AND_LONG_TERM_DEBT'] / temp_df['GC_ADJ_EBITDA']
    temp_df['SecuredLeverageAdj'] = temp_df['BS_MORTGAGE_&_OTHER_SECURED_DEBT'] / temp_df['GC_ADJ_EBITDA']
    temp_df['NetLeverageAdj'] = temp_df['NET_DEBT'] / temp_df['GC_ADJ_EBITDA']
    temp_df['AdjEBITDA_to_Interest'] = temp_df['GC_ADJ_EBITDA'] / temp_df['InterestExpense']
    temp_df['TotalDebt_to_FCF'] = temp_df['SHORT_AND_LONG_TERM_DEBT'] / temp_df['AdjustedFCF']
    

    temp_df['CFfromOps_to_NetIncome'] = temp_df['CF_CASH_FROM_OPER'] / temp_df['EARN_FOR_COMMON']
    temp_df['FCF_to_NetIncome']= temp_df['AdjustedFCF'] / temp_df['EARN_FOR_COMMON']
    temp_df['CapEx_to_AdjEBITDA']= -temp_df['FCF_CapEx'] / temp_df['GC_ADJ_EBITDA']
    temp_df['CapEx_to_Sales']= -temp_df['FCF_CapEx'] / temp_df['SALES_REV_TURN']
    return(temp_df)


def SetListToZero(temp_df, list_to_set):
    for i in list_to_set:
        if(i in temp_df.columns):
            temp_df[i] = temp_df[i].astype(float)
            temp_df[i] = temp_df[i].replace('None', 0)
            temp_df[i] = temp_df[i].fillna(0)
            
    return temp_df

def Update_Step1(QuarterOrAnnual = 'Annual',
                 AnnualFile = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedAnnual.csv", QuarterFile = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedQuarterly.csv",
                 AnnualColumns = "C:\\Users\\gcole\\Documents\\BloombergData\Desired_BBG_Columns.csv", QuarterColumns = "C:\\Users\\gcole\\Documents\\BloombergData\Desired_BBG_Columns_Quarterly.csv",
                 FileForTickers = "C:\\Users\\gcole\\Documents\\BloombergData\TickerList.xlsx", filepathfor_Excel = "C:\\Users\\gcole\\Documents\\BloombergData\\"):

    print(QuarterOrAnnual)
    Periods_to_Pull = {'Y':10, 'Q':12}
    #Load TickersList
    xl_Tickers = pd.ExcelFile(FileForTickers)
    TickersList = xl_Tickers.parse('Sheet1')
    TickersList['MRQ'] = pd.to_datetime(TickersList['MRQ'], errors='coerce')
    TickersList['MRY'] = pd.to_datetime(TickersList['MRY'], errors='coerce')
    if(QuarterOrAnnual == 'Annual'):
        ExistingDF = pd.read_csv(AnnualFile, sep = ',', index_col = 0)
        ExistingDF['LATEST_PERIOD_END_DT_FULL_RECORD'] = pd.to_datetime(ExistingDF['LATEST_PERIOD_END_DT_FULL_RECORD'], errors='coerce')
        YorQ = 'Y'
        lenUpdate = CreateUpdateFile(ExistingDF, TickersList, Periods_to_Pull, Year_or_Quarterly = YorQ, filepathfor_Excel = filepathfor_Excel, UpdateColumnsFile = AnnualColumns)
        print('After loading Annual update file in Bloomberg, run \"Update_Step2\"')
    else:
        ExistingDF = pd.read_csv(QuarterFile, sep = ',', index_col = 0)
        ExistingDF['LATEST_PERIOD_END_DT_FULL_RECORD'] = pd.to_datetime(ExistingDF['LATEST_PERIOD_END_DT_FULL_RECORD'], errors='coerce')
        YorQ = 'Q'
        lenUpdate = CreateUpdateFile(ExistingDF, TickersList, Periods_to_Pull, Year_or_Quarterly = YorQ, filepathfor_Excel = filepathfor_Excel, UpdateColumnsFile = QuarterColumns)
        print('After loading Quarter update file in Bloomberg, run \"Update_Step2\"')
    return lenUpdate

def Update_Step2(QuarterOrAnnual = 'Annual',
                 AnnualFile = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedAnnual.csv", QuarterFile = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedQuarterly.csv",
                 AnnualUpdateFile = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_UpdateAnnual.xlsx", QuarterUpdateFile = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_UpdateQuarter.xlsx"):
    if(QuarterOrAnnual == 'Annual'):
        UpdateWithExcel(AnnualFile, AnnualUpdateFile)
    else:
        UpdateWithExcel(QuarterFile, QuarterUpdateFile)

def MergeNewCompanies(OriginalFileAnnual, NewAnnualFile, OriginalFileQuarter, NewQuarterFile, CalcFunction = 'Normal'):
    
    def MergeCompanyData(OriginalFile, NewFile, CalcFunction = 'Normal'):    
        xl = pd.ExcelFile(NewFile)
        temp_df = xl.parse('Sheet1')
        temp_df = GC_Calculation_Columns(temp_df, CalcFunction)
        print(temp_df.head())
        temp_Original = pd.read_csv(OriginalFile, sep = ',', index_col = 0)
        temp_Original = temp_Original.append(temp_df)
        temp_Original.to_csv(OriginalFile, sep = ',')
        print(temp_Original[temp_Original['Ticker']=='APU US'])
        
    
    MergeCompanyData(OriginalFileAnnual, NewAnnualFile)
    MergeCompanyData(OriginalFileQuarter, NewQuarterFile)
    
        

#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------
#   CODE
#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------
print("To update data, run Update_Step1(), base periods are Annual, change to QuarterOrAnnual = \"Quarter\" to find updates for the quarter")
print("After updating the excel files, run Update_Step2() with the same instructions as above")


Dict_Row = defaultdict(list)
Dates = []
ColumnNames = []
filepathfor_Excel = "BloombergData\\"
#FileForColumns = "BloombergData\Desired_BBG_Columns.csv"
FileForColumns = "BloombergData\Desired_BBG_Columns_Quarterly.csv"
Year_or_Quarterly = 'Y'
Periods_to_Pull = {'Y':10, 'Q':12}
#Periods_to_Pull = {'Y':4, 'Q':6}

#Get Ticker List
FileForTickers = "BloombergData\TickerList.xlsx"
FileToCheckForUpdates = "BloombergData\\BBG_CombinedQuarterly.csv"
UpdateFile = "BloombergData\\BBG_UpdateQuarter.xlsx"
#FileForTickers = "BloombergData\TSWHoldings.xlsx"
#FileForTickers = "BloombergData\TickerList_New.xlsx"
#xl_Tickers = pd.ExcelFile(FileForTickers)
#TickersList = xl_Tickers.parse('Sheet1')
#TickersList = TickersList.head(506)
CalculationFunctionDict = {'Normal':'GC_Calculation_Columns', 'REIT':'GC_Calculation_Columns_REIT'}



#Need to Retreive:
#Utilities
#Financials

#listfortickers = TickersList[TickersList['GICS_SECTOR_NAME'] == 'Industrials']['Ticker']


#SectorDict = {'REIT':{ 'listfortickers': TickersList[(TickersList['GICS_SECTOR_NAME'] == 'Real Estate') | (TickersList['GICS_INDUSTRY_NAME'] == 'Mortgage Real Estate Investmen')]['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns_Quarterly_REIT.csv"}}
#SectorDict = {'NewHoldings':{ 'listfortickers': TickersList[(TickersList['GICS_SECTOR_NAME'] != 'Financials') &(TickersList['GICS_SECTOR_NAME'] != 'Real Estate') & (TickersList['GICS_SECTOR_NAME'] != 'Utilities')]['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns_Quarterly.csv"}}
#SectorDict = {'WPSHoldings':{ 'listfortickers': TickersList[(TickersList['GICS_SECTOR_NAME'] != 'Financials') &(TickersList['GICS_SECTOR_NAME'] != 'Real Estate') & (TickersList['GICS_SECTOR_NAME'] != 'Utilities')]['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns_Quarterly.csv"}}
#SectorDict = {'NewEnergy':{ 'listfortickers': TickersList['Ticker'].tail(4), 'Column_File':"BloombergData\Desired_BBG_Columns.csv"}}
#SectorDict = {'Materials':{ 'listfortickers': TickersList[TickersList['GICS_SECTOR_NAME'] == 'Materials']['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns_Quarterly.csv"}}
#SectorDict = {'Industrials':{ 'listfortickers': TickersList[TickersList['GICS_SECTOR_NAME'] == 'Industrials']['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns.csv"},
#        'HealthCare':{ 'listfortickers': TickersList[TickersList['GICS_SECTOR_NAME'] == 'Health Care']['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns.csv"},
#        'Materials':{ 'listfortickers': TickersList[TickersList['GICS_SECTOR_NAME'] == 'Materials']['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns.csv"},
#        'Telecom':{ 'listfortickers': TickersList[TickersList['GICS_SECTOR_NAME'] == 'Telecommunication Services']['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns.csv"},
#        'InformationTechnology':{ 'listfortickers': TickersList[TickersList['GICS_SECTOR_NAME'] == 'Information Technology']['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns.csv"},
#        'Energy':{ 'listfortickers': TickersList[TickersList['GICS_SECTOR_NAME'] == 'Energy']['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns.csv"},
#        'ConsumerStaples':{ 'listfortickers': TickersList[TickersList['GICS_SECTOR_NAME'] == 'Consumer Staples']['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns.csv"},
#        'ConsumerDiscretionary':{ 'listfortickers': TickersList[TickersList['GICS_SECTOR_NAME'] == 'Consumer Discretionary']['Ticker'], 'Column_File':"BloombergData\Desired_BBG_Columns.csv"}}

#NEED TO GET COLUMNS LIST FOR:
    #FINANCIALS
    #UTILITIES


#Standard Create File to Pull BBG Data
#for key, values in SectorDict.items():
#    CreateBBGPullFile(SectorDict[key]['listfortickers'], filepathfor_Excel, key, Periods_to_Pull[Year_or_Quarterly], SectorDict[key]['Column_File'], Year_or_Quarterly)


#Create File to Update Data
#ExistingDF = pd.read_csv(FileToCheckForUpdates, sep = ',', index_col = 0)
#CreateUpdateFile(ExistingDF, TickersList, Year_or_Quarterly, filepathfor_Excel, Periods_to_Pull)

#Update Data
#UpdateWithExcel(FileToCheckForUpdates, UpdateFile)




#print(test[['Ticker', 'MRY', 'LATEST_PERIOD_END_DT_FULL_RECORD', 'ComparePeriods']].head())


print(datetime.now() - startTime)


    

