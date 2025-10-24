from config.settings import Config
import requests
from bs4 import BeautifulSoup
import json
import json


def scrape_data():
    print("Scraping data...")
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        ruless = json.load(file)

    for rules in ruless:
        paginatin = rules[Config.scraper_pagination]
        url = paginatin.replace("{page}", str(1))
        print(scrape_jobs(url, rules))


def scrape_jobs(url, rules):
    """
    Scrapes job listings from a given URL using configurable CSS selectors.

    Args:
        url (str): The URL of the page containing job listings.
        rules (dict): A dictionary containing CSS selectors for scraping.

    Returns:
        list: A list of dictionaries containing job data (index, url, title, company).
    """
    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract selectors from rules
    job_card_selector = rules[Config.scraper_job_card]
    job_url_selector = rules[Config.scraper_job_url]
    job_title_selector = rules[Config.scraper_job_title]
    company_name_selector = rules[Config.scraper_company_name]

    # Find all job card elements
    job_cards = soup.select(job_card_selector)

    # List to hold the extracted job data
    jobs_data = []

    for index, card in enumerate(job_cards):
        # Initialize a dictionary for the current job
        job_data = {
            'url': None,
            'title': None,
            'company': None
        }

        # Extract data using the selectors within the current card's scope
        url_element = card.select_one(job_url_selector)
        title_element = card.select_one(job_title_selector)
        company_element = card.select_one(company_name_selector)

        if url_element:
            job_data['url'] = url_element.get(
                'href')  # Get the 'href' attribute

        if title_element:
            job_data['title'] = title_element.get_text(
                strip=True)  # Get the text content (job title)

        if company_element:
            job_data['company'] = company_element.get_text(
                strip=True)  # Get the text content (company name)

        # Add the structured data dictionary for this job to the list
        if job_data['title'] != '' and job_data['url'] != '' and job_data['company'] != '':
            jobs_data.append(job_data)

    return jobs_data
