from config.settings import Config
import json


def scrape_data():
    print("Scraping data...")
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        site_rules = json.load(file)
