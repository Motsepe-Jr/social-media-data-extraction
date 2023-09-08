import requests
from bs4 import BeautifulSoup
import time
import json
from data_lake.upload_data import upload_datafile
from datetime import datetime

base_url = 'https://kaenews.co.za/blog/category/crime'
max_pages = 50

FILE_PATH = '../datasets/news/kaenews_news.json'
CLOUD_PATH = f"exports/news/kaenews/{datetime.date}/{FILE_PATH}"

def scrape_article(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        title = soup.find('h1', class_='entry-title').text.strip()
    except Exception as e:
        title = 'No title'

    try:
        date = soup.find('span', class_='author-links').text.strip()
    except Exception as e:
        date = 'No date'

    try:
        paragraph = soup.find('div', class_='entry-content').text.strip()
    except Exception as e:
        paragraph = 'No Paragraph'

    return {
        'title': title,
        'date': date,
        'paragraph': paragraph
    }

def scrape_news_pages(base_url, max_pages):
    news_dataset = {}

    for i in range(1, max_pages + 1):
        url = f'{base_url}/page/{i}/'
        news_dataset[f'page_{i}'] = {'articles': []}

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        new_articles = soup.find_all('article')

        if not new_articles:
            break

        for article in new_articles:
            article_link = article.find('h3').find('a')['href']
            article_data = scrape_article(article_link)
            news_dataset[f'page_{i}']['articles'].append(article_data)
            time.sleep(2)

    return news_dataset

news_dataset = scrape_news_pages(base_url, max_pages)

with open(FILE_PATH, 'w') as file:
    json.dump(news_dataset, file, indent=2)
    file_uploaded = upload_datafile(FILE_PATH, CLOUD_PATH)
    if not file_uploaded:
        raise Exception("Could not upload file")