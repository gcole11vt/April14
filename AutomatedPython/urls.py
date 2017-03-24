"""AutomatedPython URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from Tasks import views as Tasks_views
#from Tasks import urls as list_urls

urlpatterns = [
    url(r'^$', Tasks_views.home_page, name='home'),
    url(r'^FinData/UpdateStepOne/completed/$', Tasks_views.completed, name='UpdateStepOneCompleted'),
    url(r'^FinData/UpdateStepOne/$', Tasks_views.fin_data_update_step_one, name='UpdateStepOne'),
    url(r'^FinData/UpdateStepTwo/completed/$', Tasks_views.completed, name='UpdateStepTwoCompleted'),
    url(r'^FinData/UpdateStepTwo/$', Tasks_views.fin_data_update_step_two, name='UpdateStepTwo'),
    url(r'^FinData/NewCompany/completed/$', Tasks_views.completed, name='completed'),
    url(r'^FinData/NewCompany/$', Tasks_views.findata_newcompany, name='findata_newcompany'),
    url(r'^FinData/NewCompanyMerge/completed/$', Tasks_views.completed, name='completed'),
    url(r'^FinData/NewCompanyMerge/$', Tasks_views.findatamerge_newcompany, name='findata_newcompanymerge'),
    url(r'^FinData/Charts/completed/$', Tasks_views.completed, name='completed'),
    url(r'^FinData/Charts/$', Tasks_views.findata_runcharts, name='findata_runcharts'),
    url(r'^FinData/$', Tasks_views.findata_home, name='findata_home'),
    url(r'^LendingClub/NewOriginationData/InitialClean/completed/$', Tasks_views.completed, name='completed'),
    url(r'^LendingClub/NewOriginationData/InitialClean/$', Tasks_views.LC_new_orig_data_clean, name='LC_NewOriginationData_Clean'),
    url(r'^LendingClub/NewOriginationData/$', Tasks_views.LC_new_orig_data_home, name='LC_NewOriginationData_home'),
    url(r'^LendingClub/NewOriginationData/CombineAppFiles/completed/$', Tasks_views.completed, name='completed'),
    url(r'^LendingClub/NewOriginationData/CombineAppFiles/$', Tasks_views.LC_new_orig_data_combine_app_files, name='LC_NewOriginationData_CombineAppFiles'),
    url(r'^LendingClub/NewOriginationData/ChargeOffs/completed/$', Tasks_views.completed_with_output, name='completed_CO'),
    url(r'^LendingClub/NewOriginationData/ChargeOffs/$', Tasks_views.LC_new_orig_data_chargeoffs, name='LC_NewOriginationData_ChargeOffs'),
    url(r'^LendingClub/NewOriginationData/CleanCombinedData/completed/$', Tasks_views.completed, name='completed'),
    url(r'^LendingClub/NewOriginationData/CleanCombinedData/$', Tasks_views.LC_new_orig_data_clean_combined_data, name='LC_NewOriginationData_CleanCombinedData'),
    url(r'^admin/', admin.site.urls),
]
