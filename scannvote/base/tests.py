from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# url's
signup_url = '/signup/'
login_url = '/login/'

# signup codes
signup_good = 0
signup_fail_mismatch_pw = 1
signup_fail_weak_password = 2
signup_fail_student_id_empty = 3
signup_fail_student_id_lt_length = 4
signup_fail_student_id_gt_length = 5
signup_fail_student_id_non_numeric = 6

# login codes
login_good = 0
login_bad_pw = 1
login_bad_username = 2
login_bad_both = 3

# test data
good_username = 'gooduser1'
good_student_id = '000000000'
good_pw = 'GoodPW12'

good_admin = 'goodadmin1'
good_admin_id = '000000001'

lt_student_id = '12345678'
gt_student_id = '1234567890'
char_student_id = '12345678a'
bad_pw = 'password'
bad_username = 'baduser'

# represents good user registration
good_student = {'username': good_username, 'student_id': good_student_id, 'password1': good_pw, 'password2': good_pw}

# represents good admin registration
good_admin = {'username': good_admin, 'student_id': good_admin_id, 'password1': good_pw, 'password2': good_pw}

# represent bad user registrations
student_mismatch_pw = {'username': good_username, 'student_id': good_student_id, 'password1': good_pw, 'password2': bad_pw}

student_weak_pw = {'username': good_username, 'student_id': good_student_id, 'password1': bad_pw, 'password2': bad_pw}

student_id_empty = {'username': good_username, 'student_id': '', 'password1': good_pw, 'password2': good_pw}

student_id_lt = {'username': good_username, 'student_id': lt_student_id, 'password1': good_pw, 'password2': good_pw}

student_id_gt = {'username': good_username, 'student_id': gt_student_id, 'password1': good_pw, 'password2': good_pw}

student_id_char = {'username': good_username, 'student_id': char_student_id, 'password1': good_pw, 'password2': good_pw}

# represent bad user logins

bad_student_login_pw = {'username': good_username, 'password1': bad_pw}

bad_student_login_username = {'username': bad_pw, 'password1': good_pw}

bad_student_login_both = {'username': bad_username, 'password1': bad_pw}

# html items
error_mismatch_pw = '/html/body/main/div/form/p[6]'
error_common_pw = error_mismatch_pw
error_length_sid = '/html/body/main/div/form/p[3]'
error_char_sid = error_length_sid
home_username = '/html/body/main/div/h2'
error_login_mismatch = '/html/body/main/div/p'

login_redirect = '/html/body/header/a[2]'
login_redirect_confirmation = '/html/body/main/div/h2'


class StudentTestCases(StaticLiveServerTestCase):
    def setUp(self):
        path = 'C:/Users/xboxa/PycharmProjects/acceltraProject/scannvote/webdriver/chromedriver.exe'
        self.browser = webdriver.Chrome(executable_path=path)

    def signup_form_content(self, code):
        """
        method to return different validation errors and 1 successful registration at signup
        :param code:
        :return: n/a
        """
        if code == signup_good:
            form = good_student
        elif code == signup_fail_mismatch_pw:
            form = student_mismatch_pw
        elif code == signup_fail_weak_password:
            form = student_weak_pw
        elif code == signup_fail_student_id_empty:
            form = student_id_empty
        elif code == signup_fail_student_id_lt_length:
            form = student_id_lt
        elif code == signup_fail_student_id_gt_length:
            form = student_id_gt
        elif code == signup_fail_student_id_non_numeric:
            form = student_id_char
        return form

    def signup_form_fill(self, code):
        """
        method to fill the signup form according to the given code
        :param code: determines the outcome of the signup form
        :return: n/a
        """
        form = self.signup_form_content(code)
        signup_form(self.browser, form)

    def signup_form_clear(self):
        """
        method to clear form fields
        :return: n/a
        """
        self.browser.find_element_by_name('username').clear()
        self.browser.find_element_by_name('student_id').clear()
        self.browser.find_element_by_name('password1').clear()
        self.browser.find_element_by_name('password2').clear()

    def student_creation(self):
        """
        method to test all validation parameters when creating a new student user
        :return: n/a
        """
        self.browser.get(self.live_server_url + signup_url)

        # mismatch password validation error
        self.signup_form_fill(signup_fail_mismatch_pw)
        self.assertEqual(self.browser.find_element_by_xpath(error_mismatch_pw).text, 'Passwords do not match.')
        self.signup_form_clear()

        # weak password validation error
        self.signup_form_fill(signup_fail_weak_password)
        self.assertEqual(self.browser.find_element_by_xpath(error_common_pw).text, 'This password is too common.')
        self.signup_form_clear()

        # blank student id when submitting form error
        self.signup_form_fill(signup_fail_student_id_empty)
        self.assertEqual(self.browser.find_element_by_xpath(error_common_pw).text, 'This password is too common.')
        self.signup_form_clear()

        # student id less than 9 digits long validation error
        self.signup_form_fill(signup_fail_student_id_lt_length)
        self.assertEqual(self.browser.find_element_by_xpath(error_length_sid).text,
                         'Ensure this value has at least 9 characters (it has 8).')
        self.signup_form_clear()

        # student id more than 9 digits long validation error
        self.signup_form_fill(signup_fail_student_id_gt_length)
        self.assertEqual(self.browser.find_element_by_xpath(error_length_sid).text,
                         'Ensure this value has at most 9 characters (it has 10).')
        self.signup_form_clear()

        # student id contains characters validation error
        self.signup_form_fill(signup_fail_student_id_non_numeric)
        self.assertEqual(self.browser.find_element_by_xpath(error_char_sid).text, 'Only digit characters.')
        self.signup_form_clear()

        # successful validation and registration
        self.signup_form_fill(signup_good)
        self.assertEqual(self.browser.find_element_by_xpath(home_username).text, 'Username: gooduser1')

        self.student_logout()

        print('Registration constraints successfully tested!')

    def login_form_fill(self, code):
        """
        method to fill login form
        :param code: determines the outcome of the login form
        :return: n/a
        """
        if code == login_good:
            form = good_student
        elif code == login_bad_pw:
            form = bad_student_login_pw
        elif code == login_bad_username:
            form = bad_student_login_username
        elif code == login_bad_both:
            form = bad_student_login_both
        else:
            pass
        self.browser.find_element_by_name('username').send_keys(form['username'])
        self.browser.find_element_by_name('password').send_keys(form['password1'])
        self.browser.find_element_by_name('login').click()

    def student_login(self):
        """
        method to test successful and unsuccessful logins
        :return: n/a
        """
        self.browser.get(self.live_server_url + login_url)

        self.login_form_fill(login_bad_pw)
        self.assertEqual(self.browser.find_element_by_xpath(error_login_mismatch).text,
                         'Your username and password didn\'t match. Please try again.')

        self.login_form_fill(login_bad_username)
        self.assertEqual(self.browser.find_element_by_xpath(error_login_mismatch).text,
                         'Your username and password didn\'t match. Please try again.')

        self.login_form_fill(login_bad_both)
        self.assertEqual(self.browser.find_element_by_xpath(error_login_mismatch).text,
                         'Your username and password didn\'t match. Please try again.')

        self.login_form_fill(login_good)
        self.assertEqual(self.browser.find_element_by_xpath(home_username).text, 'Username: gooduser1')

        self.student_logout()
        print('Login constraints successfully tested!')

    def student_logout(self):
        """
        method to logout student
        :return: n/a
        """
        self.browser.find_element_by_xpath(login_redirect).click()
        self.assertEqual(self.browser.find_element_by_xpath(login_redirect_confirmation).text, 'Login')

    def test_student(self):
        """
        method to test student creation and student login
        :return: n/a
        """
        self.student_creation()
        self.student_login()


def signup_form(browser, form):
    """
    :param browser: selenium driver for specific browser; chromedriver instance
    :param form: student form
    :return: n/a
    """
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
    browser.find_element_by_name('username').send_keys(form['username'])
    browser.find_element_by_name('student_id').send_keys(form['student_id'])
    browser.find_element_by_name('password1').send_keys(form['password1'])
    browser.find_element_by_name('password2').send_keys(form['password2'])
    browser.find_element_by_name('signup').click()




