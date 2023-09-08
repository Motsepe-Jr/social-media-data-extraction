import requests
from bs4 import BeautifulSoup
import json
from data_lake import upload_datafile

BASE_URL = 'https://census2011.adrianfrith.com'
FILENAME = 'location_dataset.json'
NEWS_EXPORT_PATH = f"/datasets/news/{FILENAME}"
NEWS_KEY_NAME = f"exports/news/{NEWS_EXPORT_PATH}"

def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_table_links(soup):
    table = soup.find_all('table', {'class': 'table'})[-1]
    links = table.find_all('a')
    sub_area = [l.text for l in links]
    return links, sub_area

def get_place_info(link):
    full_url = BASE_URL + link['href']
    soup = get_soup(full_url)
    table = soup.find_all('table', {'class': 'table'})[-1]
    link1 = table.find_all('a')
    place_names = [l.text for l in link1]
    place_links = [l['href'] for l in link1]
    
    population_tags = table.find_all(class_='text-right')[::2]
    population_values = [tag.text.replace(',', '') for tag in population_tags]
    area_tags = table.find_all(class_='text-right')[1::2]
    area_values = [tag.text for tag in area_tags]
    
    return place_names, place_links, population_values[1:], area_values[1:]

def save_location_dataset(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)
    
    return True


municipalities = {
    'City of Johannesburg': f'{BASE_URL}/place/798',
    'Ekurhuleni': f'{BASE_URL}/place/797'
}


location_dataset = {
    
}

for municipality, url in municipalities.items():
  soup = get_soup(url)
  links, sub_area = get_table_links(soup)

  if len(links) != len(sub_area):
    raise Exception("links and area must have same length")

  sub_area_dataset = {}
  for i, link in enumerate(links):
      place_names, place_links, population_values, area_values = get_place_info(link)

      if len(place_names) != len(population_values) or len(place_names) != len(area_values):
        raise Exception("place names, populations and area must have same length")

      sub_area_dataset[sub_area[i]] = {
          'sections': place_names,
          'place_links': place_links,
          'population': population_values,
          'area': area_values
      }


  location_dataset[municipality] = sub_area_dataset
  

location_dataset_saved = save_location_dataset(location_dataset, NEWS_EXPORT_PATH)

if location_dataset_saved:
   location_dataset_uploaded = upload_datafile(NEWS_EXPORT_PATH, NEWS_KEY_NAME)
   if not location_dataset_uploaded:
      raise  Exception("Could not upload location dataset")
else:
   raise Exception("Could not save location dataset")
   