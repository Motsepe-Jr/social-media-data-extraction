from facebook.driver_initialization import Initializer
from selenium.webdriver.common.by import By

import time
from datetime import datetime
import json

from data_lake.upload_data import upload_datafile

import concurrent.futures
import threading


NEWS_DATASETS = {}
FILE_PATH = '../datasets/news/kaenews_news.json'
CLOUD_FILE_PATH = f"exports/news/multi_news/{datetime.date}/{FILE_PATH}"

def initialize_driver():
    return Initializer(browser_name='chrome', headless=True).init()

def load_news_links():
    NEWS_LINKS_PATH = '../ID_datasets/news_links/news_link.json'
    with open(NEWS_LINKS_PATH, 'r') as json_file:
        return json.load(json_file)

def collect_news_data(city_name, city_url, lock):
    driver = initialize_driver()
    try:
        
        NEWS_DATASETS[city_name] = []

        links_list = []
        for page_number in range(5):
            print(f"Scraping {city_name} - Page {page_number}")
            time.sleep(2)
            try:
                driver.get(f"{city_url}page/{page_number}/")
            except Exception as e:
                print(f"Error loading page {page_number}: {e}")
                driver = initialize_driver()
                try:
                    driver.get(f"{city_url}page/{page_number}/")
                except Exception as e:
                    continue

            try:
                article_element = driver.find_element(By.ID, "posts-container")
                article_links = article_element.find_elements(By.TAG_NAME, 'li')
                for link in article_links:
                    try:
                        links_element = link.find_element(By.TAG_NAME, 'a')
                        link_url = links_element.get_attribute("href")
                        links_list.append(link_url)
                    except Exception as e:
                        continue
            except Exception as e:
                break

        for link in links_list:
            print(f"Scraping article: {link}")
            time.sleep(3)
            try:
                driver.get(link)
            except Exception as e:
                print(f"Error loading article {link}: {e}")
                driver = initialize_driver()
                try:
                    driver.get(link)
                except Exception as e:
                    continue

            try:
                entry_header = driver.find_element(By.CLASS_NAME, 'entry-header')
                date = entry_header.find_element(By.CLASS_NAME, 'date').text
                title = entry_header.find_element(By.CLASS_NAME, 'post-title').text
                summary = entry_header.find_element(By.CLASS_NAME, 'entry-sub-title').text
            except Exception as e:
                date = 'No date'
                title = 'No title'
                summary = 'No Summary'

            try:
                p_tags = driver.find_elements(By.CSS_SELECTOR, '.entry-content p')
                paragraphs = [p.text for p in p_tags]
                paragraphs = ' '.join(paragraphs).strip()
            except Exception as e:
                paragraphs = 'No Paragraphs'

            with lock:
                NEWS_DATASETS[city_name].append({
                    'title': title,
                    'date': date,
                    'paragraphs': paragraphs,
                    'summary': summary
                })

        time.sleep(2)
    finally:
        driver.quit()

def data_collection_news(search_terms):
    lock = threading.Lock()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for city_name, city_url in search_terms.items():
            futures.append(executor.submit(collect_news_data, city_name, city_url, lock))
        
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    search_terms = load_news_links()
    data_collection_news(search_terms)
    file_uploaded = upload_datafile(FILE_PATH, CLOUD_FILE_PATH)
    if not file_uploaded:
        raise Exception("Could not upload file")



