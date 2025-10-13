import os
import time
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.base_menu import BaseMenu
import re
from tinydb import TinyDB, Query

console = Console()


class ScraperMenu(BaseMenu):
    def execute(self):
        self.clear_screen()
        console.print("--- SCRAPE DATA ---", style="bold magenta")
        console.print("Starting scraping workflow...", style="cyan")
        time.sleep(0.5)

        try:
            # Step 1: Load configuration and scraper rules
            from config.settings import Config
            if not os.path.exists(Config.scraper_rules):
                console.print(
                    "Error: scraper_rules.json not found. Please run 'Generate Scraper Rules' first.", style="bold red")
                self.wait_for_input()
                return

            with open(Config.scraper_rules, 'r', encoding='utf-8') as f:
                rules = json.load(f)

            console.print("Step 1: Collecting job URLs", style="yellow")
            job_urls = self.collect_job_urls(Config.job_sites, rules)

            console.print(f"Collected {len(job_urls)} job URLs", style="green")
            time.sleep(1)

            console.print(
                "Step 2: Scraping raw text data for LLM processing", style="yellow")
            raw_text_data = self.scrape_raw_text_data(job_urls)

            console.print(f"Scraped raw text from {
                          len(raw_text_data)} pages", style="green")
            self.save_raw_text_to_tinydb(raw_text_data)

            console.print(
                "Scraping completed successfully! Raw text stored in TinyDB for later LLM processing.", style="bold green")
        except Exception as e:
            console.print(f"Scraping failed: {str(e)}", style="bold red")

        self.wait_for_input()

    def collect_job_urls(self, job_sites, rules):
        all_job_urls = []

        for site_url in job_sites:
            site_name = self.get_site_name(site_url)
            console.print(f"Collecting URLs from {site_name}...", style="cyan")

            if site_name not in rules:
                console.print(f"Warning: No rules found for {
                              site_name}, skipping.", style="yellow")
                continue

            site_rules = rules[site_name]
            job_list_selector = site_rules.get("job_list_selector")
            pagination_pattern = site_rules.get("pagination_pattern")

            if not job_list_selector:
                console.print(f"Warning: No job_list_selector for {
                              site_name}, skipping.", style="yellow")
                continue

            # Collect URLs from first few pages
            page = 1
            while True:
                if pagination_pattern:
                    current_url = pagination_pattern.format(n=page)
                else:
                    current_url = f"{site_url.strip()}?page={
                        page}" if page > 1 else site_url.strip()

                try:
                    response = requests.get(current_url, timeout=10)
                    if response.status_code != 200:
                        break  # No more pages

                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_elements = soup.select(job_list_selector)

                    if not job_elements:
                        break  # No more jobs on this page

                    for elem in job_elements:
                        link_elem = elem.find('a')
                        if link_elem and link_elem.get('href'):
                            full_url = urljoin(site_url, link_elem['href'])
                            all_job_urls.append(full_url)

                    page += 1
                    if page > 3:  # Limit to first 3 pages as per requirements
                        break

                    time.sleep(1)  # Be respectful to the server

                except Exception as e:
                    console.print(f"Error collecting URLs from {
                                  current_url}: {str(e)}", style="red")
                    break

        return list(set(all_job_urls))  # Return unique URLs

    def scrape_raw_text_data(self, job_urls):
        raw_text_data = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Scraping raw text from job pages...", total=len(job_urls))

            for url in job_urls:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code != 200:
                        continue

                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract all text from the page
                    all_text = []

                    # Get all text from common text-containing elements
                    for element in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'article', 'section']):
                        text = element.get_text(strip=True)
                        if text and len(text) > 10:  # Only include substantial text
                            all_text.append(text)

                    # Also get the full text content of the body
                    body_text = soup.get_text(separator=' ', strip=True)
                    if body_text and len(body_text) > 50:
                        all_text.append(body_text)

                    # Remove duplicates while preserving order
                    unique_texts = []
                    seen = set()
                    for text in all_text:
                        if text not in seen:
                            seen.add(text)
                            unique_texts.append(text)

                    raw_text_data.append({
                        "url": url,
                        "site_name": self.get_site_name(url),
                        "raw_text_items": unique_texts,
                        "scraped_at": time.time()
                    })

                except Exception as e:
                    console.print(f"Error scraping {url}: {
                                  str(e)}", style="red")

                progress.update(task, advance=1)
                time.sleep(0.5)  # Be respectful

        return raw_text_data

    def save_raw_text_to_tinydb(self, raw_text_data):
        # Initialize TinyDB
        db = TinyDB('raw_job_data.json')

        # Insert each raw text entry as a document
        for entry in raw_text_data:
            # Use TinyDB's insert method to store the raw text data
            db.insert(entry)

        console.print(f"Saved {len(raw_text_data)
                               } raw text entries to TinyDB", style="green")

    def get_site_name(self, url):
        """Extract a simple site name from URL for rule matching"""
        parsed = urlparse(url)
        hostname = parsed.hostname or parsed.path.split('/')[0]
        # Remove common prefixes like www, m, etc.
        hostname = re.sub(r'^(www|m)\.', '', hostname)
        # Remove .md, .com, etc.
        hostname = re.sub(r'\.(md|com|ro)$', '', hostname)
        return hostname
