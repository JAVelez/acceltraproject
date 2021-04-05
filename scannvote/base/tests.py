from django.test import LiveServerTestCase
from selenium import webdriver

# Create your tests here.
from django.urls import reverse

signup = '/signup/'
login = '/login/'
assemblies_index = '/cgeassembly/'

signup_good = 0
signup_fail_mismatch_pw = 1
signup_fail_weak_password = 2
signup_fail_student_id_empty = 3
signup_fail_student_id_lt_length = 4
signup_fail_student_id_gt_length = 5
signup_fail_student_id_non_numeric = 6

login_good = 0
login_bad = 1

good_student = {'username': 'gooduser1',
                    'student_id': '000000000',
                    'password1': 'GoodPW12',
                    'password2': 'GoodPW12'}
bad_student = {'username': 'gooduser1',
                    'student_id': '000000000',
                    'password1': 'GoodPW',
                    'password2': 'GoodPW'}


class StudentTest(LiveServerTestCase):
    def setUp(self):
        path = 'C:/Users/xboxa/PycharmProjects/acceltraProject/scannvote/webdriver/chromedriver.exe'
        self.browser = webdriver.Chrome(executable_path=path)

    def tearDown(self):
        self.browser.close()

    def signup_form_content(self, code):
        if code == signup_good:
            form = good_student
        elif code == signup_fail_mismatch_pw:
            form = {'username': 'tryhard1',
                    'student_id': '123456789',
                    'password1': 'GoodPW12',
                    'password2': 'GoodPW123'}
        elif code == signup_fail_weak_password:
            form = {'username': 'tryhard1',
                    'student_id': '123456789',
                    'password1': 'password1',
                    'password2': 'password1'}
        elif code == signup_fail_student_id_empty:
            form = {'username': 'tryhard1',
                    'student_id': '',
                    'password1': 'GoodPW12',
                    'password2': 'GoodPW12'}
        elif code == signup_fail_student_id_lt_length:
            form = {'username': 'tryhard1',
                    'student_id': '12345678',
                    'password1': 'GoodPW12',
                    'password2': 'GoodPW12'}
        elif code == signup_fail_student_id_gt_length:
            form = {'username': 'tryhard1',
                    'student_id': '1234567890',
                    'password1': 'GoodPW12',
                    'password2': 'GoodPW12'}
        elif code == signup_fail_student_id_non_numeric:
            form = {'username': 'tryhard1',
                    'student_id': '12345678a',
                    'password1': 'GoodPW12',
                    'password2': 'GoodPW12'}
        return form

    def signup_form_fill(self, code):
        form = self.signup_form_content(code)
        self.browser.find_element_by_name('username').send_keys(form['username'])
        self.browser.find_element_by_name('student_id').send_keys(form['student_id'])
        self.browser.find_element_by_name('password1').send_keys(form['password1'])
        self.browser.find_element_by_name('password2').send_keys(form['password2'])
        self.browser.find_element_by_name('signup').click()

    def signup_form_clear(self):
        self.browser.find_element_by_name('username').clear()
        self.browser.find_element_by_name('student_id').clear()
        self.browser.find_element_by_name('password1').clear()
        self.browser.find_element_by_name('password2').clear()

    def student_creation(self):
        self.browser.get(self.live_server_url + signup)
        self.signup_form_fill(signup_fail_mismatch_pw)
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/form/p[6]').text, 'Passwords do not match.')
        self.signup_form_clear()

        self.signup_form_fill(signup_fail_weak_password)
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/form/p[6]').text, 'This password is too common.')
        self.signup_form_clear()

        self.signup_form_fill(signup_fail_student_id_empty)
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/form/p[6]').text, 'This password is too common.')
        self.signup_form_clear()

        self.signup_form_fill(signup_fail_student_id_lt_length)
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/form/p[3]').text,
                         'Ensure this value has at least 9 characters (it has 8).')
        self.signup_form_clear()

        self.signup_form_fill(signup_fail_student_id_gt_length)
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/form/p[3]').text,
                         'Ensure this value has at most 9 characters (it has 10).')
        self.signup_form_clear()

        self.signup_form_fill(signup_fail_student_id_non_numeric)
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/form/p[3]').text, 'Only digit characters.')
        self.signup_form_clear()

        self.signup_form_fill(signup_good)
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/main/h2').text, 'Username: gooduser1')

        self.student_logout()

        print('Registration constraints successfully tested!')

    def login_form_fill(self, code):
        if code == login_good:
            form = good_student
        else:
            form = bad_student
        self.browser.find_element_by_name('username').send_keys(form['username'])
        self.browser.find_element_by_name('password').send_keys(form['password1'])
        self.browser.find_element_by_name('login').click()

    def student_login(self):
        self.browser.get(self.live_server_url + login)

        self.login_form_fill(login_bad)
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/main/p').text,
                         'Your username and password didn\'t match. Please try again.')

        self.login_form_fill(login_good)
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/main/h2').text, 'Username: gooduser1')

        self.student_logout()
        print('Login constraints successfully tested!')

    def student_logout(self):
        self.browser.find_element_by_xpath('/html/body/header/a').click()
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/main/h2').text, 'Log in to My Site')

    def test_student(self):
        self.student_creation()
        self.student_login()




