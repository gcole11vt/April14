from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from Tasks.views import home_page, fin_data_update_step_one, fin_data_step_one_home
from Tasks.models import UpdatingCompanyDataStepOne
from Tasks.forms import UpdatingCompanyDataStepOneForm, EMPTY_ITEM_ERROR
from django.utils.html import escape
from unittest import skip


# Create your tests here.
@skip
class HomePageTest(TestCase):
    
    def test_root_url_resolves_to_home_page_view(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')
        
        
class StepOnePageTest(TestCase):

   
        
    def temp_StepOne_page_redirects_after_POST(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['QuarterOrAnnual'] = 'Annual'
        
        response = fin_data_update_step_one(request)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')       

    def test_StepOne_page_only_saves_items_when_necessary(self):
        request = HttpRequest()
        fin_data_update_step_one(request)
        self.assertEqual(UpdatingCompanyDataStepOne.objects.count(),0)
        
    def test_StepOne_page_renders_temp_template(self):
        response = self.client.get('/FinData/UpdateStepOne/')
        self.assertTemplateUsed(response, 'fin_data_step_one.html')
        
    def test_StepOne_page_uses_UpdatingCompanyDataStepOneForm_form(self):
        response = self.client.get('/FinData/UpdateStepOne/')
        self.assertIsInstance(response.context['form'], UpdatingCompanyDataStepOneForm)
        
    def test_validation_errors_are_sent_back_to_StepOne_page_template(self):
        response = self.client.post('/FinData/UpdateStepOne/', data={'ExcelFilePath': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fin_data_step_one.html')
       
    def test_invalid_input_passes_form_to_template(self):
        response = self.client.post('/FinData/UpdateStepOne/', data={'ExcelFilePath': ''})
        self.assertIsInstance(response.context['form'], UpdatingCompanyDataStepOneForm)
        
        
class Model_UpdatingCompanyDataStepOne_Test(TestCase):
    
    def test_saving_and_retrieving(self):
        first_task = UpdatingCompanyDataStepOne()
        first_task.QuarterOrAnnual = 'Quarterly'
        first_task.save()
        
        second_task = UpdatingCompanyDataStepOne()
        second_task.QuarterOrAnnual = 'Annual'
        second_task.save()
        
        saved_tasks = UpdatingCompanyDataStepOne.objects.all()
        self.assertEqual(saved_tasks.count(), 2)
        first_saved_task = saved_tasks[0]
        second_saved_task = saved_tasks[1]
        self.assertEqual(first_saved_task.QuarterOrAnnual, 'Quarterly')
        self.assertEqual(second_saved_task.QuarterOrAnnual, 'Annual')

        
class UpdatingCompanyDataStepOneFormTest(TestCase):
    
    def test_form_renders_item_text_input(self):
        form = UpdatingCompanyDataStepOneForm()
        self.fail(form.as_p())
   
    def test_form_validation_for_blank_items(self):
        form = UpdatingCompanyDataStepOneForm(data={'QuarterOrAnnual': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['QuarterOrAnnual'], [EMPTY_ITEM_ERROR])
    
    
        
    
        
