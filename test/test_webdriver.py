import os
import sys
import new
import unittest
import time
from selenium import webdriver
from sauceclient import SauceClient

parentdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.insert(0, parentdir)

from flaskr import app, get_db

# it's best to remove the hardcoded defaults and always get these values
# from environment variables
USERNAME = os.environ.get('SAUCE_USERNAME', os.environ.get('SAUCE_USERNAME'))
ACCESS_KEY = os.environ.get(
    'SAUCE_ACCESS_KEY', os.environ.get('SAUCE_ACCESS_KEY'))
FLASK_USERNAME = 'admin'
FLASK_PASSWORD = 'default'

sauce = SauceClient(USERNAME, ACCESS_KEY)

browsers = [{'platform': 'Windows 8',
             'browserName': 'chrome',
             'version': '34',
             'tags': ['python', 'chrome', 'webdriver']},
            {'platform': 'Windows 8',
             'browserName': 'firefox',
             'version': '29',
             'tags': ['python', 'firefox', 'webdriver']},
            {'platform': 'Windows 8.1',
             'browserName': 'internet explorer',
             'version': '11',
             'tags': ['python', 'internet explorer', 'webdriver']},
            {'browserName': 'Safari',
             'platformName': 'iOS',
             'appium-version': '1.0',
             'platformVersion': '7.1',
             'deviceName': 'iPhone Simulator',
             'device-orientation': 'portrait',
             'tags': ['python', 'Safari', 'appium']
             }]


def on_platforms(platforms):
    def decorator(base_class):
        module = sys.modules[base_class.__module__].__dict__
        for i, platform in enumerate(platforms):
            d = dict(base_class.__dict__)
            d['desired_capabilities'] = platform
            name = '%s_%s' % (base_class.__name__, i + 1)
            module[name] = new.classobj(name, (base_class,), d)
    return decorator


@on_platforms(browsers)
class SauceSampleTest(unittest.TestCase):

    def setUp(self):

        self.desired_capabilities['name'] = 'flask app test'
        self.desired_capabilities['username'] = USERNAME
        self.desired_capabilities['access-key'] = ACCESS_KEY

        if os.environ.get('TRAVIS_BUILD_NUMBER'):
            self.desired_capabilities[
                'build'] = os.environ.get('TRAVIS_BUILD_NUMBER')
            self.desired_capabilities[
                'tunnel-identifier'] = os.environ.get('TRAVIS_JOB_NUMBER')

        self.driver = webdriver.Remote(
            desired_capabilities=self.desired_capabilities,
            command_executor='http://localhost:4445/wd/hub'
        )
        self.driver.implicitly_wait(30)

    def login(self):
        # go to login page
        self.driver.get('http://localhost:5000/login')

        # enter user name
        name = self.driver.find_element_by_css_selector(
            'input[name="username"]')
        name.send_keys(FLASK_USERNAME)

        # enter password
        pw = self.driver.find_element_by_css_selector(
            'input[name="password"]')
        pw.send_keys(FLASK_PASSWORD)

        # click submit
        button = self.driver.find_element_by_css_selector(
            'input[value="Login"]')
        button.click()

    def test_login(self):

        # login
        self.login()

        # login check
        message = self.driver.find_element_by_css_selector('.flash').text
        assert 'You were logged in' in message

    def test_post(self):

        self.login()

        # go to main page
        self.driver.get('http://localhost:5000')

        # enter title
        title = self.driver.find_element_by_css_selector(
            'input[name="title"]')
        title.send_keys('Sauce Labs Python test')

        # enter text
        textarea = self.driver.find_element_by_css_selector(
            'textarea')
        textarea.send_keys('Hi, there!')

        # click submit
        button = self.driver.find_element_by_css_selector(
            'input[value="Share"]')
        button.click()

        # check if entry was posted successfully
        flash = self.driver.find_element_by_css_selector('.flash').text
        assert 'New entry was successfully posted' in flash

        # check if content is correct
        post = self.driver.find_element_by_css_selector(
            'body > div > ul > li:nth-child(1)').text
        assert 'Sauce Labs Python test\nHi, there!' in post

    def test_mocked_post(self):

        print 'dsadsdasad'

        ts = time.time()

        with app.app_context():
            db = get_db()
            db.execute('insert into entries (title, text) values (?, ?)',
                       ['Current timestamp', ts])
            db.commit()

        # go to main page
        self.driver.get('http://localhost:5000')

        # check if mcoked content is correct
        post = self.driver.find_element_by_css_selector(
            'body > div > ul > li:nth-child(1)').text
        assert 'Current timestamp\n%d' % ts in post

    def tearDown(self):

        try:
            if sys.exc_info() == (None, None, None):
                sauce.jobs.update_job(
                    self.driver.session_id, passed=True, public=True)
            else:
                sauce.jobs.update_job(
                    self.driver.session_id, passed=False, public=True)
        finally:
            self.driver.quit()
