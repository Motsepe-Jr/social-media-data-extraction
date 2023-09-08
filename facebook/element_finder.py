#!/usr/bin/env python3

from typing import Union
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from dateutil.parser import parse
from selenium.webdriver.common.by import By
import logging
import time
import re
import datetime
logger = logging.getLogger(__name__)
format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(format)
logger.addHandler(ch)


class Finder:
    """
    this class should contain all the static method to find that accept
    webdriver instance and perform operation to find elements and return the
    found element.
    method should follow convention like so:

    @staticmethod
    def method_name(parameters):
    """
    
    @staticmethod
    def search_posts(search_term, driver):
        """search for posts on and get results
        """
        search_element = driver.find_element(By.XPATH,
                                             "//input[@aria-label='Search Facebook']")
        search_element.send_keys(Keys.CONTROL + "a")
        search_element.send_keys(Keys.DELETE)
        search_element.send_keys(search_term)
        search_element.send_keys(Keys.ENTER)
        time.sleep(3)

        return driver
    
    @staticmethod
    def get_all_posts(driver):
        """
        Return Posts and Dates
        """
        feed_data = driver.find_elements(By.XPATH, 
                                         "//div[@class='x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z']")

        return feed_data
    
    @staticmethod
    def get_posts_dates(driver):
        """
        Returns Posts Date if the Posts
        """
        dates = driver.find_elements(By.XPATH, 
                                     "//div[@class='__fb-light-mode']")
        
        return dates
    
    @staticmethod
    def process_dates(dates):
        """
        Return dates in a set to avoid duplication
        """
        date_set = set()
        for date in dates:
            try:
                data = date.find_element(By.TAG_NAME, 'text')
                innerHTML = data.get_attribute("innerHTML")
                if re.search(r'\d', innerHTML):
                    date_set.add(innerHTML)
            except:
                pass
                print("Failed to process dates") 
        return list(date_set)
    
    @staticmethod
    def get_posts_names(feed_data):
        """
        Return post names 
        """
        post_names = []
        for feed in feed_data:
            try:
                post_name = feed.find_element(By.TAG_NAME, "strong")
                post_names.append(post_name.text)
            except:
                pass
                print("Failed to process feed data") 
        return post_names
    
    @staticmethod
    def get_posts_text(feed_data):
        """
        Return post names 
        """
        post_texts = []
        for feed in feed_data:
            try:
                post_name = feed.find_element(
                    By.CSS_SELECTOR, '[data-ad-preview="message"]')
                if post_name.text:
                    post_texts.append(post_name.text)
            except:
                pass
                print("Failed to process feed text") 
        return post_texts
    
    @staticmethod
    def get_current_date(feed_data):
        """
        get current  date for each feed
        """
        return [datetime.date.today()] *  len(feed_data)




   
