import requests
from bs4 import BeautifulSoup
import time
import json
import datetime
from data_lake.upload_data import upload_datafile


PLACES_PATH = 'datasets/datasets_places/location_dataset.json'
FILE_PATH = f'datasets/datasets_places/{datetime.day}/ewn_news_dataset.json'
CLOUD_PATH =  f"exports/news/ewn/{FILE_PATH}"

def load_location_dataset(filename):
    with open(filename, 'r') as file:
        return json.load(file)

class NewsScraper:
    def __init__(self, location_dataset):
        self.location_dataset = location_dataset
        self.news_dataset = {}

    def scrape_news(self):
        municipalities = list(self.location_dataset.keys())
        search_terms = self.generate_search_terms(municipalities)
        
        for search_term in search_terms:
            self.news_dataset[search_term] = {}
            for i in range(1, 4):
                url = self.generate_url(search_term, i)
                news_data = self.scrape_page(url)
                if not news_data:
                    break
                self.news_dataset[search_term][f'page_{i}'] = news_data
                time.sleep(3)
    
    def generate_search_terms(self, municipalities):
        search_terms = []
        for municipality in municipalities:
            for sub_area in self.location_dataset[municipality].keys():
                if sub_area == 'Johannesburg':
                    for section in self.location_dataset[municipality][sub_area]['sections']:
                        search_terms.append(section.lower())
                search_terms.append(sub_area.lower())
        return search_terms
    
    def generate_url(self, search_term, page_number):
        return f'https://ewn.co.za/searchresultspage?searchTerm={search_term}&type=All&sortBy=Relevance&pageNumber={page_number}&perPage=18'
    
    def scrape_page(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        new_articles = soup.find_all('article', class_='article-short')
        
        articles_data = []
        for article in new_articles:
            article_link = article.find('a')['href']
            article_data = self.scrape_article(article_link)
            if article_data:
                articles_data.append(article_data)
        
        return {'articles': articles_data}
    
    def scrape_article(self, article_link):
        article_link_response = requests.get(article_link)
        soup = BeautifulSoup(article_link_response.text, 'html.parser')
        article_content = soup.find('article', class_='article-full')
        
        if not article_content:
            return None
        
        try:
            title = article_content.find('h1').text
        except AttributeError:
            title = "No title found"

        try:
            summary = article_content.find('p', class_='lead').text
        except AttributeError:
            summary = "No summary found"

        try:
            article_topics = article_content.find('div', class_='article-topics').text
        except AttributeError:
            article_topics = "No topics found"

        try:
            article_date = article_content.find('abbr', class_='dateago').text
        except AttributeError:
            article_date = "No date found"
        
        article_body = [content.text.strip() for content in article_content.find_all('p') if content]
        
        return {
            'title': title.strip(),
            'summary': summary.strip(),
            'article_topics': article_topics.strip().split('\n'),
            'article_date': article_date.strip(),
            'article_body': ' '.join(article_body),
        }
    
    
location_dataset = load_location_dataset(PLACES_PATH)
scraper = NewsScraper(location_dataset)
scraper.scrape_news()

news_data = scraper.news_dataset

with open(FILE_PATH, 'w') as file:
    json.dump(news_data, file, indent=2)
    file_uploaded = upload_datafile(FILE_PATH, CLOUD_PATH)
    if not file_uploaded:
        raise Exception("Could not upload file")
