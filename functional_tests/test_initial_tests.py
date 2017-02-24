from .base import FunctionalTest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape
from unittest import skip


class InitialTests(FunctionalTest):
    
    def test_home_page_title_is_correct(self):
        #User goes to site
        self.browser.get('http://localhost:8000')

        self.assertIn('Types of Tasks', self.browser.title)
        
        #User sees "Temp" link
        linkitem = self.browser.find_element_by_link_text('TEMP')
        desiredLinkText = 'TEMP'
        self.assertEqual(linkitem.text, desiredLinkText)
        
        #User clicks on "Temp" link
        if(linkitem.text == desiredLinkText):
            linkitem.click()
        
        #Able to find place to input location of market data file
        inputbox_market_data_file_loc = self.browser.find_element_by_name("QuarterOrAnnual")
        self.assertEqual(
            inputbox_market_data_file_loc.get_attribute('placeholder'),
            "Annual or Quarterly Data?"
            )
        
        #Able to find place to input location of historical data file
        inputbox_historical_data_file_loc = self.browser.find_element_by_name("ExcelFilePath")
        self.assertEqual(
            inputbox_historical_data_file_loc.get_attribute('placeholder'),
            "Base filepath for files"
            )
        
        #Type "abc" & "123" into boxes
        inputbox_market_data_file_loc.send_keys('abc')
        inputbox_historical_data_file_loc.send_keys('123\n')
        
        
        
    
        