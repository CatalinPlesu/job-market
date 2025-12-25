"""
Reporting module for scraping statistics.
Generates compact daily reports per stage.
"""
import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class Stage1Stats:
    """Statistics for Stage 1 - Scraping job listings."""
    site: str
    links_found: int
    pages_scraped: int
    errors: int = 0


@dataclass
class Stage2Stats:
    """Statistics for Stage 2 - Getting job details."""
    site: str
    total_jobs: int
    success: int  # Got description
    empty: int    # Page loaded but no content found
    failed: int   # HTTP errors or exceptions
    http_200: int = 0
    http_404: int = 0
    http_other: int = 0


@dataclass
class Stage3Stats:
    """Statistics for Stage 3 - Rechecking jobs."""
    site: str
    total_checked: int
    alive: int    # HTTP 200
    dead: int     # Any error or non-200


class DailyReport:
    """
    Generates and manages daily scraping reports.
    Creates one compact file per day with all stage statistics.
    """
    
    def __init__(self, reports_dir: str = "reports"):
        """
        Initialize daily report.
        
        Args:
            reports_dir: Directory to store reports (default: "reports")
        """
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.report_date = date.today()
        self.report_file = self.reports_dir / f"report_{self.report_date.isoformat()}.json"
        
        # Initialize report structure
        self.report_data = {
            'date': self.report_date.isoformat(),
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'stage1': {
                'sites': [],
                'aggregated': {
                    'total_links': 0,
                    'total_pages': 0,
                    'total_errors': 0
                }
            },
            'stage2': {
                'sites': [],
                'aggregated': {
                    'total_jobs': 0,
                    'total_success': 0,
                    'total_empty': 0,
                    'total_failed': 0,
                    'total_http_200': 0,
                    'total_http_404': 0,
                    'total_http_other': 0
                }
            },
            'stage3': {
                'sites': [],
                'aggregated': {
                    'total_checked': 0,
                    'total_alive': 0,
                    'total_dead': 0
                }
            }
        }
    
    def add_stage1_stats(self, stats: Stage1Stats):
        """Add Stage 1 statistics for a site."""
        self.report_data['stage1']['sites'].append(asdict(stats))
        
        # Update aggregated
        agg = self.report_data['stage1']['aggregated']
        agg['total_links'] += stats.links_found
        agg['total_pages'] += stats.pages_scraped
        agg['total_errors'] += stats.errors
    
    def add_stage2_stats(self, stats: Stage2Stats):
        """Add Stage 2 statistics for a site."""
        self.report_data['stage2']['sites'].append(asdict(stats))
        
        # Update aggregated
        agg = self.report_data['stage2']['aggregated']
        agg['total_jobs'] += stats.total_jobs
        agg['total_success'] += stats.success
        agg['total_empty'] += stats.empty
        agg['total_failed'] += stats.failed
        agg['total_http_200'] += stats.http_200
        agg['total_http_404'] += stats.http_404
        agg['total_http_other'] += stats.http_other
    
    def add_stage3_stats(self, stats: Stage3Stats):
        """Add Stage 3 statistics for a site."""
        self.report_data['stage3']['sites'].append(asdict(stats))
        
        # Update aggregated
        agg = self.report_data['stage3']['aggregated']
        agg['total_checked'] += stats.total_checked
        agg['total_alive'] += stats.alive
        agg['total_dead'] += stats.dead
    
    def save(self):
        """Save report to file."""
        self.report_data['completed_at'] = datetime.now().isoformat()
        
        with open(self.report_file, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        # Also create a human-readable text version
        self._save_text_report()
    
    def _save_text_report(self):
        """Save a human-readable text version of the report."""
        text_file = self.report_file.with_suffix('.txt')
        
        with open(text_file, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write(f"DAILY SCRAPING REPORT - {self.report_date.isoformat()}\n")
            f.write(f"{'='*80}\n\n")
            
            # Stage 1
            f.write(f"STAGE 1: Job Listings Scraping\n")
            f.write(f"{'-'*80}\n")
            for site_stats in self.report_data['stage1']['sites']:
                f.write(f"  {site_stats['site']:20} | "
                       f"Links: {site_stats['links_found']:5} | "
                       f"Pages: {site_stats['pages_scraped']:4} | "
                       f"Errors: {site_stats['errors']:3}\n")
            
            agg = self.report_data['stage1']['aggregated']
            f.write(f"\n  {'TOTAL':20} | "
                   f"Links: {agg['total_links']:5} | "
                   f"Pages: {agg['total_pages']:4} | "
                   f"Errors: {agg['total_errors']:3}\n")
            f.write(f"\n")
            
            # Stage 2
            f.write(f"STAGE 2: Job Details Scraping\n")
            f.write(f"{'-'*80}\n")
            for site_stats in self.report_data['stage2']['sites']:
                f.write(f"  {site_stats['site']:20} | "
                       f"Total: {site_stats['total_jobs']:4} | "
                       f"OK: {site_stats['success']:4} | "
                       f"Empty: {site_stats['empty']:4} | "
                       f"Failed: {site_stats['failed']:4}\n")
                f.write(f"  {' '*20} | "
                       f"HTTP 200: {site_stats['http_200']:4} | "
                       f"404: {site_stats['http_404']:4} | "
                       f"Other: {site_stats['http_other']:4}\n")
            
            agg = self.report_data['stage2']['aggregated']
            f.write(f"\n  {'TOTAL':20} | "
                   f"Total: {agg['total_jobs']:4} | "
                   f"OK: {agg['total_success']:4} | "
                   f"Empty: {agg['total_empty']:4} | "
                   f"Failed: {agg['total_failed']:4}\n")
            f.write(f"  {' '*20} | "
                   f"HTTP 200: {agg['total_http_200']:4} | "
                   f"404: {agg['total_http_404']:4} | "
                   f"Other: {agg['total_http_other']:4}\n")
            f.write(f"\n")
            
            # Stage 3
            f.write(f"STAGE 3: Job Status Recheck\n")
            f.write(f"{'-'*80}\n")
            for site_stats in self.report_data['stage3']['sites']:
                f.write(f"  {site_stats['site']:20} | "
                       f"Checked: {site_stats['total_checked']:5} | "
                       f"Alive: {site_stats['alive']:5} | "
                       f"Dead: {site_stats['dead']:5}\n")
            
            agg = self.report_data['stage3']['aggregated']
            f.write(f"\n  {'TOTAL':20} | "
                   f"Checked: {agg['total_checked']:5} | "
                   f"Alive: {agg['total_alive']:5} | "
                   f"Dead: {agg['total_dead']:5}\n")
            
            f.write(f"\n{'='*80}\n")
            f.write(f"Report generated at: {self.report_data['completed_at']}\n")
            f.write(f"{'='*80}\n")
    
    @staticmethod
    def list_reports(reports_dir: str = "reports") -> List[Path]:
        """
        List all report files.
        
        Args:
            reports_dir: Directory containing reports
            
        Returns:
            List of report file paths, sorted by date (newest first)
        """
        reports_path = Path(reports_dir)
        if not reports_path.exists():
            return []
        
        json_reports = sorted(reports_path.glob("report_*.json"), reverse=True)
        return json_reports
    
    @staticmethod
    def load_report(report_file: Path) -> Dict:
        """
        Load a report from file.
        
        Args:
            report_file: Path to report file
            
        Returns:
            Dict containing report data
        """
        with open(report_file, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def display_report(report_file: Path):
        """
        Display a report in a human-readable format.
        
        Args:
            report_file: Path to report file
        """
        # Check if text version exists and display it
        text_file = report_file.with_suffix('.txt')
        if text_file.exists():
            with open(text_file, 'r') as f:
                print(f.read())
        else:
            # Fall back to JSON
            report_data = DailyReport.load_report(report_file)
            print(json.dumps(report_data, indent=2))
    
    @staticmethod
    def display_report_rich(report_file: Path, rich_logger):
        """
        Display a report with rich formatting.
        
        Args:
            report_file: Path to report file
            rich_logger: RichLogger instance for formatted output
        """
        from rich.table import Table
        
        report_data = DailyReport.load_report(report_file)
        
        rich_logger.print_header(
            f"DAILY SCRAPING REPORT - {report_data['date']}",
            f"Generated at {report_data['completed_at']}"
        )
        
        # Stage 1 Table
        rich_logger.print_section("Stage 1: Job Listings Scraping")
        table1 = Table(show_header=True, header_style="bold cyan")
        table1.add_column("Site", style="yellow", no_wrap=True)
        table1.add_column("Links Found", justify="right", style="green")
        table1.add_column("Pages Scraped", justify="right", style="blue")
        table1.add_column("Errors", justify="right", style="red")
        
        for site_stats in report_data['stage1']['sites']:
            table1.add_row(
                site_stats['site'],
                str(site_stats['links_found']),
                str(site_stats['pages_scraped']),
                str(site_stats['errors'])
            )
        
        agg = report_data['stage1']['aggregated']
        table1.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{agg['total_links']}[/bold]",
            f"[bold]{agg['total_pages']}[/bold]",
            f"[bold]{agg['total_errors']}[/bold]",
            style="bold"
        )
        
        rich_logger.console.print(table1)
        rich_logger.console.print()
        
        # Stage 2 Table
        rich_logger.print_section("Stage 2: Job Details Scraping")
        table2 = Table(show_header=True, header_style="bold cyan")
        table2.add_column("Site", style="yellow", no_wrap=True)
        table2.add_column("Total", justify="right", style="cyan")
        table2.add_column("Success", justify="right", style="green")
        table2.add_column("Empty", justify="right", style="yellow")
        table2.add_column("Failed", justify="right", style="red")
        table2.add_column("HTTP 200", justify="right", style="blue")
        table2.add_column("HTTP 404", justify="right", style="magenta")
        
        for site_stats in report_data['stage2']['sites']:
            table2.add_row(
                site_stats['site'],
                str(site_stats['total_jobs']),
                str(site_stats['success']),
                str(site_stats['empty']),
                str(site_stats['failed']),
                str(site_stats['http_200']),
                str(site_stats['http_404'])
            )
        
        agg = report_data['stage2']['aggregated']
        table2.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{agg['total_jobs']}[/bold]",
            f"[bold]{agg['total_success']}[/bold]",
            f"[bold]{agg['total_empty']}[/bold]",
            f"[bold]{agg['total_failed']}[/bold]",
            f"[bold]{agg['total_http_200']}[/bold]",
            f"[bold]{agg['total_http_404']}[/bold]",
            style="bold"
        )
        
        rich_logger.console.print(table2)
        rich_logger.console.print()
        
        # Stage 3 Table
        rich_logger.print_section("Stage 3: Job Status Recheck")
        table3 = Table(show_header=True, header_style="bold cyan")
        table3.add_column("Site", style="yellow", no_wrap=True)
        table3.add_column("Total Checked", justify="right", style="cyan")
        table3.add_column("Alive", justify="right", style="green")
        table3.add_column("Dead", justify="right", style="red")
        
        for site_stats in report_data['stage3']['sites']:
            table3.add_row(
                site_stats['site'],
                str(site_stats['total_checked']),
                str(site_stats['alive']),
                str(site_stats['dead'])
            )
        
        agg = report_data['stage3']['aggregated']
        table3.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{agg['total_checked']}[/bold]",
            f"[bold]{agg['total_alive']}[/bold]",
            f"[bold]{agg['total_dead']}[/bold]",
            style="bold"
        )
        
        rich_logger.console.print(table3)
        rich_logger.console.print()
