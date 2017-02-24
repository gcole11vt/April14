from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

import sys


class FunctionalTest(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):         
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                cls.live_server_url = ''
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url
        cls.browser = webdriver.Firefox()
        cls.browser.implicitly_wait(3)
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()

    def setUp(self):         
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()
