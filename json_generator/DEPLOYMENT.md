# Example: GitHub Actions Workflow Integration

This is an example of how to integrate the JSON generator into a GitHub Actions deployment workflow.

## Example Workflow File

```yaml
name: Generate and Deploy Job Market API

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  generate-api:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -e .
      
      - name: Download databases (from artifact or secure storage)
        run: |
          # Example: Download from GitHub secrets or artifact storage
          # This step would retrieve scrape.db and data.db
          echo "Download databases here"
      
      - name: Generate JSON API
        run: |
          python -m json_generator --output pages/api
        
      - name: Check API size
        run: |
          du -sh pages/api
          echo "API generated successfully"
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./pages
          publish_branch: gh-pages
```

## Local Usage

For development and testing:

```bash
# Generate API files locally
python -m json_generator --output pages/api

# Preview with a local server
cd pages
python -m http.server 8000

# Open http://localhost:8000/api/jobs/index.json in browser
```

## Integration Points

1. **Input**: SQLite databases (`scrape.db`, `data.db`)
   - Must be accessible via paths in `config/settings.py`
   - Can be downloaded from secure storage in CI

2. **Output**: JSON files in `pages/api/` directory
   - `jobs/index.json` - Metadata and filters
   - `jobs/page-N.json` - Paginated job listings

3. **Exit Codes**:
   - `0` - Success
   - `1` - Error (database connection, generation failure, etc.)

4. **Performance**:
   - Completes in <30 seconds for 10,000 jobs
   - Total output size <20MB

## Configuration

Set environment variables or update `config/settings.py`:

```python
# Database paths
Config.scrape_db_path = "databases/scrape.db"
Config.data_db_path = "databases/data.db"
```

Update `json_generator/config.py` for generation settings:

```python
class GeneratorConfig:
    JOBS_PER_PAGE = 100  # Adjust pagination
    OUTPUT_DIR = 'pages/api'  # Output directory
```
