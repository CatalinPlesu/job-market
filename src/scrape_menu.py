from .base_menu import BaseMenu
from rich.console import Console
from rich.table import Table
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
from datetime import datetime
import sqlite3
import requests
import asyncio
import aiohttp
import time
import json
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

console = Console()


class ScrapeMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        self.db_path = "raw.db"
        self.state_path = "scraper_state.json"
        self.state_db = TinyDB(self.state_path)
        self.state = self.load_state()
        self.config = self.load_config()
        self.init_sqlite()

    def load_config(self):
        from config.settings import Config

        return Config

    def init_sqlite(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # URLs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                origin TEXT NOT NULL,
                collected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP,
                next_check_date TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        """)

        # Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                origin TEXT NOT NULL,
                bodyText TEXT,
                scraped_date TIMESTAMP,
                status TEXT,
                last_updated TIMESTAMP,
                FOREIGN KEY (url) REFERENCES urls(url)
            )
        """)

        conn.commit()
        conn.close()

    def load_state(self):
        """Load scraper state from TinyDB JSON"""
        table = self.state_db.table("scraper_state")
        records = table.all()
        if records:
            return records[0]

        default_state = {"last_run": None, "total_urls_collected": 0, "sites": {}}
        table.insert(default_state)
        return default_state

    def save_state(self):
        """Save scraper state to TinyDB JSON"""
        table = self.state_db.table("scraper_state")
        table.truncate()
        table.insert(self.state)

    def get_robots_delay(self, site_url):
        """Parse robots.txt to get crawl delay"""
        try:
            base_url = f"{urljoin(site_url, '/').rstrip('/')}"
            robots_url = f"{base_url}/robots.txt"
            response = requests.get(robots_url, timeout=5)

            if response.status_code == 200:
                for line in response.text.split("\n"):
                    if line.lower().startswith("crawl-delay:"):
                        delay = float(line.split(":")[1].strip())
                        console.print(f"  [cyan]Found Crawl-Delay: {delay}s[/cyan]")
                        return delay

            console.print(f"  [yellow]No Crawl-Delay in robots.txt, using default 1s[/yellow]")
            return 1.0
        except Exception as e:
            console.print(
                f"  [yellow]Error reading robots.txt: {str(e)}, using default 1s[/yellow]"
            )
            return 1.0

    def binary_search_pages(self, pagination_url, max_page=500):
        """Use binary search to find max page count"""
        left, right = 1, max_page
        last_valid = 1

        while left <= right:
            mid = (left + right) // 2
            test_url = pagination_url.format(page=mid)

            try:
                response = requests.head(test_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    last_valid = mid
                    left = mid + 1
                else:
                    right = mid - 1
            except:
                right = mid - 1

        return last_valid

    def scrape_site_urls_sequential(self, site_name, pagination_url, selector, delay):
        """Scrape all URLs from one site sequentially, respecting delay"""
        console.print(f"\n[bold cyan]>>> {site_name}: Detecting max pages...[/bold cyan]")
        start_detect = time.time()
        max_pages = self.binary_search_pages(pagination_url)
        detect_time = time.time() - start_detect

        console.print(f"[green]✓ {site_name}: Found {max_pages} pages ({detect_time:.1f}s)[/green]")
        console.print(f"[yellow]  Scraping with {delay}s delay per page[/yellow]")

        collected_urls = []
        start_scrape = time.time()

        for page in range(1, max_pages + 1):
            url = pagination_url.format(page=page)

            try:
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    console.print(
                        f"[yellow]  {site_name}: Page {page} returned {
                            response.status_code
                        }, stopping[/yellow]"
                    )
                    break

                soup = BeautifulSoup(response.content, "html.parser")
                job_links = soup.select(selector)

                if not job_links:
                    console.print(
                        f"[yellow]  {site_name}: No jobs found on page {page}, stopping[/yellow]"
                    )
                    break

                for link in job_links:
                    href = link.get("href")
                    if href:
                        full_url = urljoin(url, href)
                        collected_urls.append(full_url)

                console.print(
                    f"[cyan]  {site_name}: Page {page}/{max_pages} - {len(job_links)} jobs[/cyan]"
                )
                time.sleep(delay)

            except Exception as e:
                console.print(f"[red]  {site_name}: Error on page {page}: {str(e)}[/red]")
                break

        scrape_time = time.time() - start_scrape
        return collected_urls, scrape_time, detect_time

    def store_urls(self, collected_urls, site_name):
        """Store URLs in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stored_count = 0
        skipped_count = 0

        for url in collected_urls:
            try:
                cursor.execute(
                    "INSERT INTO urls (url, origin, status) VALUES (?, ?, ?)",
                    (url, site_name, "pending"),
                )
                stored_count += 1
            except sqlite3.IntegrityError:
                skipped_count += 1

        conn.commit()
        conn.close()

        return stored_count, skipped_count

    async def scrape_job_detail(self, session, url, site_name):
        """Fetch and extract text from job detail page"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")

                    body_text = soup.get_text(separator=" ", strip=True)
                    body_text = re.sub(r"\s+", " ", body_text)[:5000]

                    return {
                        "url": str(url),
                        "origin": site_name,
                        "bodyText": body_text,
                        "scraped_date": datetime.now().isoformat(),
                        "status": "success",
                    }
        except Exception as e:
            return {
                "url": str(url),
                "origin": site_name,
                "bodyText": "",
                "scraped_date": datetime.now().isoformat(),
                "status": f"error: {str(e)}",
            }

    def scrape_site_details_sequential(self, site_name, urls, delay):
        """Scrape job details from one site sequentially"""
        results = []

        console.print(f"[cyan]>>> {site_name}: Scraping {len(urls)} job details...[/cyan]")
        start = time.time()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def fetch_all():
            async with aiohttp.ClientSession() as session:
                for idx, url in enumerate(urls):
                    result = await self.scrape_job_detail(session, url, site_name)
                    results.append(result)
                    if (idx + 1) % 10 == 0:
                        console.print(f"[cyan]  {site_name}: {idx + 1}/{len(urls)} jobs[/cyan]")
                    time.sleep(delay / 10)

        loop.run_until_complete(fetch_all())
        elapsed = time.time() - start

        return results, elapsed

    def store_jobs(self, results):
        """Store job details in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        success_count = 0
        error_count = 0

        for result in results:
            try:
                cursor.execute(
                    """INSERT INTO jobs (url, origin, bodyText, scraped_date, status)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        result["url"],
                        result["origin"],
                        result["bodyText"],
                        result["scraped_date"],
                        result["status"],
                    ),
                )
                if result["status"] == "success":
                    success_count += 1
                    cursor.execute(
                        "UPDATE urls SET status = ? WHERE url = ?", ("scraped", result["url"])
                    )
                else:
                    error_count += 1
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        conn.close()

        return success_count, error_count

    def process_site(self, rule):
        """Process one site completely (Stage 1 + 2)"""
        site_name = rule["name"]
        pagination = rule["pagination"]
        selector = rule["job-url-class-selector"]

        console.print(f"\n[bold magenta]═══ PROCESSING: {site_name} ═══[/bold magenta]")

        delay = self.get_robots_delay(pagination)
        stage1_start = time.time()

        # Stage 1: Collect URLs
        urls, stage1_scrape_time, detect_time = self.scrape_site_urls_sequential(
            site_name, pagination, selector, delay
        )

        stored, skipped = self.store_urls(urls, site_name)
        console.print(
            f"[green]✓ {site_name}: Stored {stored} new URLs, {skipped} duplicates[/green]"
        )

        stage1_total = time.time() - stage1_start

        # Stage 2: Scrape details
        if urls:
            stage2_start = time.time()
            results, detail_time = self.scrape_site_details_sequential(site_name, urls, delay)
            success, errors = self.store_jobs(results)
            stage2_total = time.time() - stage2_start

            console.print(f"[green]✓ {site_name}: {success} jobs scraped, {errors} errors[/green]")
        else:
            success = errors = stage2_total = 0

        return {
            "site": site_name,
            "urls_collected": stored,
            "jobs_scraped": success,
            "errors": errors,
            "stage1_time": stage1_total,
            "stage2_time": stage2_total if urls else 0,
        }

    def execute(self):
        self.clear_screen()
        console.print("--- SCRAPE DATA ---", style="bold magenta")

        rules = self.load_scraper_rules()
        if not rules:
            console.print("[red]Error: Could not load scraper rules[/red]")
            self.wait_for_input()
            return

        console.print("\n[bold yellow]STAGE 1 + 2: Scraping all sites in parallel[/bold yellow]")
        console.print(
            f"[cyan]Running {len(rules)} sites simultaneously (each site sequential)[/cyan]\n"
        )

        overall_start = time.time()
        site_results = []

        # Process all sites in parallel
        with ThreadPoolExecutor(max_workers=len(rules)) as executor:
            futures = {executor.submit(self.process_site, rule): rule["name"] for rule in rules}

            for future in as_completed(futures):
                result = future.result()
                site_results.append(result)

        overall_time = time.time() - overall_start

        # Print summary
        console.print("\n[bold cyan]═══ FINAL SUMMARY ═══[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Site", style="cyan")
        table.add_column("URLs", style="green")
        table.add_column("Jobs", style="green")
        table.add_column("Errors", style="red")
        table.add_column("Stage 1", style="yellow")
        table.add_column("Stage 2", style="yellow")

        total_urls = 0
        total_jobs = 0

        for result in site_results:
            table.add_row(
                result["site"],
                str(result["urls_collected"]),
                str(result["jobs_scraped"]),
                str(result["errors"]),
                f"{result['stage1_time']:.1f}s",
                f"{result['stage2_time']:.1f}s",
            )
            total_urls += result["urls_collected"]
            total_jobs += result["jobs_scraped"]

        console.print(table)

        console.print(f"\n[bold green]Total URLs: {total_urls}[/bold green]")
        console.print(f"[bold green]Total Jobs: {total_jobs}[/bold green]")
        console.print(
            f"[bold green]Total Time: {overall_time:.1f}s ({
                overall_time / 60:.1f} min)[/bold green]"
        )
        console.print(f"[cyan]Speed: {(total_jobs / overall_time):.1f} jobs/sec[/cyan]")

        # Update state
        self.state["last_run"] = datetime.now().isoformat()
        self.state["total_urls_collected"] = total_urls
        for result in site_results:
            self.state["sites"][result["site"]] = {
                "urls_collected": result["urls_collected"],
                "jobs_scraped": result["jobs_scraped"],
                "errors": result["errors"],
            }
        self.save_state()

        self.wait_for_input()

    def load_scraper_rules(self):
        """Load scraper rules from config"""
        try:
            with open(self.config.scraper_rules, "r") as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]Error loading scraper rules: {str(e)}[/red]")
            return None
