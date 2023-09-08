from twitter_scraper_selenium.profile import scrape_profile
import time
#todo: check delted files profile.py
twitter_accounts = [
    "SAPoliceService",
    "Fidelity_Secure",
    "VehicleTrackerz",
    "Fidelity_Secure",
    "Abramjee",
    "sa_crime",
    "BEAST_OF_NEWS",
    "ExposingCrimeSA",
    "crimewatch202",
    "JoburgMPD",
    "TMPDSafety",
    "KasiCrime",
]

def scrape_account(username):
    profile = scrape_profile(
        twitter_username=username,
        output_format="csv",
        browser="chrome",
        tweets_count=300000,
        headless=False
    )

for account in twitter_accounts:
    scrape_account(account)
    time.sleep(60 * 3)
