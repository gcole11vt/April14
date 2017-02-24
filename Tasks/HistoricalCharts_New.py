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
from IPython.display import display
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import matplotlib.ticker as tickermatplot
from xlsxwriter.utility import xl_rowcol_to_cell
from matplotlib.backends.backend_pdf import PdfPages
from IPython.display import display, HTML

startTime = datetime.now()

#PURPOSE: CREATE PEER GROUP OUTPUT FOR INDUSTRIES
#Note: Titles don't work if import seaborn
#TYPICAL RUN-TIME: 

#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------
#   FUNCTIONS
#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------

#Creating empty dataframes to make the base functions work
df_all = pd.DataFrame()
df_allq = pd.DataFrame()
df_allLTM = pd.DataFrame()
TickersList = pd.DataFrame()

def trimDF(temp_df):
    """Cleans Columns for CF Waterfall Plot"""
    Desired_Columns = ['CF_NET_CHNG_CASH', 'FCF_ErrorCheck', 'FCF_OtherDiscontinued', 'CF_NET_CASH_DISCONT_OPS_OPER', 'FCF_OtherNonOperations', 'FCF_OtherInvestingCF', 'FCF_OtherFinancingCF', 'UnleveragedFCF', 'InterestExpense', 'FCF_TaxBenefitOfInterest', 'PROC_FR_REPURCH_EQTY_DETAILED', 'CF_DVD_PAID', 'PROC_FR_REPAYMNTS_BOR_DETAILED', 'FCF_AcquisitionsAndDivestitures', 'CF_EFFECT_FOREIGN_EXCHANGES']
    #print(temp_df[Desired_Columns])
    sum_row = pd.DataFrame(data=temp_df[Desired_Columns].sum()).T.reindex(columns = temp_df.columns)
    test = temp_df['LATEST_PERIOD_END_DT_FULL_RECORD'].max()
    sum_row.ix[0, 'Ticker'] = temp_df.iloc[0]['Ticker']
    sum_row.ix[0, 'LATEST_PERIOD_END_DT_FULL_RECORD'] = test
    sum_row.ix[0, 'Relative Fiscal Period'] = temp_df.iloc[0]['Relative Fiscal Period']
    #print(sum_row.ix[0, 'LATEST_PERIOD_END_DT_FULL_RECORD'])
    #print(sum_row)
    return sum_row

def getLTM(QuarterDF, AnnualDF, CalcFunction = 'Normal'):
    """ Calculates LTM Data for a company """
    temp_df = QuarterDF
    if(CalcFunction == 'REIT'):
        ColumnsToSet = ['C&CE_AND_STI_DETAILED', 'BS_ACCT_NOTE_RCV', 'BS_INVENTORIES', 'BS_CUR_ASSET_REPORT', 'BS_NET_FIX_ASSET', 'BS_GROSS_FIX_ASSET', 'BS_ACCUM_DEPR', 'BS_LT_INVEST', 'BS_DISCLOSED_INTANGIBLES', 'BS_TOT_ASSET', 'ACCT_PAYABLE_&_ACCRUALS_DETAILED', 'BS_ST_BORROW', 'BS_CUR_LIAB', 'BS_LT_BORROW', 'PENSION_LIABILITIES', 'BS_TOT_LIAB2', 'BS_PFD_EQY', 'EQTY_BEF_MINORITY_INT_DETAILED', 'MINORITY_NONCONTROLLING_INTEREST', 'TOTAL_EQUITY', 'TOT_LIAB_AND_EQY', 'NET_DEBT', 'BS_SH_OUT', 'CASH_CONVERSION_CYCLE', 'NUM_OF_EMPLOYEES','SHORT_AND_LONG_TERM_DEBT', 'IS_SQUARE_GLA', 'IS_NUMBER_OF_PROPERTIES']
    else:
        ColumnsToSet = ['C&CE_AND_STI_DETAILED', 'BS_ACCT_NOTE_RCV', 'BS_INVENTORIES', 'BS_CUR_ASSET_REPORT', 'BS_NET_FIX_ASSET', 'BS_GROSS_FIX_ASSET', 'BS_ACCUM_DEPR', 'BS_LT_INVEST', 'BS_DISCLOSED_INTANGIBLES', 'BS_TOT_ASSET', 'ACCT_PAYABLE_&_ACCRUALS_DETAILED', 'BS_ST_BORROW', 'BS_CUR_LIAB', 'BS_LT_BORROW', 'PENSION_LIABILITIES', 'BS_TOT_LIAB2', 'BS_PFD_EQY', 'EQTY_BEF_MINORITY_INT_DETAILED', 'MINORITY_NONCONTROLLING_INTEREST', 'TOTAL_EQUITY', 'TOT_LIAB_AND_EQY', 'NET_DEBT', 'BS_SH_OUT', 'CASH_CONVERSION_CYCLE', 'NUM_OF_EMPLOYEES']

    IncomePeriods = 4
    BalanceSheetPeriods = 5
    #temp_df.dropna(subset=['FCF_ErrorCheck'])
    (AverageAssets, AverageCommon, AverageTangibleAssets) = getBSaverageLTM(temp_df)
    temp_df.sort_values(by='LATEST_PERIOD_END_DT_FULL_RECORD', inplace=True, ascending = True)
    BS_df = temp_df
    mylist = [col for col in temp_df.select_dtypes(include=['float64']).columns if col not in ColumnsToSet]
    for i in mylist:
        temp_df[i] = temp_df.groupby('Ticker')[i].apply(lambda x:x.rolling(center=False, window=IncomePeriods).sum())
    temp_df.sort_values(by='LATEST_PERIOD_END_DT_FULL_RECORD', inplace=True, ascending = False)
    return temp_df
    



def getBSaverageLTM(temp_df):
    temp_df = temp_df[temp_df['LATEST_PERIOD_END_DT_FULL_RECORD'].isin(temp_df['LATEST_PERIOD_END_DT_FULL_RECORD'].nlargest(5))]
    AverageAssets = temp_df['BS_TOT_ASSET'].mean()
    temp_df['CommonEquity'] = temp_df['TOTAL_EQUITY'] - temp_df['BS_PFD_EQY'] - temp_df['MINORITY_NONCONTROLLING_INTEREST']
    AverageCommon = temp_df['CommonEquity'].mean()
    AverageTangibleAssets = temp_df['TangibleAssets'].mean()    
    return AverageAssets, AverageCommon, AverageTangibleAssets

def ChartStatistic(temp_df, DesiredColumn, pdf_pages, LabelColumn = 'Ticker', SortByColumn = True, SortAscending = False, Title = True, LabelFormat = "%.1f", Show = True, SavePDF = False):
    """Creates a Chart of Historical Data """
    fig = plt.figure(frameon=False)
    fig.set_size_inches(11.69,8.27)
    if (SortByColumn == True):
        SortByColumn = DesiredColumn
    if (Title == True):
        Title = DesiredColumn
    else:
        Title = Title + ' - ' + DesiredColumn
    temp_df.sort_values(by=SortByColumn, inplace=True, ascending = SortAscending)
    my_plot = temp_df[DesiredColumn].plot(kind='bar', legend=None, title=Title, color="blue")
    my_plot.set_xticklabels(temp_df[LabelColumn])
    if (temp_df[LabelColumn].dtype == 'datetime64[ns]'):
        ticklabels = [item.strftime('%b %Y') if not pd.isnull(item) else '' for item in temp_df[LabelColumn]]
        #ticklabels = [item.strftime('%b %Y') for item in temp_df[LabelColumn]]
        my_plot.xaxis.set_major_formatter(tickermatplot.FixedFormatter(ticklabels))
        plt.gcf().autofmt_xdate()
    
    my_plot.spines['top'].set_visible(False)
    my_plot.spines['right'].set_visible(False)
    my_plot.xaxis.set_ticks_position('bottom')
    my_plot.axhline(y=temp_df[DesiredColumn].median(), color = 'lightgrey')
    my_plot.axhline(y=0, color = 'black')
    for p in my_plot.patches:
        if(p.get_y())<0:
            my_plot.annotate(LabelFormat % -p.get_height(), (p.get_x() + p.get_width() / 2., -p.get_height()), ha = 'center', va = 'center', xytext=(0,-10), textcoords = 'offset points')
        else:
            my_plot.annotate(LabelFormat % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext=(0,10), textcoords = 'offset points')
    plt.tight_layout()
    if(Show == True):
        plt.show()
    if(SavePDF == True):
        pdf_pages.savefig()
    plt.close()



def ChartStackedStatistic(temp_df, DesiredColumn, pdf_pages, LabelColumn = 'Ticker', SortByColumn = True, SortAscending = False, Title = True, LabelFormat = "%.1f", Show = True, SavePDF = False):
    """Create a stacked statistic chart"""
    fig = plt.figure(frameon=False)
    fig.set_size_inches(11.69,8.27)
    if (SortByColumn == True):
        SortByColumn = DesiredColumn
    if (Title == True):
        Title = DesiredColumn
    else:
        Title = Title + ' - ' + DesiredColumn
    temp_df.sort_values(by=SortByColumn, inplace=True, ascending = SortAscending)
    #Need to reduce df to only included columns, date & ticker
    #my_plot = temp_df[['C&CE_AND_STI_DETAILED', 'BS_ACCT_NOTE_RCV', 'BS_INVENTORIES', 'BS_CUR_ASSET_REPORT', 'BS_NET_FIX_ASSET', 'BS_GROSS_FIX_ASSET', 'BS_ACCUM_DEPR', 'BS_LT_INVEST', 'BS_DISCLOSED_INTANGIBLES']].plot(kind='bar', stacked=True)
    



def SetLTMBalanceSheetData(LTMDF, CalcFunction = 'Normal'):
    """Sets LTM Balance Sheet to most recent period's statistic"""
    LTMDF['RentalExpenseToDebtMultiple'] = 8
    if(CalcFunction == 'REIT'):
        LTMDF['AdjustedFCF_Maintenance'] = LTMDF['CF_CASH_FROM_OPER'] + LTMDF['FCF_MaintenanceCapEx'] - LTMDF['CF_NET_CASH_DISCONT_OPS_OPER']
        LTMDF['UnleveragedFCF_Maintenance'] = LTMDF['AdjustedFCF'] + LTMDF['InterestExpense'] - LTMDF['FCF_TaxBenefitOfInterest']
        LTMDF['TotalDebt'] = LTMDF['SHORT_AND_LONG_TERM_DEBT']
        LTMDF['TotalDebt_PensionAdj'] = LTMDF['SHORT_AND_LONG_TERM_DEBT'] + LTMDF['PENSION_LIABILITIES']
        LTMDF['NetDebt_PensionAdj'] = LTMDF['NET_DEBT'] + LTMDF['PENSION_LIABILITIES']
        LTMDF['TotalDebt_RentAdj'] = LTMDF['SHORT_AND_LONG_TERM_DEBT'] + (LTMDF['RentalExpenseToDebtMultiple']*LTMDF['BS_CURR_RENTAL_EXPENSE'])
        LTMDF['NetDebt_RentAdj'] = LTMDF['NET_DEBT'] + (LTMDF['RentalExpenseToDebtMultiple']*LTMDF['BS_CURR_RENTAL_EXPENSE'])
        LTMDF['TotalDebt_to_AdjEBITDAR'] = LTMDF['TotalDebt_RentAdj'] / LTMDF['GC_ADJ_EBITDAR']
        LTMDF['NetDebt_to_AdjEBITDAR'] = LTMDF['NetDebt_RentAdj'] / LTMDF['GC_ADJ_EBITDAR']

        LTMDF['TotalLeverage'] = LTMDF['SHORT_AND_LONG_TERM_DEBT'] / LTMDF['GC_EBITDA']
        LTMDF['NetLeverage'] = LTMDF['NET_DEBT'] / LTMDF['GC_EBITDA']
        LTMDF['TotalLeverageAdj'] = LTMDF['SHORT_AND_LONG_TERM_DEBT'] / LTMDF['GC_ADJ_EBITDA']
        LTMDF['SecuredLeverageAdj'] = LTMDF['BS_MORTGAGE_&_OTHER_SECURED_DEBT'] / LTMDF['GC_ADJ_EBITDA']
        LTMDF['NetLeverageAdj'] = LTMDF['NET_DEBT'] / LTMDF['GC_ADJ_EBITDA']
        LTMDF['AdjEBITDA_to_Interest'] = LTMDF['GC_ADJ_EBITDA'] / LTMDF['InterestExpense']
        LTMDF['TotalDebt_to_FCF'] = LTMDF['SHORT_AND_LONG_TERM_DEBT'] / LTMDF['AdjustedFCF']
    else:
        LTMDF['TotalDebt'] = LTMDF['BS_LT_BORROW'] + LTMDF['BS_ST_BORROW']
        LTMDF['TotalDebt_PensionAdj'] = LTMDF['TotalDebt'] + LTMDF['PENSION_LIABILITIES']
        LTMDF['NetDebt_PensionAdj'] = LTMDF['NET_DEBT'] + LTMDF['PENSION_LIABILITIES']
        LTMDF['TotalDebt_RentAdj'] = LTMDF['TotalDebt'] + (LTMDF['RentalExpenseToDebtMultiple']*LTMDF['BS_CURR_RENTAL_EXPENSE'])
        LTMDF['NetDebt_RentAdj'] = LTMDF['NET_DEBT'] + (LTMDF['RentalExpenseToDebtMultiple']*LTMDF['BS_CURR_RENTAL_EXPENSE'])
        LTMDF['TotalDebt_to_AdjEBITDAR'] = LTMDF['TotalDebt_RentAdj'] / LTMDF['GC_ADJ_EBITDAR']
        LTMDF['NetDebt_to_AdjEBITDAR'] = LTMDF['NetDebt_RentAdj'] / LTMDF['GC_ADJ_EBITDAR']

        LTMDF['TotalLeverage'] = LTMDF['TotalDebt'] / LTMDF['GC_EBITDA']
        LTMDF['NetLeverage'] = LTMDF['NET_DEBT'] / LTMDF['GC_EBITDA']
        LTMDF['TotalLeverageAdj'] = LTMDF['TotalDebt'] / LTMDF['GC_ADJ_EBITDA']
        LTMDF['NetLeverageAdj'] = LTMDF['NET_DEBT'] / LTMDF['GC_ADJ_EBITDA']
        LTMDF['AdjEBITDA_to_Interest'] = LTMDF['GC_ADJ_EBITDA'] / LTMDF['InterestExpense']
        LTMDF['TotalDebt_to_FCF'] = LTMDF['TotalDebt'] / LTMDF['AdjustedFCF']

    LTMDF['EBITDA_to_Interest'] = LTMDF['GC_ADJ_EBITDA'] / LTMDF['InterestExpense']
    LTMDF['UnleveragedFCF_to_Interest'] = LTMDF['UnleveragedFCF'] / LTMDF['InterestExpense']

    LTMDF['CFfromOps_to_NetIncome'] = LTMDF['CF_CASH_FROM_OPER'] / LTMDF['EARN_FOR_COMMON']
    LTMDF['FCF_to_NetIncome']= LTMDF['AdjustedFCF'] / LTMDF['EARN_FOR_COMMON']
    LTMDF['CapEx_to_AdjEBITDA']= -LTMDF['FCF_CapEx'] / LTMDF['GC_ADJ_EBITDA']
    LTMDF['CapEx_to_Sales']= -LTMDF['FCF_CapEx'] / LTMDF['SALES_REV_TURN']
    LTMDF['EBITDA_Margin'] = LTMDF['GC_ADJ_EBITDA'] *100 / LTMDF['SALES_REV_TURN']
    LTMDF['Adj_EBITDA_Margin'] = LTMDF['GC_EBITDA'] *100 / LTMDF['SALES_REV_TURN']
    LTMDF['BBG_EBITDA_Margin'] = LTMDF['EBITDA'] *100 / LTMDF['SALES_REV_TURN']
    if(CalcFunction == 'Normal'):
        LTMDF['Gross_Margin'] = LTMDF['GROSS_PROFIT'] *100 / LTMDF['SALES_REV_TURN']
    LTMDF['TangibleAssets'] = LTMDF['BS_TOT_ASSET'] - LTMDF['BS_DISCLOSED_INTANGIBLES']
    LTMDF['TangibleAsset_Coverage'] = LTMDF['TangibleAssets'] * 100 / LTMDF['TotalDebt']

    if(CalcFunction == 'REIT'):
        LTMDF['MaintenanceCapEx_to_AdjEBITDA']= -LTMDF['FCF_MaintenanceCapEx'] / LTMDF['GC_ADJ_EBITDA']
        LTMDF['GrowthCapEx_to_AdjEBITDA']= -LTMDF['FCF_GrowthCapEx'] / LTMDF['GC_ADJ_EBITDA']

    return LTMDF

def ChartHistoricalData(tickers, AnnualDF, QuarterDF, LTMDF, DesiredColumn, pdf_pages, IncludeLTM = True, LabelFormat = "%.1f", Show = True, SavePDF = False):
    """Function to Chart Historical Data and Use Either Only Annual Data or Annual + LTM Data"""
    AnnualDF = AnnualDF[AnnualDF['Ticker'] == tickers]
    if (IncludeLTM == True):
        QuarterDF = QuarterDF[QuarterDF['Ticker'] == tickers]
        AnnualDF = AnnualDF.append(LTMDF[LTMDF['Ticker'] == tickers].ix[0,])
    if(ColumnFormatting[DesiredColumn]['ChartType'] == 'Normal'):
        ChartStatistic(AnnualDF, DesiredColumn, pdf_pages, LabelColumn = 'LATEST_PERIOD_END_DT_FULL_RECORD', SortByColumn = 'LATEST_PERIOD_END_DT_FULL_RECORD', SortAscending = True, Title = tickers, LabelFormat = LabelFormat, Show = Show, SavePDF = SavePDF)
        
def CalculateMargins(temp_df, CalcFunction= 'Normal'):
    """Create Calculations That Are Not Done in the Base File"""
    temp_df = temp_df.replace('#N/A Field Not Applicable', np.nan)
    #temp_df['LATEST_PERIOD_END_DT_FULL_RECORD'] = temp_df['LATEST_PERIOD_END_DT_FULL_RECORD'].apply(pd.to_datetime(coerce = True))
    temp_df['LATEST_PERIOD_END_DT_FULL_RECORD'] = pd.to_datetime(temp_df['LATEST_PERIOD_END_DT_FULL_RECORD'], errors='coerce')
    temp_df['IS_DILUTED_EPS'] = temp_df['IS_DILUTED_EPS'].astype(float)
    temp_df['BS_DISCLOSED_INTANGIBLES'] = temp_df['BS_DISCLOSED_INTANGIBLES'].fillna(0)
    temp_df['EBITDA_Margin'] = temp_df['GC_EBITDA'] *100 / temp_df['SALES_REV_TURN']
    temp_df['Adj_EBITDA_Margin'] = temp_df['GC_ADJ_EBITDA'] *100 / temp_df['SALES_REV_TURN']
    temp_df['BBG_EBITDA_Margin'] = temp_df['EBITDA'] *100 / temp_df['SALES_REV_TURN']
    if(CalcFunction == 'Normal'):
        temp_df['Gross_Margin'] = temp_df['GROSS_PROFIT'] *100 / temp_df['SALES_REV_TURN']
    temp_df['EBITDA_to_Interest'] = temp_df['GC_ADJ_EBITDA'] / temp_df['InterestExpense']
    temp_df['UnleveragedFCF_to_Interest'] = temp_df['UnleveragedFCF'] / temp_df['InterestExpense']
    temp_df['TangibleAssets'] = temp_df['BS_TOT_ASSET'] - temp_df['BS_DISCLOSED_INTANGIBLES']
    temp_df['TangibleAsset_Coverage'] = temp_df['TangibleAssets'] * 100 / temp_df['TotalDebt']
    temp_df['CommonEquity'] = temp_df['TOTAL_EQUITY'] - temp_df['BS_PFD_EQY'] - temp_df['MINORITY_NONCONTROLLING_INTEREST']
    return temp_df
                        
def money(x, pos):
    return "${:,.0f}".format(x)

def CreateMarketValueColumns(temp_df):
    temp_df['EV_to_EBITDA_GC_Adj'] = temp_df['CURR_ENTP_VAL'] / temp_df['GC_ADJ_EBITDA']
    temp_df['Forward_EV_to_EBITDA_GC_Adj'] = temp_df['CURR_ENTP_VAL'] / temp_df['BEST_EBITDA']
    temp_df['Price_to_EPS_LTM'] = temp_df['PX_LAST'] / temp_df['IS_DILUTED_EPS']
    temp_df['Price_to_EPS_NTM'] = temp_df['PX_LAST'] / temp_df['BEST_EPS']
    #temp_df['Est_EPS_Growth'] = (temp_df['BEST_EPS'] / temp_df['IS_DILUTED_EPS'] - 1) * 100
    temp_df['Est_EBITDA_Growth'] = (temp_df['BEST_EBITDA'] / temp_df['GC_ADJ_EBITDA'] - 1) * 100
    return temp_df

def SaveOutputToExcel(temp_df, AnnualDF, fileName, sheetName):
    ColumnFormatting = DictionaryOfChartFormats()
    

    if('SALES_REV_TURN' in temp_df.columns):
        temp_df.sort_values(by='SALES_REV_TURN', inplace=True, ascending = False)
    writer = pd.ExcelWriter(fileName, engine='xlsxwriter', datetime_format = 'mmm yyyy')
    temp_df.to_excel(writer, index=False, sheet_name= sheetName)
    workbook = writer.book
    worksheet = writer.sheets[sheetName]
    money_fmt = workbook.add_format({'num_format': '$#,##0', 'bold':True})
    for number, i in enumerate(temp_df.columns):
        #print(str(i) + str(number))
        #worksheet.set_column(number, number, 18, money_fmt)
        if(ColumnFormatting[i]['ExcelFormat'] != 'none'):
            worksheet.set_column(number, number, ColumnFormatting[i]['ExcelWidth'],workbook.add_format({'num_format':ColumnFormatting[i]['ExcelFormat']}))
    writer.save()
    

def DictionaryOfChartFormats():
    #'Ticker', 'LATEST_PERIOD_END_DT_FULL_RECORD'
    ColumnFormattingDict = {'SALES_REV_TURN':{ 'SortAscending': False, 'LabelFormat' : "%.0f", 'ExcelWidth':20, 'ExcelFormat':'#,##0_);(#,##0)', 'ChartType':'Normal'},
        'SalesGrowth':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'BS_TOT_ASSET':{ 'SortAscending': False, 'LabelFormat' : "%.0f", 'ExcelWidth':20, 'ExcelFormat':'#,##0_);(#,##0)', 'ChartType':'Normal'},
        'BS_Stacked':{ 'SortAscending': False, 'LabelFormat' : "%.0f", 'ExcelWidth':20, 'ExcelFormat':'#,##0_);(#,##0)', 'ChartType':'Stacked'},
        'IS_NUMBER_OF_PROPERTIES':{ 'SortAscending': False, 'LabelFormat' : "%.0f", 'ExcelWidth':20, 'ExcelFormat':'#,##0_);(#,##0)', 'ChartType':'Normal'},
        'IS_SQUARE_GLA':{ 'SortAscending': False, 'LabelFormat' : "%.0f", 'ExcelWidth':20, 'ExcelFormat':'#,##0_);(#,##0)', 'ChartType':'Normal'},
        'ROA':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'UnleveragedFCFROA':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'UnleveragedFCFROTA':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'Gross_Margin':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'EBITDAGrowth':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'GC_ADJ_EBITDA':{ 'SortAscending': False, 'LabelFormat' : "%.0f", 'ExcelWidth':20, 'ExcelFormat':'#,##0_);(#,##0)', 'ChartType':'Normal'},
        'ROTA':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'ROCE':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'TangibleAsset_Coverage':{ 'SortAscending': False, 'LabelFormat' : "%.0f", 'ExcelWidth':20, 'ExcelFormat':'#,##0_);(#,##0)', 'ChartType':'Normal'},
        'Adj_EBITDA_Margin':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'TotalLeverage':{ 'SortAscending': True, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'TotalLeverageAdj':{ 'SortAscending': True, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'NetLeverage':{ 'SortAscending': True, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'NetLeverageAdj':{ 'SortAscending': True, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'CF_FFO':{ 'SortAscending': False, 'LabelFormat' : "%.0f", 'ExcelWidth':20, 'ExcelFormat':'#,##0_);(#,##0)', 'ChartType':'Normal'},
        'FFOGrowth':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'AFFOGrowth':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'EBITDA_to_Interest':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'CapEx_to_AdjEBITDA':{ 'SortAscending': True, 'LabelFormat' : "%.2f", 'ExcelWidth':20, 'ExcelFormat':'0%', 'ChartType':'Normal'},
        'MaintenanceCapEx_to_AdjEBITDA':{ 'SortAscending': True, 'LabelFormat' : "%.2f", 'ExcelWidth':20, 'ExcelFormat':'0%', 'ChartType':'Normal'},
        'GrowthCapEx_to_AdjEBITDA':{ 'SortAscending': True, 'LabelFormat' : "%.2f", 'ExcelWidth':20, 'ExcelFormat':'0%', 'ChartType':'Normal'},                            
        'EV_to_EBITDA_GC_Adj':{ 'SortAscending': True, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'Forward_EV_to_EBITDA_GC_Adj':{ 'SortAscending': True, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'Est_EBITDA_Growth':{ 'SortAscending': True, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'Price_to_EPS_NTM':{ 'SortAscending': True, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'EQY_DVD_YLD_IND':{ 'SortAscending': True, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'CURRENT_TRR_1YR':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'#,##0.0_);(#,##0.0)', 'ChartType':'Normal'},
        'Ticker':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'none', 'ChartType':'Normal'},
        'LATEST_PERIOD_END_DT_FULL_RECORD':{ 'SortAscending': False, 'LabelFormat' : "%.1f", 'ExcelWidth':20, 'ExcelFormat':'mmm/yyyy', 'ChartType':'Normal'},}


    #ChartStatistic(temp_df, chart, LabelColumn = 'Ticker', SortByColumn = True, SortAscending = False, Title = True, LabelFormat = "%.1f")
    #ColumnsForChart = ['SALES_REV_TURN', 'SalesGrowth', 'BS_TOT_ASSET', 'ROA', 'ROCE', 'TangibleAsset_Coverage', 'Adj_EBITDA_Margin', 'TotalLeverage', 'NetLeverage', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA', 'EV_to_EBITDA_GC_Adj', 'Price_to_EPS_NTM', 'EQY_DVD_YLD_IND', 'CURRENT_TRR_1YR']
    return ColumnFormattingDict

def CalculateAnnualStats(tickers, AnnualDF):
    AnnualDF = AnnualDF[AnnualDF['Ticker'] == tickers]
    AnnualDF.sort_values(by='LATEST_PERIOD_END_DT_FULL_RECORD', inplace=True, ascending = False)
    
def CreateAverageBalanceSheet(temp_df, PeriodsToAverage, CalcFunction = 'Normal'):
    temp_df.sort_values(by='LATEST_PERIOD_END_DT_FULL_RECORD', inplace=True, ascending = True)
    temp_df['AverageAssets'] = temp_df.groupby('Ticker')['BS_TOT_ASSET'].apply(lambda x:x.rolling(center=False, window=PeriodsToAverage).mean())
    temp_df['AverageTangibleAssets'] = temp_df.groupby('Ticker')['TangibleAssets'].apply(lambda x:x.rolling(center=False, window=PeriodsToAverage).mean())
    temp_df['AverageEquity'] = temp_df.groupby('Ticker')['TOTAL_EQUITY'].apply(lambda x:x.rolling(center=False, window=PeriodsToAverage).mean())
    temp_df['AverageCommonEquity'] = temp_df.groupby('Ticker')['CommonEquity'].apply(lambda x:x.rolling(center=False, window=PeriodsToAverage).mean())
    temp_df['ROCE'] = temp_df['EARN_FOR_COMMON'] * 100 / temp_df['AverageCommonEquity']
    temp_df['ROA'] = temp_df['NET_INCOME'] * 100 / temp_df['AverageAssets']
    temp_df['ROTA'] = temp_df['NET_INCOME'] * 100 / temp_df['AverageTangibleAssets']
    temp_df['SalesGrowth'] = temp_df.groupby('Ticker')['SALES_REV_TURN'].pct_change(PeriodsToAverage-1)*100
    temp_df['EBITDAGrowth'] = temp_df.groupby('Ticker')['GC_ADJ_EBITDA'].pct_change(PeriodsToAverage-1)*100
    temp_df['EPSGrowth'] = temp_df.groupby('Ticker')['IS_DILUTED_EPS'].pct_change(PeriodsToAverage-1)*100
    if(CalcFunction == 'REIT'):
        temp_df['FFOGrowth'] = temp_df.groupby('Ticker')['CF_FFO'].pct_change(PeriodsToAverage-1)*100
        temp_df['AFFOGrowth'] = temp_df.groupby('Ticker')['ADJUSTED_FUNDS_FROM_OPERATIONS'].pct_change(PeriodsToAverage-1)*100
    temp_df['UnleveragedFCFROA'] = temp_df['UnleveragedFCF'] * 100 / temp_df['AverageAssets']
    temp_df['UnleveragedFCFROTA'] = temp_df['UnleveragedFCF'] * 100 / temp_df['AverageTangibleAssets']
    temp_df.sort_values(by='LATEST_PERIOD_END_DT_FULL_RECORD', inplace=True, ascending = False)
    return temp_df


def MassProduceHistoricalCharts(AnnualDF, QuarterDF, LTMDF, tickerList, SectorName, BaseFileSaveLocation, ListofTickersThatDontWork, AllColumns, ChartColumns, ColumnFormatting = DictionaryOfChartFormats(), IncludeLTM = False, SavePDF = False):
    for tickers in tickerList:
        if not (tickers in ListofTickersThatDontWork):
            #InitialCodeForFile = re.sub(r'*',"",tickers)
            ExcelSheet = re.sub(r'[\W " "]',"", SectorName) + '_' + re.sub(r'/',"_", tickers)
            PDF_toSave = BaseFileSaveLocation + ExcelSheet + '.pdf'
            pdf_pages = PdfPages(PDF_toSave)
            for chart in ChartColumns:
                ChartHistoricalData(tickers, AnnualDF, QuarterDF, LTMDF, chart, pdf_pages, IncludeLTM = IncludeLTM, LabelFormat = ColumnFormatting[chart]['LabelFormat'], Show = False, SavePDF = SavePDF)
                #Note: LTM Data created in "ChartHistoricalData"
            pdf_pages.close()
            print(ExcelSheet)

def MassProducePeerGroups(AnnualDF, QuarterDF, LTMDF, tickerList, MarketDataDF, SectorName, BaseFileSaveLocation, ListofTickersThatDontWork, AllColumns, ChartColumns, ColumnFormatting = DictionaryOfChartFormats(), SavePDF = False, OutputToExcel = False, Writer = 'none'):
    LTM_df = pd.DataFrame()
    for tickers in tickerList:
        if not (tickers in ListofTickersThatDontWork):
            LTM_df = LTM_df.append(LTMDF[LTMDF['Ticker'] == tickers].ix[0,])

    LTM_df.sort_values(by='SALES_REV_TURN', inplace=True, ascending = False)
    LTM_df = pd.merge(LTM_df, MarketDataDF, on='Ticker')
    LTM_df = CreateMarketValueColumns(LTM_df)
    temp_AnnualDF =  CreateMarketValueColumns(pd.merge(AnnualDF[(AnnualDF['Ticker'].isin(tickerList)) & (AnnualDF['Relative Fiscal Period']== '-0FY')], MarketDataDF, on='Ticker'))
    temp_AnnualDF = temp_AnnualDF[['Ticker', 'LATEST_PERIOD_END_DT_FULL_RECORD'] + ChartColumns]
    temp_df = LTM_df[['Ticker', 'LATEST_PERIOD_END_DT_FULL_RECORD'] + ChartColumns]
    ExcelSheet = re.sub(r'[\W " "]',"", SectorName)
    PDF_toSave = BaseFileSaveLocation + ExcelSheet + '.pdf'
    Excel_toSave = BaseFileSaveLocation + SectorName +'.xlsx'
    pdf_pages = PdfPages(PDF_toSave)
    for chart in ChartColumns:
        if(ColumnFormatting[chart]['ChartType'] == 'Normal'):
            ChartStatistic(temp_df, chart, pdf_pages, LabelColumn = 'Ticker', SortByColumn = True, SortAscending = ColumnFormatting[chart]['SortAscending'], Title = True, LabelFormat = ColumnFormatting[chart]['LabelFormat'], Show= False, SavePDF = SavePDF)     
    if(OutputToExcel == True):
        SaveOutputToExcel(temp_df, temp_AnnualDF, Excel_toSave, ExcelSheet)
    pdf_pages.close()
    print(ExcelSheet)
    
def MarketDataSectorCharts(LTM_df, MarketDataDF, ChartColumns, SavePDF = False, ColumnFormatting = DictionaryOfChartFormats(), LabelColumn = 'GICS_INDUSTRY_NAME'):
    CalcItem = ['np.mean', 'np.median']
    LTM_df.sort_values(by='SALES_REV_TURN', inplace=True, ascending = False)
    LTM_df = pd.merge(LTM_df, MarketDataDF, on ='Ticker')
    LTM_df = CreateMarketValueColumns(LTM_df)
    LTM_df =  LTM_df[LTM_df['Relative Fiscal Period'] == '-0FQ']
    for chart in ChartColumns:
        GroupedDF = LTM_df.groupby(LabelColumn).agg({chart: ['np.median']})
        my_plot = GroupedDF.sort(columns=chart, ascending = False).plot(kind='bar', legend=None, title = chart)
        plt.tight_layout()
        plt.show()
        

def LoadFiles(AnnualDataFile =  "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedAnnual.csv", QuarterDataFile = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedQuarterly.csv", SecondDataSet = False, SecondAnnualDataFile = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_TSWHoldingsAnnual.csv", SecondQuarterDataFile = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_TSWHoldingsQuarterABBR.csv", TickerFile = "C:\\Users\\gcole\\Documents\\BloombergData\\TickerList.xlsx", CalcFunction = 'Normal'):
    """Load Necessary Data To Run All Other Parts of Script
    If you are loading a second set of data, use SecondDataSet = True and the Files are SecondAnnualDataFile and SecondQuarterDataFile
    CalcFunction Options ---> 'Normal', 'REIT'"""

    #Retrieve Data
    df_all = pd.read_csv(AnnualDataFile, sep=',', index_col=0)
    df_all['LATEST_PERIOD_END_DT_FULL_RECORD'] = pd.to_datetime(df_all['LATEST_PERIOD_END_DT_FULL_RECORD'], coerce = True)
    df_allq = pd.read_csv(QuarterDataFile, sep = ',', index_col = 0)
    df_allq['LATEST_PERIOD_END_DT_FULL_RECORD'] = pd.to_datetime(df_allq['LATEST_PERIOD_END_DT_FULL_RECORD'], coerce = True)
    
    if (SecondDataSet == True):
        df_allSecond = pd.read_csv(SecondAnnualDataFile, sep=',', index_col=0)
        df_allSecond['LATEST_PERIOD_END_DT_FULL_RECORD'] = pd.to_datetime(df_allSecond['LATEST_PERIOD_END_DT_FULL_RECORD'], coerce = True)
        df_allqSecond = pd.read_csv(SecondQuarterDataFile, sep = ',', index_col = 0)
        df_allqSecond['LATEST_PERIOD_END_DT_FULL_RECORD'] = pd.to_datetime(df_allqSecond['LATEST_PERIOD_END_DT_FULL_RECORD'], coerce = True)
        df_all = pd.concat([df_all, df_allSecond]).drop_duplicates().reset_index(drop=True)
        df_allq = pd.concat([df_allq, df_allqSecond]).drop_duplicates().reset_index(drop=True)

    #Set Up Data To Make it Ready For Analysis
    df_all = CalculateMargins(df_all, CalcFunction = CalcFunction)
    df_allq = CalculateMargins(df_allq, CalcFunction = CalcFunction)
    df_allLTM = getLTM(df_allq.copy(), df_all.copy(), CalcFunction = CalcFunction) #Note: Using a copy so df_allq doesn't get set to the LTM values
    df_allLTM = CalculateMargins(df_allLTM, CalcFunction = CalcFunction)
    df_allLTM = SetLTMBalanceSheetData(df_allLTM, CalcFunction = CalcFunction)
    df_all = CreateAverageBalanceSheet(df_all, 2, CalcFunction = CalcFunction)
    df_allLTM = CreateAverageBalanceSheet(df_allLTM, 5, CalcFunction = CalcFunction)
    df_allLTM = CalculateMargins(df_allLTM, CalcFunction = CalcFunction)

    #Load Tickers Data
    xl_Tickers = pd.ExcelFile(TickerFile)
    TickersList = xl_Tickers.parse('Sheet1')

    return (df_all, df_allq, df_allLTM, TickersList)


def RunPeerGroupsAllSectors(AnnualDF = df_all, QuarterDF = df_allq, LTMDF = df_allLTM, MarketData = TickersList, BaseSaveLocation = 'BloombergData\\PeerGroups\\', SavePDFs = True, ShowPDF = False, Sector = True, DontWork = [], OutputToExcel = False,
                            ChartColumns = ['SALES_REV_TURN', 'SalesGrowth', 'BS_TOT_ASSET', 'TangibleAsset_Coverage', 'GC_ADJ_EBITDA', 'Adj_EBITDA_Margin', 'TotalLeverageAdj', 'NetLeverageAdj', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA', 'ROA', 'UnleveragedFCFROA','EV_to_EBITDA_GC_Adj', 'Price_to_EPS_NTM', 'EQY_DVD_YLD_IND', 'CURRENT_TRR_1YR'],
                            BaseSpreadSheetColumns = ['Ticker', 'LATEST_PERIOD_END_DT_FULL_RECORD']):
    if(AnnualDF.empty == True):
        print('Did not pass data frames to function.  Loading standard files...')
        (AnnualDF, QuarterDF, LTMDF, MarketData) = LoadFiles()
    if (Sector == True):
        SectorList = list(MarketData['GICS_SECTOR_NAME'].unique())        
    else:
        SectorList = list(MarketData['GICS_INDUSTRY_NAME'].unique())
    for sector in SectorList:
        print(sector)
        if (Sector == True):
            TickersList_Reduced = MarketData[(MarketData['Ticker'].isin(AnnualDF['Ticker'].unique())) & (MarketData['GICS_SECTOR_NAME']== sector)]['Ticker'].unique()
        else:
            TickersList_Reduced = MarketData[(MarketData['Ticker'].isin(AnnualDF['Ticker'].unique())) & (MarketData['GICS_INDUSTRY_NAME']== sector)]['Ticker'].unique()
        if(len(TickersList_Reduced)>0):
            MassProducePeerGroups(AnnualDF, QuarterDF, LTMDF, TickersList_Reduced, MarketData, sector, BaseSaveLocation, DontWork, BaseSpreadSheetColumns, ChartColumns, SavePDF = SavePDFs, OutputToExcel = OutputToExcel)


def RunPeerGroupsAndHistoricalChartsSector(AnnualDF = df_all, QuarterDF = df_allq, LTMDF = df_allLTM, MarketData = TickersList,
                                           BaseSaveLocation = 'BloombergData\\PeerGroups\\', HistoricalChartBaseSaveLocation = 'BloombergData\\PeerGroups\\CompanyData\\',
                                           SavePDFs = True, ShowPDF = False, Sector = True, DontWork = [], OutputToExcel = False, IncludeLTM = True,
                                           ChartColumns = ['SALES_REV_TURN', 'SalesGrowth', 'BS_TOT_ASSET', 'TangibleAsset_Coverage', 'GC_ADJ_EBITDA', 'Adj_EBITDA_Margin', 'TotalLeverageAdj', 'NetLeverageAdj', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA', 'ROA', 'UnleveragedFCFROA','EV_to_EBITDA_GC_Adj', 'Price_to_EPS_NTM', 'EQY_DVD_YLD_IND', 'CURRENT_TRR_1YR'],
                                           HistoricalChartColumns = ['SALES_REV_TURN', 'SalesGrowth', 'GC_ADJ_EBITDA', 'EBITDAGrowth', 'ROTA', 'UnleveragedFCFROTA', 'ROA', 'UnleveragedFCFROA', 'TangibleAsset_Coverage', 'Adj_EBITDA_Margin', 'Gross_Margin', 'TotalLeverageAdj', 'NetLeverageAdj', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA'],
                                           BaseSpreadSheetColumns = ['Ticker', 'LATEST_PERIOD_END_DT_FULL_RECORD'],
                                           SectorsToPrint = []):
    print('Reminder to Make Sure \"Sector = True\" if using GICS_SECTOR_NAME and False if using GICS_INDUSTRY_NAME')
    if(AnnualDF.empty == True):
        print('Did not pass data frames to function.  Loading standard files...')
        (AnnualDF, QuarterDF, LTMDF, MarketData) = LoadFiles()
    if(len(SectorsToPrint)>0):
        for sector in SectorsToPrint:
            print(sector)
            if (Sector == True):
                TickersList_Reduced = MarketData[(MarketData['Ticker'].isin(AnnualDF['Ticker'].unique())) & (MarketData['GICS_SECTOR_NAME']== sector)]['Ticker'].unique()
            else:
                TickersList_Reduced = MarketData[(MarketData['Ticker'].isin(AnnualDF['Ticker'].unique())) & (MarketData['GICS_INDUSTRY_NAME']== sector)]['Ticker'].unique()
            if(len(TickersList_Reduced)>0):
                MassProduceHistoricalCharts(AnnualDF, QuarterDF, LTMDF, TickersList_Reduced, sector, HistoricalChartBaseSaveLocation, DontWork, BaseSpreadSheetColumns, HistoricalChartColumns, ColumnFormatting = DictionaryOfChartFormats(), IncludeLTM = IncludeLTM, SavePDF = SavePDFs)
                MassProducePeerGroups(AnnualDF, QuarterDF, LTMDF, TickersList_Reduced, MarketData, sector, BaseSaveLocation, DontWork, BaseSpreadSheetColumns, ChartColumns, SavePDF = SavePDFs, OutputToExcel = OutputToExcel)
            
    else:
        if (Sector == True):
            SectorList = list(MarketData['GICS_SECTOR_NAME'].unique())
        else:
            SectorList = list(MarketData['GICS_INDUSTRY_NAME'].unique())
        print('No Sectors Set.  Add a List to \"SectorsToPrint\".  Available Sectors:')
        print(SectorList)

def RunPeerGroupsAndHistoricalChartsList(AnnualDF = df_all, QuarterDF = df_allq, LTMDF = df_allLTM, MarketData = TickersList,
                                           BaseSaveLocation = 'BloombergData\\PeerGroups\\', HistoricalChartBaseSaveLocation = 'BloombergData\\PeerGroups\\CompanyData\\',
                                           SavePDFs = True, ShowPDF = False, Sector = True, DontWork = [], OutputToExcel = False, IncludeLTM = True,
                                           ChartColumns = ['SALES_REV_TURN', 'SalesGrowth', 'BS_TOT_ASSET', 'TangibleAsset_Coverage', 'GC_ADJ_EBITDA', 'Adj_EBITDA_Margin', 'TotalLeverageAdj', 'NetLeverageAdj', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA', 'ROA', 'UnleveragedFCFROA','EV_to_EBITDA_GC_Adj', 'Price_to_EPS_NTM', 'EQY_DVD_YLD_IND', 'CURRENT_TRR_1YR'],
                                           HistoricalChartColumns = ['SALES_REV_TURN', 'SalesGrowth', 'GC_ADJ_EBITDA', 'EBITDAGrowth', 'ROTA', 'UnleveragedFCFROTA', 'ROA', 'UnleveragedFCFROA', 'TangibleAsset_Coverage', 'Adj_EBITDA_Margin', 'Gross_Margin', 'TotalLeverageAdj', 'NetLeverageAdj', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA'],
                                           BaseSpreadSheetColumns = ['Ticker', 'LATEST_PERIOD_END_DT_FULL_RECORD'],
                                           CompanyList = [], CompanyListName = 'Test'):
    if(AnnualDF.empty == True):
        print('Did not pass data frames to function.  Loading standard files...')
        (AnnualDF, QuarterDF, LTMDF, MarketData) = LoadFiles()
    if(len(CompanyList)>0):
        ListOfCompaniesWithData = list(AnnualDF['Ticker'].unique())
        TickersList_Reduced = list(set(CompanyList).intersection(set(ListOfCompaniesWithData)))
        TickersList_NoData = list(set(CompanyList) - set(TickersList_Reduced))
        MassProduceHistoricalCharts(AnnualDF, QuarterDF, LTMDF, TickersList_Reduced, CompanyListName, HistoricalChartBaseSaveLocation, DontWork, BaseSpreadSheetColumns, HistoricalChartColumns, ColumnFormatting = DictionaryOfChartFormats(), IncludeLTM = IncludeLTM, SavePDF = SavePDFs)
        MassProducePeerGroups(AnnualDF, QuarterDF, LTMDF, TickersList_Reduced, MarketData, CompanyListName, BaseSaveLocation, DontWork, BaseSpreadSheetColumns, ChartColumns, SavePDF = SavePDFs, OutputToExcel = OutputToExcel)
        if(len(TickersList_NoData)>0):
            print('The following companies do not have data:')
            print(TickersList_NoData)
            
    else:
        print('No companies selected.  Add a list to \"CompanyList\"')
        

def CreateBalanceSheetChartsPeerGroup(AnnualDF = df_all, QuarterDF = df_allq, LTMDF = df_allLTM, MarketData = TickersList, Companies = [], IncludeLTM = True, BaseFileLocation = 'BloombergData\\PeerGroups\\', PDFCode = 'test'):
    """NEED TO FIX COLUMNS TO INCLUDE OTHER ASSETS AND REMOVE SUBTOTALS"""

    LTM_df = pd.DataFrame()
    for tickers in Companies:
        LTM_df = LTM_df.append(LTMDF[LTMDF['Ticker'] == tickers].ix[0,])

    LTM_df.sort_values(by='LATEST_PERIOD_END_DT_FULL_RECORD', ascending = True)
    PDF_toSave = BaseFileLocation + 'BalanceSheet_' + PDFCode + '.pdf'
    pdf_pages = PdfPages(PDF_toSave)
    def StackedBS_Assets(temp_df, Companies, Show = True, SavePDF = False, LegendFontSize = 6):
        temp_df = temp_df[temp_df['Ticker'].isin(Companies)]
        abbr_df = temp_df[['C&CE_AND_STI_DETAILED', 'BS_ACCT_NOTE_RCV', 'BS_INVENTORIES', 'BS_CUR_ASSET_REPORT', 'BS_NET_FIX_ASSET', 'BS_LT_INVEST', 'BS_DISCLOSED_INTANGIBLES']]
        labels = temp_df['Ticker']
        DF_for_plot = abbr_df.div(abbr_df.sum(1).astype(float), axis=0)*100
        fig = plt.figure(frameon=False)
        fig.set_size_inches(11.69,8.27)
        my_plot = DF_for_plot.plot(kind='bar', stacked=True)
        plt.title('Asset Composition')
        plt.xlabel('Company')
        plt.ylabel('Percentage of Assets')
        plt.ylim([0,120])
        lg = plt.legend(loc='best', ncol=3, prop={'size':LegendFontSize})
        lg.draw_frame(False)
        my_plot.set_xticklabels(labels)
        my_plot.spines['top'].set_visible(False)
        my_plot.spines['right'].set_visible(False)
        my_plot.xaxis.set_ticks_position('bottom')
        plt.tight_layout()
        if(Show == True):
            plt.show()
        if(SavePDF == True):
            pdf_pages.savefig()
        
    
    StackedBS_Assets(LTM_df, Companies, Show = False, SavePDF = True)
    pdf_pages.close()

#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------
#   CODE
#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------

formatter = FuncFormatter(money)
plt.close('all')
Dict_Row = defaultdict(list)
Chart_List = ['SYY US', 'CAH US', 'ABC US', 'MCK US', 'DHR US', 'GPC US', 'GWW US', 'UNFI US', 'LKQ US']
DontWork = []

Dates = []
ColumnNames = []
filepathfor_Excel = "BloombergData\\"
#Data_File_TSW = "BloombergData\BBG_TSWHoldingsAnnual.csv"
#Quarter_Data_File_TSW = "BloombergData\BBG_TSWHoldingsQuarterABBR.csv"
Data_File = "BloombergData\BBG_CombinedAnnual.csv"
Quarter_Data_File = "BloombergData\BBG_CombinedQuarterly.csv"
#Data_File = "BloombergData\BBG_REITAnnual.csv"
#Quarter_Data_File = "BloombergData\BBG_REITQuarter.csv"
ExcelSaveFile = 'BloombergData\\PeerGroups\\test.xlsx'
#Only using the below line for simplicity purposes
#TickersList = TickersList.head(506)
SavePDFs = True
IncludeLTM = True
OutputToExcel = False
CalcFunction = 'Normal'
#CalcFunction Options ---> 'Normal', 'REIT'"""
HistoricalChartBaseSaveLocation = 'BloombergData\\PeerGroups\\CompanyData\\'
PeerGroupBaseSaveLocation = 'BloombergData\\PeerGroups\\'


#(df_all, df_allq, df_allLTM, TickersList) = LoadFiles()

#TickersList = TickersList[TickersList['Ticker'].isin(df_all['Ticker'].unique())]

ColumnFormatting = DictionaryOfChartFormats()


#REIT Chart Output
#ColumnsForChartPeerGroup = ['SALES_REV_TURN', 'BS_TOT_ASSET', 'SalesGrowth', 'FFOGrowth', 'TangibleAsset_Coverage', 'Adj_EBITDA_Margin', 'TotalLeverageAdj', 'NetLeverageAdj', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA', 'MaintenanceCapEx_to_AdjEBITDA', 'GrowthCapEx_to_AdjEBITDA', 'ROA', 'UnleveragedFCFROA','EV_to_EBITDA_GC_Adj', 'Price_to_EPS_NTM', 'EQY_DVD_YLD_IND', 'CURRENT_TRR_1YR']
#ColumnsForChartHistorical = ['SALES_REV_TURN', 'SalesGrowth', 'GC_ADJ_EBITDA', 'EBITDAGrowth', 'CF_FFO', 'FFOGrowth','ROTA', 'UnleveragedFCFROTA', 'ROA', 'UnleveragedFCFROA', 'TangibleAsset_Coverage', 'Adj_EBITDA_Margin', 'TotalLeverageAdj', 'NetLeverageAdj', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA', 'MaintenanceCapEx_to_AdjEBITDA', 'GrowthCapEx_to_AdjEBITDA', 'IS_SQUARE_GLA', 'IS_NUMBER_OF_PROPERTIES']
#ColumnsForChartHistorical = ['SALES_REV_TURN', 'BS_TOT_ASSET', 'SalesGrowth']
#ColumnsForChartHistorical = ['SalesGrowth']





#tempLTM.groupby('GICS_INDUSTRY_NAME').agg({'EV_to_EBITDA_GC_Adj': [np.mean, np.median, 'count'], 'Forward_EV_to_EBITDA_GC_Adj': [np.mean, np.median, 'count'], 'Price_to_EPS_NTM': [np.mean, np.median, 'count'], 'Est_EBITDA_Growth': [np.mean, np.median, 'count']})

print(datetime.now() - startTime)


    

