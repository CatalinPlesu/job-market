# src/debug_menu.py
import json
import os
import re
from pathlib import Path
from .base_menu import BaseMenu
from rich.console import Console

console = Console()

# --- JavaScript Template ---
JS_TEMPLATE = """
// --- Debug Script for {site_name} ---
console.log("Highlighting job links and pagination on {site_name}");

// Selector for job links based on config
const jobLinkSelector = '{job_url_selector}';
// Selector for pagination links (general pattern based on config)
// This might need fine-tuning per site after inspection if the pattern is complex
const paginationSelector = 'a[href*="{pagination_pattern}"]';

// --- Determine First Page URL ---
const currentUrl = window.location.href;
let firstPageUrl = null;

// Attempt to construct the first page URL based on the detected pattern
// This is a heuristic and might not work perfectly for every URL structure
if (currentUrl.includes('{pagination_pattern}')) {{
    // If the pattern is found in the current URL, try replacing the page number part
    // Example: If pattern is 'page=' and URL is '.../page=3', replace 'page=3' part
    // Example: If pattern is 'jobs-moldova/' and URL is '.../jobs-moldova/2', replace the number part
    const regexPattern = new RegExp(/{pagination_regex}/, 'i'); // Use the escaped regex from Python
    firstPageUrl = currentUrl.replace(regexPattern, '{first_page_replacement}');
}} else {{
    // If the pattern is not in the current URL, assume the base URL (without page info) is the first page
    // This is often true for sites like delucru.md where ?page=1 is the same as no page param
    // Or construct based on the template provided in the config
    firstPageUrl = '{first_page_url_template}';
    // Replace the placeholder again, just in case the template itself was used
    firstPageUrl = firstPageUrl.replace('{{{{page}}}}', '1'); // Double braces to escape in Python format string
}}

console.log("Potential First Page URL (copy and paste into address bar):", firstPageUrl);

// Function to highlight an element
function highlightElement(element) {{
  if (element && !element.style.outline) {{ // Only highlight if not already highlighted
    element.style.outline = '3px solid red';
    element.style.outlineOffset = '2px';
    element.style.backgroundColor = 'rgba(255, 0, 0, 0.2)'; // Optional: semi-transparent background
    // Store original styles to potentially revert later
    element.dataset.originalOutline = element.style.outline;
    element.dataset.originalOutlineOffset = element.style.outlineOffset;
    element.dataset.originalBg = element.style.backgroundColor;
  }}
}}

// Function to remove highlight
function removeHighlight(element) {{
  if (element && element.dataset.originalOutline) {{
    element.style.outline = element.dataset.originalOutline || '';
    element.style.outlineOffset = element.dataset.originalOutlineOffset || '';
    element.style.backgroundColor = element.dataset.originalBg || '';
    delete element.dataset.originalOutline;
    delete element.dataset.originalOutlineOffset;
    delete element.dataset.originalBg;
  }}
}}

// Find and highlight job links
const jobLinks = document.querySelectorAll(jobLinkSelector);
console.log(`Found ${{jobLinks.length}} job links matching selector "${{jobLinkSelector}}".`);
jobLinks.forEach(link => highlightElement(link));

// Find and highlight pagination links
const paginationLinks = document.querySelectorAll(paginationSelector);
console.log(`Found ${{paginationLinks.length}} potential pagination links matching selector "${{paginationSelector}}".`);
paginationLinks.forEach(link => highlightElement(link));

// Optional: Add a helper function to remove highlights
window.remove{site_name_uppercase}Highlights = function() {{
    jobLinks.forEach(removeHighlight);
    paginationLinks.forEach(removeHighlight);
    console.log("Highlights removed for {site_name}.");
}};

console.log("Highlighting complete. Check the console for counts and the potential first page URL. Run remove{site_name_uppercase}Highlights() to remove highlights.");
"""


def sanitize_filename(name):
    """Sanitizes the site name to be a valid filename."""
    return name.replace('.', '_').replace('/', '_').replace('\\', '_').replace(' ', '_')


def generate_js_files(config_path, output_dir):
    """Reads config and generates JS files."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            sites_config = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: Configuration file '{
                      config_path}' not found.[/red]")
        return False
    except json.JSONDecodeError:
        console.print(f"[red]Error: Configuration file '{
                      config_path}' is not valid JSON.[/red]")
        return False

    Path(output_dir).mkdir(exist_ok=True)

    success_count = 0
    for site_config in sites_config:
        site_name = site_config.get("name")
        job_url_selector = site_config.get("job-url-class-selector")
        pagination_url_template = site_config.get("pagination")

        if not all([site_name, job_url_selector, pagination_url_template]):
            console.print(
                f"[yellow]Warning: Skipping entry due to missing 'name', 'job-url-class-selector', or 'pagination' keys: {site_config}[/yellow]")
            continue

        # --- Derive pattern and first page URL ---
        # Split the template by {page}
        parts = pagination_url_template.split("{page}")
        if len(parts) != 2:
            console.print(f"[yellow]Warning: Pagination template for '{
                          site_name}' does not contain '{{page}}'. Using fallback logic for pattern and URL.[/yellow]")
            # Fallback for pattern (less reliable)
            if '?' in pagination_url_template:
                fallback_pattern = pagination_url_template.split(
                    '?')[-1].split('=')[0] + '='
            else:
                match = re.search(r'(?:page|p|pg)(?:-|_|=)',
                                  pagination_url_template.lower())
                if match:
                    fallback_pattern = match.group()
                else:
                    fallback_pattern = "page="  # Default guess
            pagination_pattern = fallback_pattern
            # Fallback for first page URL: just replace {page} with 1
            first_page_url_template = pagination_url_template.replace(
                "{page}", "1")
            # Fallback for regex: escape the fallback pattern
            escaped_fallback_pattern = re.escape(fallback_pattern)
            # A simple replacement regex might be /page=\d+/ or /\/page-\d+\//
            # Use the fallback pattern as the base for the regex, assuming digits follow
            # e.g., if fallback_pattern is 'page=', the regex could be /page=\d+/
            # e.g., if fallback_pattern is 'jobs-moldova/', the regex could be /jobs-moldova\/\d+/ or similar
            # Let's try a more generic approach based on the fallback
            # Look for the pattern followed by digits: /fallback_pattern\d+/
            # Or, if it looks like a query param: /fallback_pattern\d+(?=[&\s])/ or /fallback_pattern\d+(?=[&\s\/])/
            # Query param style: e.g., page=2
            if '=' in fallback_pattern:
                fallback_regex_pattern = re.escape(fallback_pattern) + r'\d+'
            else:  # Path style: e.g., page-2
                # Ensure it's not just the base path without digits, add \d+
                # Handle potential trailing slashes or other chars
                fallback_regex_pattern = re.escape(
                    fallback_pattern) + r'\d+(?=[^\w]|$)'
            pagination_regex = fallback_regex_pattern
            first_page_replacement = fallback_pattern + "1"
        else:
            before_page, after_page = parts
            # Determine pattern and construct regex/first page replacement based on structure
            if '?' in before_page:
                # Query parameter: e.g., ?page=2
                query_part = before_page.split('?')[-1]
                param_name = query_part.split('=')[0]
                pagination_pattern = param_name + '='
                # Regex to match the parameter and its value: e.g., /page=\d+/
                pagination_regex = re.escape(param_name) + r'=\d+'
                # Replacement string for first page: e.g., page=1
                first_page_replacement = param_name + '=1'
            else:
                # Path segment: e.g., /page-2/ or /section/2
                # Take the last part of the path before {page}, assuming it indicates the page number part
                path_parts = before_page.strip('/').split('/')
                potential_base = path_parts[-1] if path_parts[-1] else (
                    path_parts[-2] if len(path_parts) > 1 else "page")
                # Heuristic: if it looks like it contains 'page' or similar, use it
                if re.search(r'(?:page|p|pg)(?:-|_)', potential_base, re.IGNORECASE):
                    # Pattern is likely the base part indicating the number follows
                    # e.g., 'page-' from 'https://site.com/jobs/page-{page}/'
                    pagination_pattern = potential_base
                    # Regex: match the base followed by digits: e.g., /page-\d+/
                    pagination_regex = re.escape(potential_base) + r'\d+'
                    # Replacement: base + '1': e.g., page-1
                    first_page_replacement = potential_base + "1"
                else:
                    # If the heuristic for path segment fails, fall back
                    # This is tricky, let's assume the part before {page} contains the info
                    # A common structure might be like 'jobs/2' -> 'jobs/1'
                    # We need to find the number part more robustly.
                    # Let's try a regex that finds the last occurrence of a number preceded by a common delimiter
                    # before the {page} placeholder.
                    # Example: "https://example.com/path/to/page-<num>/"
                    # We look for the part before {page}, e.g., "https://example.com/path/to/page-"
                    # and assume the number follows the last non-number character.
                    # This is complex. Let's simplify the heuristic again.
                    # If before_page is "https://jobber.md/jobs/page-", the pattern is "page-"
                    # and the regex should find "page-" followed by digits.
                    # If before_page is "https://delucru.md/jobs?", the pattern is "?page=" (handled above)
                    # If before_page is "https://rabota.md/ro/jobs-moldova/", the pattern is "/"
                    # and the number follows the last "/". The template is ".../{page}"
                    # So, the part *before* {page} is "https://rabota.md/ro/jobs-moldova/"
                    # The *last* segment before {page} is "jobs-moldova/"
                    # We want to match "jobs-moldova/" followed by the page number.
                    # This is getting complex. Let's use a more general approach for path segments.
                    # If the part before {page} ends with a specific string followed by a number,
                    # e.g., ".../page-<num>", ".../p<num>", ".../pg<num>"
                    # We can try to find the last occurrence of such a pattern fragment.
                    # For now, let's assume the last path segment (before '/') is the base pattern if it looks like a page indicator.
                    # Otherwise, fall back to a simpler guess.
                    if potential_base and re.search(r'(?:page|p|pg)', potential_base, re.IGNORECASE):
                        pagination_pattern = potential_base
                        pagination_regex = re.escape(potential_base) + r'\d+'
                        first_page_replacement = potential_base + "1"
                    else:
                        # Fallback for path if heuristic fails
                        pagination_pattern = "/"  # Default guess for path-based, often the number follows /
                        # A more robust regex for a number at the end or followed by non-word: /\/\d+(?=[\/\s?#]|$)/
                        # But this is very generic. Let's stick to the potential base if found, else guess.
                        # Use the full 'before_page' segment as a base for regex if it ends clearly.
                        # A simpler fallback: if the template is ".../something/{page}", the pattern is "something/"
                        # and the regex matches "something/" + number.
                        # Find the segment before the last slash in before_page (excluding trailing slash)
                        segments = [s for s in before_page.strip(
                            '/').split('/') if s]
                        if segments:
                            last_segment = segments[-1]
                            if re.search(r'(?:page|p|pg)', last_segment, re.IGNORECASE):
                                pagination_pattern = last_segment + "/"
                                pagination_regex = re.escape(
                                    last_segment + "/") + r'\d+'
                                first_page_replacement = last_segment + "/1"
                            else:
                                # Ultimate fallback if path segment heuristic fails
                                pagination_pattern = "page"  # Generic guess
                                # Generic for query or path
                                pagination_regex = r'page=\d+|\/\d+(?=[\/\s?#]|$)'
                                first_page_replacement = "page=1"  # Or try to replace the number part
                        else:
                            # If no segments, very generic
                            pagination_pattern = "page"
                            pagination_regex = r'page=\d+|\/\d+(?=[\/\s?#]|$)'
                            first_page_replacement = "page=1"

            # Construct the first page URL template for logging
            first_page_url_template = pagination_url_template.replace(
                "{page}", "1")

        # Sanitize the site name for the filename and function names
        sanitized_site_name = sanitize_filename(site_name)
        site_name_uppercase = sanitized_site_name.upper()

        # Format the JavaScript template with the specific site details
        js_content = JS_TEMPLATE.format(
            site_name=site_name,
            job_url_selector=job_url_selector,
            pagination_pattern=pagination_pattern,
            pagination_regex=pagination_regex,
            first_page_replacement=first_page_replacement,
            first_page_url_template=first_page_url_template,
            site_name_uppercase=site_name_uppercase
        )

        # Define the output filename
        filename = f"{sanitized_site_name}.js"
        filepath = os.path.join(output_dir, filename)

        # Write the JavaScript content to the file
        try:
            with open(filepath, 'w', encoding='utf-8') as js_file:
                # Remove leading newline from template
                js_file.write(js_content.strip())
            console.print(f"  - Generated: {filepath}", style="cyan")
            success_count += 1
        except IOError as e:
            console.print(f"  - [red]Error writing file {filepath}: {e}[/red]")
            # Consider returning False if any single file fails, depending on requirements
            # For now, we'll continue trying to generate others.
            # return False

    if success_count > 0:
        console.print(f"[bold green]Successfully generated {
                      success_count} debug JavaScript files in '{output_dir}/'.[/bold green]")
        console.print(
            "[bold yellow]Important:[/bold yellow] The generated scripts will log the potential first page URL to the console. You must navigate to it manually.")
        return True
    else:
        console.print(
            "[red]No JavaScript files were generated due to configuration errors.[/red]")
        return False


class DebugMenu(BaseMenu):
    def execute(self):
        self.clear_screen()
        console.print("--- GENERATE DEBUG JAVASCRIPT ---",
                      style="bold magenta")

        # --- Call the generation logic ---
        config_path = "config/scraper_rules.json"  # Adjust path if needed
        output_dir = "js"
        success = generate_js_files(config_path, output_dir)

        if not success:
            console.print(
                "[red]Failed to generate debug scripts.[/red]", style="bold red")
        # --- End of generation logic call ---

        self.wait_for_input()
