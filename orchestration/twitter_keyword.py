from twitter_scraper_selenium.keyword import scrape_keyword
import time, json, re


#todo: check delted files 

search_terms =  []
search_terms_bank_terms = [] # 'capitec scam','fnb scam',

def read_set_from_json():
    with open('twitter_keyword_search.json', 'r') as json_file:
        data = json.load(json_file)
        return set(data)

twitter_keyword_search_written = read_set_from_json()


def remove_numbers_and_ext(text):
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Remove "ext"
    text = re.sub(r'\bext\b', '', text, flags=re.IGNORECASE)

    text = re.sub(r'\bsp\b', '', text, flags=re.IGNORECASE)

    text = re.sub(r'\bah\b', '', text, flags=re.IGNORECASE)

    return text

def load_location_dataset(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

location_dataset = load_location_dataset('locations/location_dataset.json')
municipalities = list(location_dataset.keys())

twitter_sub_areas = set()
for municipality in municipalities:
    for sub_area in location_dataset[municipality].keys():
        for sections in location_dataset[municipality][sub_area]['sections']:
            twitter_sub_areas.add(sub_area)

twitter_keyword_search_write = set()
search_terms_bank_terms = set(search_terms_bank_terms)

# twitter_sub_areas.update(search_terms_bank_terms)

# for section in twitter_sub_areas:
for search_term in search_terms:
    # if section not in search_terms_bank_terms:
    #     section = remove_numbers_and_ext(section).strip()
    #     place_ = f'{search_term} {section}'.lower()
    # else:
    #     place_ = section

    # if place_ in twitter_keyword_search_written or 'discovery' in place_ or 'tornado' in place_ or 'comet' in place_ or 'satmar' in place_ or 'tunney' in place_ or 'kensington' in place_ or 'apex' in place_ or 'norscot' in place_ or 'selby' in place_ or  'petit' in place_ or 'florida' in place_ or 'selection' in place_ or 'cambria' in place_:
    #     continue

    # if '/' in place_:
    #     place_ = place_.replace('/', ' ')

    twitter_keyword_search_write.add(search_term)
        
twitter_keyword_search_write.update(search_terms_bank_terms)       
twitter_keyword_search_write = list(twitter_keyword_search_write)


keywords = scrape_keyword(
    keywords=twitter_keyword_search_write,
    output_format="csv",
    browser="chrome",
    tweets_count=3000000,
    headless=False
)

