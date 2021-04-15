from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from .models import Assembly, Motion, Amendment, Interaction
import base.tests as base
import base.models as basemodels
from django.contrib.auth.models import User
from django.utils import timezone
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Create your tests here.

home = '/cgeassembly/'
login_button = '/html/body/main/form/input[5]'

# html items
asamblea1_text = 'Asamblea General 1'
asamblea1_link = '/html/body/main/div/ul/li/a'
mocion1_text = 'Moción para acabar capstone'
mocion1_link = '/html/body/main/div/ul[2]/li/a'
mocion2_text = 'Moción #2 para acabar capstone pls'
mocion2_link = '/html/body/main/div/ul[2]/li[2]/a'
a_favor_radio_id = 'a-favor'
en_contra_radio_id = 'en-contra'
vote_button_name = 'vote-btn'
view_results_button = '/html/body/main/div/a'
a_favor_results = '/html/body/main/div/ul/li[1]'
en_contra_results = '/html/body/main/div/ul/li[2]'
no_amendments_name = 'no-amendments-msg'
no_amendments_text = 'No amendments'
student_id_form = '//*[@id="id_student_id"]'
scanner_submit_btn = '/html/body/main/div/form/button'

vote_error_name = 'vote-error'
vote_not_concluded_name = 'vote-not-concluded-msg'
motion_name_desc = 'motion-desc'


class CgeassemblyTestCases(StaticLiveServerTestCase):
    def setUp(self):
        path = 'C:/Users/xboxa/PycharmProjects/acceltraProject/scannvote/webdriver/chromedriver.exe'
        self.browser = webdriver.Chrome(executable_path=path)

        self.assembly1 = Assembly(assembly_name='Asamblea General 1', date=timezone.now())
        self.assembly1.save()
        self.motion1 = Motion(assembly=self.assembly1, motion_text='Moción para acabar capstone',
                              date=timezone.now())
        self.motion1.save()

    def anon_user_run(self):
        """
        method that represents an anonymous user requesting access to view information and a failed attempt to vote
        :return: n/a
        """
        self.navigate_to_motion(mocion1_link, mocion1_text)

        # Not voteable, anonymous user
        self.assertEqual(self.browser.find_element_by_name('voting-closed').text,
                         'Voting is not open at the moment')

        # Voteable, anonymous user
        self.motion_is_now_voteable()
        self.assert_(self.browser.find_element_by_xpath(base.login_redirect))
        self.browser.find_element_by_xpath(base.login_redirect).click()
        self.assertEqual(self.browser.find_element_by_xpath(base.login_redirect_confirmation).text, 'Login')

        print('Anonymous user run successful!')

    def student_user_run(self):
        """
        method that represents a student logged in trying to access information and voting while not attending and later
        while attending the assembly

        it also represents voting access limited due to not being open for voting by the staff members
        :return: n/a
        """
        # <--------- motion testing begins --------->
        # revert motion changes
        self.motion1.voteable = False
        self.motion1.save()

        # signup
        self.browser.get(self.live_server_url + '/signup')

        # signup + login, not attending
        base.signup_form(self.browser, base.good_student)

        self.navigate_to_motion(mocion1_link, mocion1_text)
        self.assertEqual(self.browser.find_element_by_name('voting-closed').text,
                         'Voting is not open at the moment')

        # motion is open to vote from the admin side
        self.motion1.voteable = True
        self.motion1.save()
        self.browser.refresh()

        self.browser.find_element_by_id(a_favor_radio_id).click()
        self.browser.find_element_by_name(vote_button_name).click()
        self.assertEqual(self.browser.find_element_by_name(vote_error_name).text, 'You are not attending the assembly')

        # user enters the assembly and "is attending"
        user = User.objects.get()
        Interaction.objects.create(student=user.student, timestamp=timezone.now(), assembly=self.assembly1)

        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, a_favor_radio_id)))
        self.browser.find_element_by_id(a_favor_radio_id).click()
        self.browser.find_element_by_name(vote_button_name).click()

        # voting has not concluded assertion
        self.assertEqual('Voting has not concluded yet.', self.browser.find_element_by_name(vote_not_concluded_name).text)

        # try to vote twice
        self.browser.back()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, en_contra_radio_id)))
        self.browser.find_element_by_id(en_contra_radio_id).click()
        self.browser.find_element_by_name(vote_button_name).click()

        # you cannot vote twice assertion
        self.assertEqual('You have already cast your vote.',
                         self.browser.find_element_by_name(vote_error_name).text)

        # voting has conlcuded / closed by the cge through the admin side
        self.motion1 = Motion.objects.get()  # refresh local motion object to match db motion
        self.motion1.voteable = False
        self.motion1.save()

        # user navigates to results
        self.browser.find_element_by_xpath(view_results_button).click()
        self.assertEqual('A favor: 1', self.browser.find_element_by_xpath(a_favor_results).text)
        self.assertEqual('En contra: 0', self.browser.find_element_by_xpath(en_contra_results).text)

        print('successful log in ->attending ->voting ->results view run')

        # <--------- amendment testing begins --------->
        # staff member creates 2nd motion
        self.motion2 = Motion.objects.create(assembly=self.assembly1, motion_text='Moción #2 para acabar capstone pls',
                                             date=timezone.now())
        self.motion2.save()

        self.assertTrue(Motion.objects.all()[0].archived)  # prev motion is archived
        self.browser.get(self.live_server_url + home)
        self.navigate_to_motion(mocion2_link, mocion2_text)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.NAME, no_amendments_name)))
        self.assertEqual(no_amendments_text, self.browser.find_element_by_name(no_amendments_name).text)

        # staff member amends motion
        self.amendment = Amendment(motion_amended=self.motion2)
        self.amendment.assembly = self.assembly1
        self.amendment.motion_text = 'amendando porque capstone es lo mejor del mundo'
        self.amendment.save()

        self.browser.refresh()
        # view amendment details
        self.browser.find_element_by_xpath('/html/body/main/div/li/a').click()
        self.assertEqual(self.browser.find_element_by_name('voting-closed').text,
                         'Voting is not open at the moment')

        # staff member opens voting
        self.amendment.voteable = True
        self.amendment.save()

        self.browser.refresh()

        # vote on amendment
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, a_favor_radio_id)))
        self.browser.find_element_by_id(a_favor_radio_id).click()
        self.browser.find_element_by_name(vote_button_name).click()

        # voting has conlcuded / closed by the cge through the admin side
        self.amendment = Amendment.objects.get()  # refresh local amendment object to match db amendment
        self.amendment.voteable = False
        self.amendment.save()

        # user navigates to results
        self.browser.refresh()
        self.assertEqual('A favor: 1', self.browser.find_element_by_xpath(a_favor_results).text)
        self.assertEqual('En contra: 0', self.browser.find_element_by_xpath(en_contra_results).text)

        # staff member updates motion with amendment and user votes on original motion now amended
        amendado_text = self.motion2.motion_text + ' AMENDADO: ' + self.amendment.motion_text
        self.motion2.motion_text = amendado_text
        self.motion2.save()
        self.navigate_to_motion(mocion2_link, amendado_text)
        self.assertEqual(amendado_text, self.browser.find_element_by_name(motion_name_desc).text)
        print('Successful amendment creation and voting!')

    def navigate_to_motion(self, mocion, mocion_text):
        """
        helper method to navigate all pages according to a user use case scenario
        :param mocion: motion to enter
        :param mocion_text: motion text for assertion
        :return: n/a
        """
        self.browser.get(self.live_server_url + home)
        self.assertEqual(asamblea1_text, self.browser.find_element_by_xpath(asamblea1_link).text)

        self.browser.find_element_by_xpath(asamblea1_link).click()
        self.assertEqual(mocion_text, self.browser.find_element_by_xpath(mocion).text)

        self.browser.find_element_by_xpath(mocion).click()

    def motion_is_now_voteable(self):
        """
        method to simulate when a staff member allows voting access to attending members
        :return:
        """
        self.motion1.voteable = True
        self.motion1.save()
        self.browser.refresh()

    def scan_student(self):
        """
        method that represents an admin scans a student id
        :return: n/a
        """

        # signup + login admin
        self.browser.get(self.live_server_url + '/signup')
        base.signup_form(self.browser, base.good_admin)

        # assign admin priv
        admin = basemodels.Student.objects.all()[1].user
        admin.is_superuser = True
        admin.save()

        self.browser.refresh()
        self.browser.find_element_by_xpath('/html/body/main/div/a').click()

        # test form decline a shorter student id
        self.browser.find_element_by_xpath(student_id_form).send_keys(base.lt_student_id)
        self.browser.find_element_by_xpath(scanner_submit_btn).click()
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/main/div/form/p[2]').text,
                         'Ensure this value has at least 9 characters (it has 8).')
        self.browser.find_element_by_xpath(student_id_form).clear()

        # test form decline a longer student id
        self.browser.find_element_by_xpath(student_id_form).send_keys(base.gt_student_id)
        self.browser.find_element_by_xpath(scanner_submit_btn).click()
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/main/div/form/p[2]').text,
                         'Ensure this value has at most 9 characters (it has 10).')
        self.browser.find_element_by_xpath(student_id_form).clear()

        # test form decline a student id including a char
        self.browser.find_element_by_xpath(student_id_form).send_keys(base.char_student_id)
        self.browser.find_element_by_xpath(scanner_submit_btn).click()
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/main/div/form/p[2]').text, 'Only digit characters.')
        self.browser.find_element_by_xpath(student_id_form).clear()

        # test form accept existing student
        self.browser.find_element_by_xpath(student_id_form).send_keys(base.good_student_id)
        self.browser.find_element_by_xpath(scanner_submit_btn).click()
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/main/div/h3/span').text, 'Student has stopped attending')

    def test_cgeassembly(self):
        """
        method to test student user use case and an anonymous user trying to access information and vote on motions
        :return:
        """
        self.anon_user_run()
        self.student_user_run()
        self.scan_student()


