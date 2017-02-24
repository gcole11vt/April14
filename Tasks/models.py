from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone


# Create your models here.
class PrimaryTasks(models.Model):
    
    task = models.TextField(default = '')
    description = models.TextField(default = '')
    
    def __str__(self):
        return self.task
    
class UpdatingCompanyDataStepOne(models.Model):
    
    QuarterOrAnnual = models.CharField(max_length=10, choices = [('Annual', 'Annual'), ('Quarterly','Quarterly')], default='Annual')
    AnnualFile = models.TextField(default = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedAnnual.csv")
    QuarterFile = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedQuarterly.csv")
    AnnualColumns = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\Desired_BBG_Columns.csv")
    QuarterColumns = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\Desired_BBG_Columns_Quarterly.csv")
    FileForTickers = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\TickerList.xlsx")
    filepathfor_Excel = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\\")
    pub_date = models.DateTimeField('date published', default = timezone.now())
    
class UpdatingCompanyDataStepTwo(models.Model):
    
    QuarterOrAnnual = models.CharField(max_length=10, choices = [('Annual', 'Annual'), ('Quarterly','Quarterly')], default='Annual')
    ExistingAnnualFile = models.TextField(default = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedAnnual.csv")
    ExistingQuarterFile = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedQuarterly.csv")
    NewAnnualFile = models.TextField(default = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_UpdateAnnual.xlsx")
    NewQuarterFile = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\\BBG_UpdateQuarter.xlsx")
    pub_date = models.DateTimeField('date published', default = timezone.now())
    
class CreateNewDataPullFile(models.Model):
    
    TickersList = models.TextField(default = '')
    filepathfor_Excel = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\\")
    sector = models.TextField(default = 'new_tickers')
    numperiodsQuarter = models.IntegerField(default = 12, help_text="Quarterly-12")
    numperiodsAnnual = models.IntegerField(default = 10, help_text="Annual-10")
    FileForColumnsAnnual = models.TextField(default = "C:\\Users\\gcole\\Documents\\BloombergData\\Desired_BBG_Columns.csv")
    FileForColumnsQuarter = models.TextField(default = "C:\\Users\\gcole\\Documents\\BloombergData\\Desired_BBG_Columns_Quarterly.csv")
    QuarterOrAnnual = models.CharField(max_length=10, choices = [('Annual', 'Annual'), ('Quarterly','Quarterly')], default='Annual')
    pub_date = models.DateTimeField('date published', default = timezone.now())

class MergeNewCompanyData(models.Model):
    
    AnnualFile = models.TextField(default = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedAnnual.csv")
    QuarterFile = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedQuarterly.csv")
    NewAnnualFile = models.TextField(default = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_new_tickersAnnual.xlsx")
    NewQuarterFile = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\\BBG_new_tickersQuarter.xlsx")
    pub_date = models.DateTimeField('date published', default = timezone.now())
    
class PeerAndHistoricalChartsSector(models.Model):
    
    AnnualFileLoc = models.TextField(default = "C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedAnnual.csv")
    QuarterFileLoc = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedQuarterly.csv")
    TickersFileLoc = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\TickerList.xlsx")
    BaseSaveLoc = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\\PeerGroups\\")
    HistoricalChartBaseSaveLoc = models.TextField(default ="C:\\Users\\gcole\\Documents\\BloombergData\\PeerGroups\\CompanyData\\")
    SectorOrIndustry = models.BooleanField(default=False)
    IncludeLTMData = models.BooleanField(default=True)
    TickerExclusions = models.CharField(max_length = 200, blank=True, default = '')
    ChartColumns = models.TextField(default = "'SALES_REV_TURN', 'SalesGrowth', 'BS_TOT_ASSET', 'TangibleAsset_Coverage', 'GC_ADJ_EBITDA', 'Adj_EBITDA_Margin', 'TotalLeverageAdj', 'NetLeverageAdj', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA', 'ROA', 'UnleveragedFCFROA','EV_to_EBITDA_GC_Adj', 'Price_to_EPS_NTM', 'EQY_DVD_YLD_IND', 'CURRENT_TRR_1YR'")
    HistoricalChartColumns = models.TextField(default = "'SALES_REV_TURN', 'SalesGrowth', 'GC_ADJ_EBITDA', 'EBITDAGrowth', 'ROTA', 'UnleveragedFCFROTA', 'ROA', 'UnleveragedFCFROA', 'TangibleAsset_Coverage', 'Adj_EBITDA_Margin', 'Gross_Margin', 'TotalLeverageAdj', 'NetLeverageAdj', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA'")
    BaseSpreadSheetColumns = models.TextField(default = "'Ticker', 'LATEST_PERIOD_END_DT_FULL_RECORD'")
    IndustryOptions = models.TextField(default='', blank=True)
    
class LendingClub_Initial_New_Origination_Data_Cleaning(models.Model):
    
    FileLocation = models.TextField(default = "")
    pub_date = models.DateTimeField('date published', default = timezone.now())
