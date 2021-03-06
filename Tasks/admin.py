from django.contrib import admin

from .models import PrimaryTasks, UpdatingCompanyDataStepOne, CreateNewDataPullFile, MergeNewCompanyData, PeerAndHistoricalChartsSector, LendingClub_Initial_New_Origination_Data_Cleaning, LendingClub_Combine_LC_App_Files, LendingClub_ChargeOffs, LendingClub_CleanCombinedApplications

# Register your models here.
admin.site.register(PrimaryTasks)
admin.site.register(UpdatingCompanyDataStepOne)
admin.site.register(CreateNewDataPullFile)
admin.site.register(MergeNewCompanyData)
admin.site.register(PeerAndHistoricalChartsSector)
admin.site.register(LendingClub_Initial_New_Origination_Data_Cleaning)
admin.site.register(LendingClub_Combine_LC_App_Files)
admin.site.register(LendingClub_ChargeOffs)
admin.site.register(LendingClub_CleanCombinedApplications)