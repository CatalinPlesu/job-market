# API Directory

This directory contains the SQLite database files for the Job Market frontend.

## Database Files

- `data.db` - Processed job data with normalized structure
- `scrape.db` - Raw scraped job data

## How to populate

These files are automatically copied here when you:
1. Run menu option 8: "Copy Database Files to Frontend API"
2. Run menu option 9: "Push Frontend to Git (Copy DBs + Commit + Push)"
3. Run the scheduled scraper (Stage 3 at 00:00 daily)

## Git LFS

Database files are tracked with Git LFS (Large File Storage) to handle their large size efficiently. Make sure Git LFS is installed before pushing:

```bash
# Ubuntu/Debian
sudo apt-get install git-lfs

# macOS
brew install git-lfs
```

## Note

This directory exists in the frontend repository (separate from the main repository). When you deploy the frontend to GitHub Pages or another hosting service, these database files will be included and accessible at `/api/data.db` and `/api/scrape.db`.
