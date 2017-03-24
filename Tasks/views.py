from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.utils.datastructures import MultiValueDictKeyError
import sys

from Tasks.models import PrimaryTasks, UpdatingCompanyDataStepOne, UpdatingCompanyDataStepTwo, CreateNewDataPullFile, MergeNewCompanyData, PeerAndHistoricalChartsSector, LendingClub_Initial_New_Origination_Data_Cleaning, LendingClub_Combine_LC_App_Files, LendingClub_ChargeOffs, LendingClub_CleanCombinedApplications

from Tasks.forms import PrimaryTasksForm, UpdatingCompanyDataStepOneForm, UpdatingCompanyDataStepTwoForm, CreateNewDataPullFileForm, MergeNewCompanyDataForm, PeerAndHistoricalChartsSectorForm, LendingClub_Initial_New_Origination_Data_CleaningForm, LendingClub_Combine_LC_App_FilesForm, LendingClub_ChargeOffsForm, LendingClub_CleanCombinedApplicationsForm

from .PullBBGFields_New import Update_Step1, Update_Step2, CreateBBGPullFile, MergeNewCompanies
from .HistoricalCharts_New import RunPeerGroupsAndHistoricalChartsSector, LoadFiles
from .InitialCleanFileFromLCWebsite import LCCleanFile
from .CombineLCAppFiles import CombineFiles
from .LCChargeOffs import ChargeOffs
from .LC_CleanCombinedFiles import ProcessCombinedFiles

# Create your views here.
def home_page(request):
    return render(request, 'home.html',)


def findata_home(request):
    return render(request, 'FinData.html',)






def fin_data_update_step_one(request):
    header_code = 'Find Updates to Historical Data'
    title_of_page = 'Find information to update'
    code_url = 'UpdateStepOne'

    if request.method == 'POST':
        form = UpdatingCompanyDataStepOneForm(data=request.POST)
        if form.is_valid():
            form.save()
            task = UpdatingCompanyDataStepOne.objects.last()
            lenUpdateAnnual = Update_Step1(QuarterOrAnnual = 'Annual',
                     AnnualFile = task.AnnualFile, QuarterFile = task.QuarterFile,
                     AnnualColumns = task.AnnualColumns, QuarterColumns = task.QuarterColumns,
                     FileForTickers = task.FileForTickers, filepathfor_Excel = task.filepathfor_Excel)
            lenUpdateQuarterly = Update_Step1(QuarterOrAnnual = 'Quarterly',
                     AnnualFile = task.AnnualFile, QuarterFile = task.QuarterFile,
                     AnnualColumns = task.AnnualColumns, QuarterColumns = task.QuarterColumns,
                     FileForTickers = task.FileForTickers, filepathfor_Excel = task.filepathfor_Excel)
            print(lenUpdateAnnual)
            print(lenUpdateQuarterly)
            return redirect('/FinData/UpdateStepOne/completed/')
        else:
            return render(request, 'form_base.html', {'form': form, 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    else:
        return render(request, 'form_base.html', {'form': UpdatingCompanyDataStepOneForm(), 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})

def fin_data_update_step_two(request):
    header_code = 'Update Historical Data'
    title_of_page = 'Update Information'
    code_url = 'UpdateStepTwo'

    if request.method == 'POST':
        form = UpdatingCompanyDataStepTwoForm(data=request.POST)
        if form.is_valid():
            form.save()
            task = UpdatingCompanyDataStepTwo.objects.last()
            Update_Step2(QuarterOrAnnual = 'Annual',
                     AnnualFile = task.ExistingAnnualFile, 
                     QuarterFile = task.ExistingQuarterFile,
                     AnnualUpdateFile = task.NewAnnualFile, 
                     QuarterUpdateFile = task.NewQuarterFile)
            Update_Step2(QuarterOrAnnual = 'Quarterly',
                     AnnualFile = task.ExistingAnnualFile, 
                     QuarterFile = task.ExistingQuarterFile,
                     AnnualUpdateFile = task.NewAnnualFile, 
                     QuarterUpdateFile = task.NewQuarterFile)
            return redirect('/FinData/UpdateStepTwo/completed/')
        else:
            return render(request, 'form_base.html', {'form': form, 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    else:
        return render(request, 'form_base.html', {'form': UpdatingCompanyDataStepTwoForm(), 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})

    
def findata_newcompany(request):
    header_code = 'Enter New Companies To Retrieve Data'
    title_of_page = 'New Companies'
    code_url = 'findata_newcompany'

    if request.method == 'POST':
        form = CreateNewDataPullFileForm(data=request.POST)
        if form.is_valid():
            form.save()
            task = CreateNewDataPullFile.objects.last()
            tickers = [s.replace("'", "") for s in task.TickersList.split(',')]
            tickers = [s.lstrip() for s in tickers]
            tickers = [s.rstrip() for s in tickers]
            #Annual
            CreateBBGPullFile(tickers, task.filepathfor_Excel, task.sector, task.numperiodsAnnual, task.FileForColumnsAnnual,'Annual')
            #Quarterly
            CreateBBGPullFile(tickers, task.filepathfor_Excel, task.sector, task.numperiodsQuarter, task.FileForColumnsQuarter,'Quarterly')
            return redirect('/FinData/NewCompany/completed/')
        else:
            return render(request, 'form_base.html', {'form': form, 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    else:
        return render(request, 'form_base.html', {'form': CreateNewDataPullFileForm(), 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})

def findatamerge_newcompany(request):
    header_code = 'Merge New Companies'
    title_of_page = 'Merge New Companies'
    code_url = 'findata_newcompanymerge'

    if request.method == 'POST':
        form = MergeNewCompanyDataForm(data=request.POST)
        if form.is_valid():
            form.save()
            task = MergeNewCompanyData.objects.last()
            MergeNewCompanies(task.AnnualFile, task.NewAnnualFile, task.QuarterFile, task.NewQuarterFile)
            return redirect('/FinData/NewCompanyMerge/completed/')
        else:
            return render(request, 'form_base.html', {'form': form, 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    else:
        return render(request, 'form_base.html', {'form': MergeNewCompanyDataForm(), 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
        
    
def findata_runcharts(request):
    header_code = 'Create Charts'
    title_of_page = 'Charting'
    code_url = 'findata_runcharts'

    
    def prep_charts(item):
        item = [s.replace("'", "") for s in item.split(',')]
        item = [s.replace("[", "") for s in item]
        item = [s.replace("]", "") for s in item]
        item = [s.lstrip() for s in item]
        item = [s.rstrip() for s in item]
        return item
    
    
    if request.method == 'POST':
        form = PeerAndHistoricalChartsSectorForm(data=request.POST)
        if form.is_valid():
            form.save()
            task = PeerAndHistoricalChartsSector.objects.last()
            print(task.AnnualFileLoc)
            print(task.QuarterFileLoc)
            print(task.TickersFileLoc)
            (df_all, df_allq, df_allLTM, TickersList) = LoadFiles(AnnualDataFile =  task.AnnualFileLoc, QuarterDataFile = task.QuarterFileLoc, TickerFile = task.TickersFileLoc)

            RunPeerGroupsAndHistoricalChartsSector(AnnualDF = df_all, 
                                                   QuarterDF = df_allq, 
                                                   LTMDF = df_allLTM, 
                                                   MarketData = TickersList,
                                                   BaseSaveLocation = task.BaseSaveLoc,
                                                   HistoricalChartBaseSaveLocation = task.HistoricalChartBaseSaveLoc,
                                                   SavePDFs = True, ShowPDF = False, 
                                                   Sector = task.SectorOrIndustry, 
                                                   DontWork = prep_charts(task.TickerExclusions), 
                                                   OutputToExcel = False, 
                                                   IncludeLTM = task.IncludeLTMData,
                                                   ChartColumns = prep_charts(task.ChartColumns),
                                                   HistoricalChartColumns = prep_charts(task.HistoricalChartColumns),
                                                   BaseSpreadSheetColumns = prep_charts(task.BaseSpreadSheetColumns),
                                                   SectorsToPrint = prep_charts(task.IndustryOptions),
                                                                             )
            return redirect('/FinData/Charts/completed/')
        else:
            return render(request, 'form_base.html', {'form': form, 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    else:
        return render(request, 'form_base.html', {'form': PeerAndHistoricalChartsSectorForm(), 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})

        
    
    
def completed(request):
    return render(request, 'new_task.html')

def completed_with_output(request, output):
    return render(request, 'new_task.html', {'output_from_program':output})


def LC_new_orig_data_home(request):
    return render(request, 'LC_NewOrigData.html',)


def LC_new_orig_data_clean(request):
    header_code = 'LC Clean New Data'
    title_of_page = 'Clean New Lending Club Origination Data'
    code_url = 'LC_NewOriginationData_Clean'
    
    if request.method == 'POST':
        form = LendingClub_Initial_New_Origination_Data_CleaningForm(data=request.POST)
        if form.is_valid():
            form.save()
            task = LendingClub_Initial_New_Origination_Data_Cleaning.objects.last()
            LCCleanFile(FileName = task.FileName, BaseFileLocation = task.BaseFileLocation, BaseOutputLocation = task.OutputFileLocation)
            return redirect('/LendingClub/NewOriginationData/InitialClean/completed/')
        else:
            return render(request, 'form_base.html', {'form': form, 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    else:
        return render(request, 'form_base.html', {'form': LendingClub_Initial_New_Origination_Data_CleaningForm(), 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    
def LC_new_orig_data_combine_app_files(request):
    header_code = 'LC Combine Cleaned App Files'
    title_of_page = 'Combine Cleaned Application Files'
    code_url = 'LC_NewOriginationData_CombineAppFiles'
    
    if request.method == 'POST':
        form = LendingClub_Combine_LC_App_FilesForm(data=request.POST)
        if form.is_valid():
            form.save()
            task = LendingClub_Combine_LC_App_Files.objects.last()
            CombineFiles(BaseDir = task.BaseFileDirectory)
            return redirect('/LendingClub/NewOriginationData/CombineAppFiles/completed/')
        else:
            return render(request, 'form_base.html', {'form': form, 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    else:
        return render(request, 'form_base.html', {'form': LendingClub_Combine_LC_App_FilesForm(), 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    
def LC_new_orig_data_chargeoffs(request):
    header_code = 'LC Charge Offs'
    title_of_page = 'Determine Charge-Offs'
    code_url = 'LC_NewOriginationData_ChargeOffs'
    
    if request.method == 'POST':
        form = LendingClub_ChargeOffsForm(data=request.POST)
        if form.is_valid():
            form.save()
            task = LendingClub_ChargeOffs.objects.last()
            (MeanChargeOff, MedianChargeOff, RunTime) = ChargeOffs(PaymentHistoryFile = task.PaymentHistoryFile, BaseFileDirectory = task.BaseFileDirectory)
            task.MedianRecoveryRate = MedianChargeOff
            task.MeanRecoveryRate = MeanChargeOff
            task.RunTime = RunTime
            task.save()
            #return redirect('/LendingClub/NewOriginationData/ChargeOffs/completed/')
            output_result = "Median Recovery Rate: " + "%.2f" % (MedianChargeOff*100) + "% Mean Recovery Rate: " + "%.2f" % (MeanChargeOff*100) + "%"
            return render(request, 'new_task.html', {'output_from_program':output_result})
        else:
            return render(request, 'form_base.html', {'form': form, 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    else:
        return render(request, 'form_base.html', {'form': LendingClub_ChargeOffsForm(), 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    
def LC_new_orig_data_clean_combined_data(request):
    header_code = 'LC Prep App Data for ML'
    title_of_page = 'Prepare Cleaned Application Files for Machine Learning'
    code_url = 'LC_NewOriginationData_CleanCombinedData'
    
    if request.method == 'POST':
        form = LendingClub_CleanCombinedApplicationsForm(data=request.POST)
        if form.is_valid():
            form.save()
            task = LendingClub_CleanCombinedApplications.objects.last()
            RunTime = ProcessCombinedFiles(ApplicationDataLocation = task.ApplicationFileLocation, OutputFile = task.OutputFileLocation, WPS_OutputFile = task.WPSOutputFileLocation)
            task.RunTime = RunTime
            task.save()
            return redirect('/LendingClub/NewOriginationData/CleanCombinedData/completed/')
        else:
            return render(request, 'form_base.html', {'form': form, 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})
    else:
        return render(request, 'form_base.html', {'form': LendingClub_CleanCombinedApplicationsForm(), 'header_code': header_code, 'title_of_page':title_of_page, 'code_url':code_url,})