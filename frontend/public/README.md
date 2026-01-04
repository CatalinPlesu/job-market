# Public Directory

This directory contains the SQLite database files for the Job Market frontend.

## Database Files

- `data.db` - Processed job data with normalized structure (100MB+)
- `scrape.db` - Raw scraped job data

## How to populate

These files are automatically copied here when you:
1. Run menu option 8: "Copy Database Files to Frontend"
2. Run menu option 9: "Push Frontend to Git (Copy DBs + Commit + Push)"
3. Run the scheduled scraper (Stage 3 at 00:00 daily)

## Git LFS (Required)

Database files are tracked with Git LFS (Large File Storage) because they exceed GitHub's 100MB file size limit. 

**Git LFS must be installed before pushing:**

```bash
# Ubuntu/Debian
sudo apt-get install git-lfs

# macOS
brew install git-lfs
```

## How Files Are Accessed

Because GitHub Pages cannot serve LFS files directly, the frontend uses GitHub's raw download URL:

- **On GitHub Pages**: `https://github.com/{user}/{repo}/raw/refs/heads/{branch}/public/data.db?download=`
- **On Localhost**: `http://localhost:8000/public/data.db`

The `public` folder name helps avoid CORS restrictions when fetching from GitHub's download URL.

## Note

This directory exists in the frontend repository (separate from the main repository). Files are served via GitHub's raw download API to bypass the GitHub Pages 100MB limit and LFS pointer issue.
