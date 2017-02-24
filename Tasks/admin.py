from django.contrib import admin

from .models import PrimaryTasks, UpdatingCompanyDataStepOne, CreateNewDataPullFile, MergeNewCompanyData, PeerAndHistoricalChartsSector, LendingClub_Initial_New_Origination_Data_Cleaning

# Register your models here.
admin.site.register(PrimaryTasks)
admin.site.register(UpdatingCompanyDataStepOne)
admin.site.register(CreateNewDataPullFile)
admin.site.register(MergeNewCompanyData)
admin.site.register(PeerAndHistoricalChartsSector)
admin.site.register(LendingClub_Initial_New_Origination_Data_Cleaning)