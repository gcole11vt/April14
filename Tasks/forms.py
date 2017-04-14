from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from Tasks.models import PrimaryTasks, UpdatingCompanyDataStepOne, UpdatingCompanyDataStepTwo, CreateNewDataPullFile, MergeNewCompanyData, PeerAndHistoricalChartsSector, BenchmarkCharts, FinDataLoadFiles, LendingClub_Initial_New_Origination_Data_Cleaning, LendingClub_Combine_LC_App_Files, LendingClub_ChargeOffs, LendingClub_CleanCombinedApplications

EMPTY_ITEM_ERROR = 'You cannot leave this empty'
QorAChoices = (
    ('Annual', 'Annual'),
    )
INDUSTRY_CHOICES = (
        ('Aerospace & Defense', 'Aerospace & Defense'),
        ('Air Freight & Logistics', 'Air Freight & Logistics'),
        ('Airlines', 'Airlines'),
        ('Auto Components', 'Auto Components'),
        ('Automobiles', 'Automobiles'),
        #('Banks', 'Banks'),
        ('Beverages', 'Beverages'),
        ('Biotechnology', 'Biotechnology'),
        ('Building Products', 'Building Products'),
        #('Capital Markets', 'Capital Markets'),
        ('Chemicals', 'Chemicals'),
        ('Commercial Services & Supplies', 'Commercial Services & Supplies'),
        ('Communications Equipment', 'Communications Equipment'),
        ('Construction & Engineering', 'Construction & Engineering'),
        ('Construction Materials', 'Construction Materials'),
        #('Consumer Finance', 'Consumer Finance'),
        ('Containers & Packaging', 'Containers & Packaging'),
        ('Distributors', 'Distributors'),
        ('Diversified Consumer Services', 'Diversified Consumer Services'),
        #('Diversified Financial Services', 'Diversified Financial Services'),
        ('Diversified Telecommunication', 'Diversified Telecommunication'),
        #('Electric Utilities', 'Electric Utilities'),
        ('Electrical Equipment', 'Electrical Equipment'),
        ('Electronic Equipment, Instrume', 'Electronic Equipment, Instrume'),
        ('Energy Equipment & Services', 'Energy Equipment & Services'),
        #('Equity Real Estate Investment', 'Equity Real Estate Investment'),
        ('Food & Staples Retailing', 'Food & Staples Retailing'),
        ('Food Products', 'Food Products'),
        #('Gas Utilities', 'Gas Utilities'),
        ('Health Care Equipment & Suppli', 'Health Care Equipment & Suppli'),
        ('Health Care Providers & Servic', 'Health Care Providers & Servic'),
        ('Health Care Technology', 'Health Care Technology'),
        ('Hotels, Restaurants & Leisure', 'Hotels, Restaurants & Leisure'),
        ('Household Durables', 'Household Durables'),
        ('Household Products', 'Household Products'),
        ('IT Services', 'IT Services'),
        #('Independent Power and Renewabl', 'Independent Power and Renewabl'),
        ('Industrial Conglomerates', 'Industrial Conglomerates'),
        #('Insurance', 'Insurance'),
        ('Internet & Direct Marketing Re', 'Internet & Direct Marketing Re'),
        ('Internet Software & Services', 'Internet Software & Services'),
        ('Leisure Products', 'Leisure Products'),
        ('Life Sciences Tools & Services', 'Life Sciences Tools & Services'),
        ('Machinery', 'Machinery'),
        ('Media', 'Media'),
        ('Metals & Mining', 'Metals & Mining'),
        #('Mortgage Real Estate Investmen', 'Mortgage Real Estate Investmen'),
        #('Multi-Utilities', 'Multi-Utilities'),
        ('Multiline Retail', 'Multiline Retail'),
        ('Oil, Gas & Consumable Fuels', 'Oil, Gas & Consumable Fuels'),
        ('Paper & Forest Products', 'Paper & Forest Products'),
        ('Personal Products', 'Personal Products'),
        ('Pharmaceuticals', 'Pharmaceuticals'),
        ('Professional Services', 'Professional Services'),
        ('Real Estate Management & Devel', 'Real Estate Management & Devel'),
        ('Road & Rail', 'Road & Rail'),
        ('Semiconductors & Semiconductor', 'Semiconductors & Semiconductor'),
        ('Software', 'Software'),
        ('Specialty Retail', 'Specialty Retail'),
        ('Technology Hardware, Storage &', 'Technology Hardware, Storage &'),
        ('Textiles, Apparel & Luxury Goo', 'Textiles, Apparel & Luxury Goo'),
        #('Thrifts & Mortgage Finance', 'Thrifts & Mortgage Finance'),
        ('Tobacco', 'Tobacco'),
        ('Trading Companies & Distributo', 'Trading Companies & Distributo'),
        ('Transportation Infrastructure', 'Transportation Infrastructure'),
        #('Water Utilities', 'Water Utilities'),
        ('Wireless Telecommunication Ser', 'Wireless Telecommunication Ser'),
        )

BENCHMARKCHART_CHOICES = (
        ('SalesGrowth', 'SalesGrowth'),
        ('TotalLeverageAdj', 'TotalLeverageAdj'),
        )



class PrimaryTasksForm(forms.ModelForm):
    
    class Meta:
        model = PrimaryTasks
        fields = ('task', 'description')

class UpdatingCompanyDataStepOneForm(forms.models.ModelForm):
    
    class Meta:
        model = UpdatingCompanyDataStepOne
        fields = ('QuarterOrAnnual', 'AnnualFile','QuarterFile','AnnualColumns','QuarterColumns','FileForTickers', 'filepathfor_Excel')
        labels = {
            'QuarterOrAnnual':_('Periodicity'),
            'AnnualFile':_('File: Annual'),
            'QuarterFile':_('File: Quarter'),
            'AnnualColumns':_('File: Annual Columns'),
            'QuarterColumns':_('File: Quarter Columns'),
            'FileForTickers':_('File: Companies'),
            'filepathfor_Excel':_('Base File Path'),
            }
        widgets= {
            #'QuarterOrAnnual': forms.fields.TextInput(attrs={
            #    'placeholder':'Q or A',
            #    'class': 'form-control input-md',
            #    }),
            'AnnualFile': forms.fields.TextInput(attrs={
                'placeholder':'Base filepath for files',
                'class': 'col-sm-10 input-md',
                }),
            'QuarterFile': forms.fields.TextInput(attrs={
                'placeholder':'Base filepath for files',
                'class': 'col-sm-10 input-md',
                }),
            'AnnualColumns': forms.fields.TextInput(attrs={
                'placeholder':'Base filepath for files',
                'class': 'col-sm-10 input-md',
                }),
            'QuarterColumns': forms.fields.TextInput(attrs={
                'placeholder':'Base filepath for files',
                'class': 'col-sm-10 input-md',
                }),
            'FileForTickers': forms.fields.TextInput(attrs={
                'placeholder':'Base filepath for files',
                'class': 'col-sm-10 input-md',
                }),
            
            'filepathfor_Excel': forms.fields.TextInput(attrs={
                'placeholder':'Base filepath for files',
                'class': 'col-sm-10 input-md',
                }),
        }
        
        error_messages = {
            'QuarterOrAnnual': {'required': EMPTY_ITEM_ERROR},
            'filepathfor_Excel': {'required': EMPTY_ITEM_ERROR}
            }

class UpdatingCompanyDataStepTwoForm(forms.models.ModelForm):
    
    class Meta:
        model = UpdatingCompanyDataStepTwo
        fields = ('ExistingAnnualFile','ExistingQuarterFile','NewAnnualFile','NewQuarterFile')
        labels = {
            'ExistingAnnualFile':_('File: Existing Annual'),
            'ExistingQuarterFile':_('File: Existing Quarter'),
            'NewAnnualFile':_('File: New Annual'),
            'NewQuarterFile':_('File: New Quarter'),
            }
        widgets= {
            #'QuarterOrAnnual': forms.fields.TextInput(attrs={
            #    'placeholder':'Q or A',
            #    'class': 'form-control input-md',
            #    }),
            'ExistingAnnualFile': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'ExistingQuarterFile': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'NewAnnualFile': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'NewQuarterFile': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
        }
        
        
        
        
class CreateNewDataPullFileForm(forms.models.ModelForm):
    
    
    
    class Meta:
        model = CreateNewDataPullFile
        fields = ('TickersList','sector', 'filepathfor_Excel','numperiodsAnnual', 'FileForColumnsAnnual','numperiodsQuarter', 'FileForColumnsQuarter')
        labels = {
            'QuarterOrAnnual':_('Periodicity'),
            'TickersList':_('List of Tickers'),
            'sector':_('Sector Name'),
            'numperiodsAnnual':_('Annual Periods'),
            'numperiodsQuarter':_('Quarterly Periods'),
            'FileForColumnsAnnual':_('File: Annual Columns'),
            'FileForColumnsQuarter':_('File: Quarterly Columns'),
            'filepathfor_Excel':_('Base File Path'),
            }
        widgets= {
            #'QuarterOrAnnual': forms.fields.TextInput(attrs={
            #    'placeholder':'Q or A',
            #    'class': 'form-control input-md',
            #    }),
            'TickersList': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'sector': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'numperiodsAnnual': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'numperiodsQuarter': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'QuarterColumns': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'FileForColumnsAnnual': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'FileForColumnsQuarter': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'filepathfor_Excel': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
        }        

    

class MergeNewCompanyDataForm(forms.models.ModelForm):
    
    class Meta:
        model = MergeNewCompanyData
        fields = ('AnnualFile', 'NewAnnualFile', 'QuarterFile','NewQuarterFile')
        labels = {
            'AnnualFile':_('Existing Annual Data'),
            'NewAnnualFile':_('New Annual File'),
            'QuarterFile':_('Existing Quarter Data'),
            'NewQuarterFile':_('New Quarter File'),
            }
        widgets= {
            'AnnualFile': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'NewAnnualFile': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'QuarterFile': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'NewQuarterFile': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
        }    

class PeerAndHistoricalChartsSectorForm(forms.models.ModelForm):
    
    IndustryOptions = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=INDUSTRY_CHOICES,
        label='Industries',
        )
    
    
    
    class Meta:
        model = PeerAndHistoricalChartsSector
        fields = ('AnnualFileLoc', 'QuarterFileLoc', 'TickersFileLoc','BaseSaveLoc', 'HistoricalChartBaseSaveLoc', 'SectorOrIndustry', 'IncludeLTMData', 'TickerExclusions', 'ChartColumns', 'HistoricalChartColumns', 'BaseSpreadSheetColumns', 'IndustryOptions')
        
        labels = {
            'AnnualFileLoc':_('Existing Annual Data'),
            'QuarterFileLoc':_('Existing Quarterly Data'),
            'TickersFileLoc':_('Existing Market Data'),
            'BaseSaveLoc':_('Base File Save Location'),
            'HistoricalChartBaseSaveLoc':_('Base Chart Save Location'),
            'SectorOrIndustry':_('Use Sector or Industry?'),
            'IncludeLTMData':_('Use LTM Data?'),
            'TickerExclusions':_('Tickers That Do Not Work'),
            'ChartColumns':_('Peer Group Stats to Chart'),
            'HistoricalChartColumns':_('Historical Stats to Chart'),
            'BaseSpreadSheetColumns':_('Base Required Items'),
            'IndustryOptions':_('Industries'),
            }
        widgets= {
            'AnnualFileLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'QuarterFileLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'TickersFileLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'BaseSaveLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'HistoricalChartBaseSaveLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'TickerExclusions': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'ChartColumns': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'HistoricalChartColumns': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'BaseSpreadSheetColumns': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            
            

        }    

        
class BenchmarkChartsForm(forms.models.ModelForm):
    
    ChartColumns = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=BENCHMARKCHART_CHOICES,
        label='Charts',
        )
    
    
    
    class Meta:
        model = BenchmarkCharts
        fields = ('AnnualFileLoc', 'QuarterFileLoc', 'TickersFileLoc','BaseSaveLoc', 'IncludeLTMData', 'ChartColumns', 'BaseCompany', 'CompanyList', 'IncludeBaseCompanyInPeers')
        
        labels = {
            'AnnualFileLoc':_('Existing Annual Data'),
            'QuarterFileLoc':_('Existing Quarterly Data'),
            'TickersFileLoc':_('Existing Market Data'),
            'BaseSaveLoc':_('Base File Save Location'),
            'IncludeLTMData':_('Use LTM Data?'),
            'BaseCompany':_('Base Company'),
            'CompanyList':_('Peers'),
            'IncludeBaseCompanyInPeers':_('Include Base Company In Peers'),
            }
        widgets= {
            'AnnualFileLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'QuarterFileLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'TickersFileLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'BaseSaveLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'IncludeLTMData': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'BaseCompany': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'CompanyList': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            
            'IncludeBaseCompanyInPeers': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),

        }    
        
class FinDataLoadFilesForm(forms.models.ModelForm):
    
    
    class Meta:
        model = FinDataLoadFiles
        fields = ('AnnualFileLoc', 'QuarterFileLoc', 'TickersFileLoc')
        
        labels = {
            'AnnualFileLoc':_('Existing Annual Data'),
            'QuarterFileLoc':_('Existing Quarterly Data'),
            'TickersFileLoc':_('Existing Market Data'),
            }
        widgets= {
            'AnnualFileLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'QuarterFileLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'TickersFileLoc': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),           

        }    
        

class LendingClub_Initial_New_Origination_Data_CleaningForm(forms.models.ModelForm):
    
    class Meta:
        model = LendingClub_Initial_New_Origination_Data_Cleaning
        fields = ('BaseFileLocation', 'FileName', 'OutputFileLocation')
        labels = {
            'BaseFileLocation':_('Original File Location'),
            'FileName':_('File Name'),
            'OutputFileLocation':_('Cleaned File Location'),
            }
        widgets= {
            'BaseFileLocation': forms.fields.TextInput(attrs={
                'placeholder':'Base File Location',
                'class': 'col-sm-10 input-md',
                }),
            'FileName': forms.fields.TextInput(attrs={
                'placeholder':'File Name. Include .csv',
                'class': 'col-sm-10 input-md',
                }),
            'OutputBaseFileLocation': forms.fields.TextInput(attrs={
                'placeholder':'Cleaned File Location',
                'class': 'col-sm-10 input-md',
                }),
        }    
        
class LendingClub_Combine_LC_App_FilesForm(forms.models.ModelForm):
    class Meta:
        model = LendingClub_Combine_LC_App_Files
        fields = ('BaseFileDirectory',)
        labels = {
            'BaseFileDirectory':_('Base File Directory'),
            }
        widgets= {
            'BaseFileDirectory': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
        }    
        
class LendingClub_ChargeOffsForm(forms.models.ModelForm):
    
    class Meta:
        model = LendingClub_ChargeOffs
        fields = ('PaymentHistoryFile', 'BaseFileDirectory',)
        labels = {
            'PaymentHistoryFile':_('Payment History File'),
            'BaseFileDirectory':_('Base File Directory'),
            }
        widgets= {
            'PaymentHistoryFile': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'BaseFileDirectory': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
        }    
        
class LendingClub_CleanCombinedApplicationsForm(forms.models.ModelForm):
    
    class Meta:
        model = LendingClub_CleanCombinedApplications
        fields = ('ApplicationFileLocation', 'OutputFileLocation','WPSOutputFileLocation')
        labels = {
            'ApplicationFileLocation':_('Location of Apps'),
            'OutputFileLocation':_('Output File Location'),
            'WPSOutputFileLocation':_('WPS Output File Location'),
            }
        widgets= {
            'ApplicationFileLocation': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'OutputFileLocation': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
            'WPSOutputFileLocation': forms.fields.TextInput(attrs={
                'class': 'col-sm-10 input-md',
                }),
        }    