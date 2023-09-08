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
    def login(driver, URL) -> None:
        """Login into the system 
        """
        wait = WebDriverWait(driver, 10)

        driver.get(URL)

        time.sleep(2)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="text"]'))).send_keys("...email...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][contains(.,'Next')]"))).click()

        try:
            time.sleep(2)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="text"]'))).send_keys("..password...")
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][contains(.,'Next')]"))).click()
            time.sleep(2)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="password"]'))).send_keys("..password...")
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][contains(.,'Log in')]"))).click()
            time.sleep(2)

        except:
            time.sleep(2)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="password"]'))).send_keys("..password..")
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][contains(.,'Log in')]"))).click()
    
    @staticmethod 
    def search_for_tweets(driver, serach_query) -> None:
        """
        search tweet based on the search query
        """
        time.sleep(3)
        wait = WebDriverWait(driver, 10)
        search_element = driver.find_element(By.XPATH,
                                                    '//input[@aria-label="Search query"]')
        search_element.send_keys(Keys.CONTROL + "a")
        search_element.send_keys(Keys.DELETE)
        search_element.send_keys(serach_query)
        search_element.send_keys(Keys.ENTER)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@role='tab'][contains(.,'Latest')]"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@class='css-1dbjc4n r-1loqt21 r-oyd9sg'][contains(.,'Near you')]"))).click()

    @staticmethod
    def wait_until_tweets_appear(driver) -> None:
        """Wait for tweet to appear. Helpful to work with the system facing
        slow internet connection issues
        """
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="tweet"]')))
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
                time.sleep(randint(3, 5))
                state = driver.execute_script("return document.readyState")
        except Exception as ex:
            logger.exception('Error at wait_until_completion: {}'.format(ex))
