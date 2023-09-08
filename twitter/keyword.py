#!/usr/bin/env python3

from typing import Union
from .driver_initialization import Initializer
from .driver_utils import Utilities
from .element_finder import Finder
import re
import json
import os
import csv
from twitter.scraping_utilities import Scraping_utilities
import logging
import time
from random import randint

logger = logging.getLogger(__name__)
format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(format)
logger.addHandler(ch)


class Keyword:
    """This class needs to be instantiated in order to find something
    on twitter related to keywords"""

    def __init__(self, keywords: str, browser: str, filename:str, directory:str,  proxy: Union[str, None], tweets_count: int, url: Union[str, None], headless: bool):
        """Scrape Tweet using keyword.

        Args:
            keyword (str): Keyword to search on twitter.
            browser (str): Which browser to use for scraping?, Only 2 are supported Chrome and Firefox,default is set to Firefox.
            proxy (Union[str, None]): Optional parameter, if user wants to use proxy for scraping. If the proxy is authenticated proxy then the proxy format is username:password@host:port
            tweets_count (int): Number of tweets to scrap
            url (Union[str, None]): URL of the webpage.
            headless (bool): Whether to run browser in headless mode?.
        """
        self.keywords = keywords
        self.URL = url
        self.driver = ""
        self.browser = browser
        self.proxy = proxy
        self.tweets_count = tweets_count
        self.posts_data = {}
        self.retry = 5
        self.prev_retry = 4
        self.headless = headless
        self.tweets_id = set()
        self.filename = filename
        self.directory = directory


    def start_driver(self):
        """changes the class member driver value to driver on call"""
        self.driver = Initializer(
            self.browser, self.headless, self.proxy).init()

    def close_driver(self):
        self.driver.close()
        self.driver.quit()

    def check_tweets_presence(self, tweet_list):
        if len(tweet_list) <= 0:
            self.retry -= 1

    def check_retry(self):
        return self.retry <= 0
    
    def write_tweet_id(self):

        with open('tweet_ids.json', 'r') as file:
            tweet_ids_dict = json.load(file)
            
        tweet_ids_set = set(tweet_ids_dict['tweetIds'])

        tweet_ids_set.update(self.tweets_id)

        self.tweets_id = tweet_ids_set

        tweet_ids_dict = {'tweetIds': list(tweet_ids_set)}

        # Write the tweetIds dictionary to a JSON file
        with open('tweet_ids.json', 'w') as file:
            json.dump(tweet_ids_dict, file)

        print('Updated tweetIds')

    def fetch_and_store_data(self):
        try:
            self.write_tweet_id()
            all_ready_fetched_posts = []
            present_tweets = Finder.find_all_tweets(self.driver)
            self.check_tweets_presence(present_tweets)
            all_ready_fetched_posts.extend(present_tweets)

            print(len(self.posts_data), len(all_ready_fetched_posts))

            while len(self.posts_data) < self.tweets_count:

                for tweet in present_tweets:
                    status, tweet_url = Finder.find_status(tweet)
                    if tweet_url:
                        tweet_id = tweet_url.split("/")[5]
                        if int(tweet_id) in self.tweets_id or tweet_id in self.tweets_id:
                            continue
                        else:
                            self.tweets_id.add(tweet_id)
                    else:
                        continue
                    name = Finder.find_name_from_tweet(tweet)
                    replies = Finder.find_replies(tweet)
                    retweets = Finder.find_shares(tweet)
                    username = tweet_url.split("/")[3]
                    status = status[-1]
                    is_retweet = Finder.is_retweet(tweet)
                    posted_time = Finder.find_timestamp(tweet)
                    content = Finder.find_content(tweet)
                    likes = Finder.find_like(tweet)
                    images = Finder.find_images(tweet)
                    videos = Finder.find_videos(tweet)
                    hashtags = re.findall(r"#(\w+)", content)
                    mentions = re.findall(r"@(\w+)", content)
                    profile_picture = Finder.find_profile_image_link(tweet)
                    link = Finder.find_external_link(tweet)

                    self.posts_data[status] = {
                        "tweet_id": status,
                        "username": username,
                        "name": name,
                        "profile_picture": profile_picture,
                        "replies": replies,
                        "retweets": retweets,
                        "likes": likes,
                        "is_retweet": is_retweet,
                        "posted_time": posted_time,
                        "content": content,
                        "hashtags": hashtags,
                        "mentions": mentions,
                        "images": images,
                        "videos": videos,
                        "tweet_url": tweet_url,
                        "link": link
                    }

                Utilities.scroll_down(self.driver)
                Utilities.wait_until_completion(self.driver)
                Utilities.wait_until_tweets_appear(self.driver)
                present_tweets = Finder.find_all_tweets(
                    self.driver)
                present_tweets = [
                    post for post in present_tweets if post not in all_ready_fetched_posts]
                if self.prev_retry == self.retry:
                    self.write_tweet_id()
                    self.prev_retry -= 1
                self.check_tweets_presence(present_tweets)
                all_ready_fetched_posts.extend(present_tweets)
                time.sleep(randint(3, 5))
                if self.check_retry() is True:
                    break

        except Exception as ex:
            logger.exception(
                "Error at method fetch_and_store_data : {}".format(ex))

    def scrap(self):
        try:
            self.start_driver()
            Utilities.login(self.driver, self.URL)

            for keyword in self.keywords:
                self.filename = keyword
                set_filename = read_set_from_json()
                set_filename.add(self.filename)
                Utilities.search_for_tweets(self.driver, keyword)
                Utilities.wait_until_completion(self.driver)
                Utilities.wait_until_tweets_appear(self.driver)
                self.tweets_id = set()
                self.posts_data = {}
                self.retry = 5
                self.prev_retry = 4
                self.fetch_and_store_data()
                data = dict(list(self.posts_data.items())
                            [0:int(self.tweets_count)])
                json_to_csv(filename=self.filename, json_data=data, directory=self.directory)
                write_set_to_json(set_filename)
                print(f'done extrcating data for keyword {keyword}')
            self.close_driver()
            return

        except Exception as ex:
            self.close_driver()
            logger.exception(
                "Error at method scrap on : {}".format(ex))


def read_set_from_json():
    with open('twitter_keyword_search.json', 'r') as json_file:
        data = json.load(json_file)
        return set(data)
    
def write_set_to_json(data_set):
    with open('twitter_keyword_search.json', 'w') as json_file:
        json.dump(list(data_set), json_file)

def json_to_csv(filename, json_data, directory):
    os.chdir(directory)  # change working directory to given directory
    # headers of the CSV file
    fieldnames = ['tweet_id', 'username', 'name', 'profile_picture', 'replies',
                  'retweets', 'likes', 'is_retweet', 'posted_time', 'content', 'hashtags', 'mentions',
                  'images', 'videos', 'tweet_url', 'link']
    mode = 'w'
    # open and start writing to CSV files
    if os.path.exists("{}.csv".format(filename)):
        mode = 'a'
    with open("{}.csv".format(filename), mode, newline='', encoding="utf-8") as data_file:
        # instantiate DictWriter for writing CSV fi
        writer = csv.DictWriter(data_file, fieldnames=fieldnames)
        if mode == 'w':
            writer.writeheader()  # write headers to CSV file
        # iterate over entire dictionary, write each posts as a row to CSV file
        for key in json_data:
            # parse post in a dictionary and write it as a single row
            row = {
                "tweet_id": key,
                "username": json_data[key]['username'],
                "name": json_data[key]['name'],
                "profile_picture": json_data[key]['profile_picture'],
                "replies": json_data[key]['replies'],
                "retweets": json_data[key]['retweets'],
                "likes": json_data[key]['likes'],
                "is_retweet": json_data[key]['is_retweet'],
                "posted_time": json_data[key]['posted_time'],
                "content": json_data[key]['content'],
                "hashtags": json_data[key]['hashtags'],
                "mentions": json_data[key]['mentions'],
                "images": json_data[key]['images'],
                "videos": json_data[key]['videos'],
                "tweet_url": json_data[key]['tweet_url'],
                "link": json_data[key]['link']

            }
            writer.writerow(row)  # write row to CSV fi
        data_file.close()  # after writing close the file
    logger.setLevel(logging.INFO)
    logger.info('Data Successfully Saved to {}.csv'.format(filename))


def scrape_keyword(keywords: list, browser: str = "firefox", until: Union[str, None] = None,
                  since: Union[int, None] = None, since_id: Union[int, None] = None, max_id: Union[int, None] = None,
                  within_time: Union[str, None] = None,
                  proxy: Union[str, None] = None, tweets_count: int = 10, output_format: str = "csv",
                  filename: str = "", directory: str = os.getcwd(), headless: bool = True, 
                  URL = 'https://twitter.com/i/flow/login'):
    """Scrap tweets using keywords.

    Args:
        keyword (str): Keyword to search on twitter.
        browser (str, optional): Which browser to use for scraping?, Only 2 are supported Chrome and Firefox,default is set to Firefox. Defaults to "firefox".
        until (Union[str, None], optional): Optional parameter,Until date for scraping,a end date from where search ends. Format for date is YYYY-MM-DD or unix timestamp in seconds. Defaults to None.
        since (Union[int, None], optional): Optional parameter,Since date for scraping,a past date from where to search from. Format for date is YYYY-MM-DD or unix timestamp in seconds. Defaults to None.
        since_id (Union[int, None], optional): After (NOT inclusive) a specified Snowflake ID. Defaults to None.
        max_id (Union[int, None], optional): At or before (inclusive) a specified Snowflake ID. Defaults to None.
        within_time (Union[str, None], optional): Search within the last number of days, hours, minutes, or seconds. Defaults to None.
        proxy (Union[str, None], optional): Optional parameter, if user wants to use proxy for scraping. If the proxy is authenticated proxy then the proxy format is username:password@host:port. Defaults to None.
        tweets_count (int, optional): Number of posts to scrap. Defaults to 10.
        output_format (str, optional): The output format, whether JSON or CSV. Defaults to "json".
        filename (str, optional): If output parameter is set to CSV, then it is necessary for filename parameter to passed. If not passed then the filename will be same as keyword passed. Defaults to "".
        directory (str, optional): If output parameter is set to CSV, then it is valid for directory parameter to be passed. If not passed then CSV file will be saved in current working directory. Defaults to current work directory.
        headless (bool, optional): Whether to run browser in Headless Mode?. Defaults to True.

    Returns:
        str: tweets data in CSV or JSON
    """
    print('started scrap...', tweets_count, keywords[0])
    
    keyword_bot = Keyword(keywords, browser=browser, url=URL, filename=filename, directory=directory, 
                          proxy=proxy, tweets_count=tweets_count, headless=headless)
    keyword_bot.scrap()

    print('Completed Data Extraction')

    return 

