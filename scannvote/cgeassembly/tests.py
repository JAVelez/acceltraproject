from django.test import LiveServerTestCase
from selenium import webdriver
from .models import Assembly, Motion, Amendment, Choice, Interaction
import base.tests as base
from django.contrib.auth.models import User
from django.utils import timezone
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Create your tests here.

home = '/cgeassembly/'
login_button = '/html/body/main/form/input[5]'

asamblea1_text = 'Asamblea General 1'
asamblea1_link = '/html/body/main/ul/li/a'
mocion1_text = 'Moción para acabar capstone'
mocion1_link = '/html/body/main/ul[2]/li/a'
mocion2_text = 'Moción #2 para acabar capstone pls'
mocion2_link = '/html/body/main/ul[2]/li[2]/a'
a_favor_radio = '/html/body/main/form/label[1]'
en_contra_radio = '/html/body/main/form/label[2]'
vote_button = '/html/body/main/form/input[5]'
view_results_button = '/html/body/main/a'
a_favor_results = '/html/body/main/ul/li[1]'
en_contra_results = '/html/body/main/ul/li[2]'
no_amendments = '/html/body/main/p'
no_amendments_text = 'No amendments'


class CgeassemblyTestCases(LiveServerTestCase):
    def setUp(self):
        path = 'C:/Users/xboxa/PycharmProjects/acceltraProject/scannvote/webdriver/chromedriver.exe'
        self.browser = webdriver.Chrome(executable_path=path)

        self.assembly1 = Assembly(assembly_name='Asamblea General 1', date=timezone.now())
        self.assembly1.save()
        self.motion1 = Motion(assembly=self.assembly1, motion_text='Moción para acabar capstone',
                              date=timezone.now())
        self.motion1.save()
        self.choices_creation(self.motion1)

    def anon_user_run(self):
        """
        method that represents an anonymous user requesting access to view information and a failed attempt to vote
        :return: n/a
        """
        self.navigate_to_motion(mocion1_link, mocion1_text)

        # Not voteable, anonymous user
        self.assertEqual('Voting is not open at the moment',
                         self.browser.find_element_by_xpath('/html/body/main/h3').text)

        # Voteable, anonymous user
        self.motion_is_now_voteable()
        self.assert_(self.browser.find_element_by_xpath(login_button))
        self.browser.find_element_by_xpath(login_button).click()
        self.assertEqual(self.browser.find_element_by_xpath('/html/body/main/h2').text, 'Log in to My Site')

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
        self.assertEqual('Voting is not open at the moment',
                         self.browser.find_element_by_xpath('/html/body/main/h3').text)

        # motion is open to vote from the admin side
        self.motion1.voteable = True
        self.motion1.save()
        self.browser.refresh()

        self.assertEqual('a favor', self.browser.find_element_by_xpath(a_favor_radio).text)
        self.browser.find_element_by_xpath(vote_button).click()
        self.assertEqual('You are not attending the assembly',
                         self.browser.find_element_by_xpath('/html/body/main/p[1]/strong').text)

        # user enters the assembly and "is attending"
        user = User.objects.get()
        Interaction.objects.create(student=user.student, timestamp=timezone.now(), assembly=self.assembly1)
        # user.student.attending = True
        # user.save()

        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, a_favor_radio)))
        self.browser.find_element_by_xpath(a_favor_radio).click()
        self.browser.find_element_by_xpath(vote_button).click()

        # voting has not concluded assertion
        self.assertEqual('Voting has not concluded yet.', self.browser.find_element_by_xpath('/html/body/main/h3').text)

        # try to vote twice
        self.browser.back()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, en_contra_radio)))
        self.browser.find_element_by_xpath(en_contra_radio).click()
        self.browser.find_element_by_xpath(vote_button).click()

        # you cannot vote twice assertion
        self.assertEqual('You have already cast your vote.',
                         self.browser.find_element_by_xpath('/html/body/main/p[1]/strong').text)

        # voting has conlcuded / closed by the cge through the admin side
        self.motion1.voteable = False
        self.motion1.save()

        # user navigates to results
        self.browser.find_element_by_xpath(view_results_button).click()
        self.assertEqual('a favor -- 1 vote', self.browser.find_element_by_xpath(a_favor_results).text)
        self.assertEqual('en contra -- 0 votes', self.browser.find_element_by_xpath(en_contra_results).text)

        print('successful log in ->attending ->voting ->results view run')

        # <--------- amendment testing begins --------->
        # staff member creates 2nd motion
        self.motion2 = Motion.objects.create(assembly=self.assembly1, motion_text='Moción #2 para acabar capstone pls',
                                             date=timezone.now())
        self.motion2.save()
        self.choices_creation(self.motion2)

        self.assertTrue(Motion.objects.all()[0].archived)  # prev motion is archived
        self.browser.get(self.live_server_url + home)
        self.navigate_to_motion(mocion2_link, mocion2_text)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, no_amendments)))
        self.assertEqual(no_amendments_text, self.browser.find_element_by_xpath(no_amendments).text)

        # staff member amends motion
        self.amendment = Amendment(motion_amended=self.motion2)
        self.amendment.assembly = self.assembly1
        self.amendment.motion_text = 'amendando porque capstone es lo mejor del mundo'
        self.amendment.save()
        self.choices_creation(self.amendment)

        self.browser.refresh()
        # view amendment details
        self.browser.find_element_by_xpath('/html/body/main/li/a').click()
        self.assertEqual('Voting is not open at the moment',
                         self.browser.find_element_by_xpath('/html/body/main/h3').text)

        # staff member opens voting
        self.amendment.voteable = True
        self.amendment.save()

        self.browser.refresh()

        # vote on amendment
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, a_favor_radio)))
        self.browser.find_element_by_xpath(a_favor_radio).click()
        self.browser.find_element_by_xpath(vote_button).click()

        # voting has conlcuded / closed by the cge through the admin side
        self.amendment.voteable = False
        self.amendment.save()

        # user navigates to results
        self.browser.refresh()
        self.assertEqual('a favor -- 1 vote', self.browser.find_element_by_xpath(a_favor_results).text)
        self.assertEqual('en contra -- 0 votes', self.browser.find_element_by_xpath(en_contra_results).text)

        # staff member updates motion with amendment and user votes on original motion now amended
        amendado_text = self.motion2.motion_text + ' AMENDADO: ' + self.amendment.motion_text
        self.motion2.motion_text = amendado_text
        self.motion2.save()
        self.navigate_to_motion(mocion2_link, amendado_text)
        self.assertEqual(amendado_text, self.browser.find_element_by_xpath('/html/body/main/h1').text)
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

    def choices_creation(self, motion):
        """
        helper method to create all 3 choices for a motion
        :param motion: motion without choices
        :return: n/a
        """
        Choice.objects.create(choice_text='a favor', motion=motion)
        Choice.objects.create(choice_text='en contra', motion=motion)
        Choice.objects.create(choice_text='abstenido', motion=motion)


    def test_cgeassembly(self):
        """
        method to test student user use case and an anonymous user trying to access information and vote on motions
        :return:
        """
        self.anon_user_run()
        self.student_user_run()

