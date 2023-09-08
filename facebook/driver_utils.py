#!/usr/bin/env python3
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException
import time
from selenium.webdriver.common.keys import Keys
from random import randint
import logging

logger = logging.getLogger(__name__)
format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(format)
logger.addHandler(ch)


class Utilities:
    """
    this class contains all the method related to driver behaviour,
    like scrolling, waiting for element to appear, it contains all static
    method, which accepts driver instance as a argument

    @staticmethod
    def method_name(parameters):
    """

    @staticmethod
    def login(driver, url):
        """"
        Login into the system. Helfull to wait for the page to load
        """
        driver.get(url)
        driver.maximize_window()

        time.sleep(3)
        user_name = driver.find_element(By.XPATH,
                                        "//input[@type='text']")
        # TODOl Remove passwords // and TRY
        user_name.send_keys('....helton phone....')

        password = driver.find_element(By.XPATH,
                                       "//input[@placeholder='Password']")
        # TODOl Remove passwords // and TRY
        password.send_keys('...name....')

        login_button =  driver.find_element(By.XPATH,"//button[@type='submit']")
        login_button.click()
        time.sleep(3)

        return driver

    @staticmethod
    def wait_until_posts_appear(driver) -> None:
        """Wait for tweet to appear. Helpful to work with the system facing
        slow internet connection issues
        """
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, "//div[@class='x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z']")))
        except WebDriverException:
            logger.exception(
                "Tweets did not appear!, Try setting headless=False to see what is happening")

    @staticmethod
    def scroll_down(driver) -> None:
        """Helps to scroll down web page"""
        try:
            body = driver.find_element(By.CSS_SELECTOR, 'body')
            for _ in range(randint(4, 7)):
                body.send_keys(Keys.PAGE_DOWN)
        except Exception as ex:
            logger.exception("Error at scroll_down method {}".format(ex))

    @staticmethod
    def wait_until_completion(driver) -> None:
        """waits until the page have completed loading"""
        try:
            state = ""
            while state != "complete":
                time.sleep(randint(1,3))
                state = driver.execute_script("return document.readyState")
        except Exception as ex:
            logger.exception('Error at wait_until_completion: {}'.format(ex))
