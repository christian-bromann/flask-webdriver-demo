import os
import sys
import new
import unittest
from selenium import webdriver
from sauceclient import SauceClient

# it's best to remove the hardcoded defaults and always get these values
# from environment variables
USERNAME = os.environ.get('SAUCE_USERNAME', os.environ.get('SAUCE_USERNAME'))
ACCESS_KEY = os.environ.get(
    'SAUCE_ACCESS_KEY', os.environ.get('SAUCE_ACCESS_KEY'))
sauce = SauceClient(USERNAME, ACCESS_KEY)

browsers = [{"platform": "Windows 8",
             "browserName": "chrome",
             "version": "34",
             "tags": ["python", "chrome", "webdriver"]},
            {"platform": "Windows 8",
             "browserName": "firefox",
             "version": "29",
             "tags": ["python", "firefox", "webdriver"]},
            {"browserName": "Safari",
             "platformName": "iOS",
             "appium-version": "1.0",
             "platformVersion": "7.1",
             "deviceName": "iPhone Simulator",
             "device-orientation": "portrait",
             "tags": ["python", "Safari", "appium"]
             }]


def on_platforms(platforms):
    def decorator(base_class):
        module = sys.modules[base_class.__module__].__dict__
        for i, platform in enumerate(platforms):
            d = dict(base_class.__dict__)
            d['desired_capabilities'] = platform
            name = "%s_%s" % (base_class.__name__, i + 1)
            module[name] = new.classobj(name, (base_class,), d)
    return decorator


@on_platforms(browsers)
class SauceSampleTest(unittest.TestCase):

    def setUp(self):
        self.desired_capabilities['name'] = "flask app test"
        self.desired_capabilities['username'] = USERNAME
        self.desired_capabilities['access-key'] = ACCESS_KEY

        self.driver = webdriver.Remote(
            desired_capabilities=self.desired_capabilities,
            command_executor="http://localhost:4445/wd/hub"
        )
        self.driver.implicitly_wait(30)

    def test_login(self):

        # go to login page
        self.driver.get('http://localhost:5000/login')

        # enter user name
        name = self.driver.find_element_by_css_selector(
            'input[name="username"]')
        name.send_keys('admin')

        # enter password
        pw = self.driver.find_element_by_css_selector(
            'input[name="password"]')
        pw.send_keys('default')

        # click submit
        button = self.driver.find_element_by_css_selector(
            'input[value="Login"]')
        button.click()

        # login check
        message = self.driver.find_element_by_css_selector('.flash').text
        assert "You were logged in" in message

    def tearDown(self):

        try:
            if sys.exc_info() == (None, None, None):
                sauce.jobs.update_job(self.driver.session_id, passed=True)
            else:
                sauce.jobs.update_job(self.driver.session_id, passed=False)
        finally:
            self.driver.quit()
