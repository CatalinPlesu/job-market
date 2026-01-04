# Frontend Auto-Deploy Implementation

## Overview

This implementation adds automated deployment of database files to a frontend git repository (e.g., GitHub Pages) after the scheduled scraper completes its daily job check at midnight.

**Important**: The frontend directory will be a separate git repository that uses **Git LFS (Large File Storage)** for database files.

## Prerequisites

### Git LFS Installation

Database files can be large, so Git LFS is required to handle them efficiently:

**Ubuntu/Debian:**
```bash
sudo apt-get install git-lfs
```

**macOS:**
```bash
brew install git-lfs
```

**Windows:**
Download from https://git-lfs.github.com/

The system will automatically configure Git LFS when initializing the frontend repository.

## Key Features

### 1. Manual Deployment (Menu Option #9)
- **Menu Item**: "Push Frontend to Git (Copy DBs + Commit + Push)"
- **What it does**:
  1. Copies `scrape.db` and `data.db` to `frontend/api/`
  2. Initializes/updates git repository in `frontend/`
  3. Configures Git LFS for `.db` files (via `.gitattributes`)
  4. Commits changes with timestamp
  5. Pushes to configured remote repository

### 2. Automated Deployment (After Stage 3)
- **When**: Daily at 00:00 (midnight) after Stage 3 completes
- **What happens**:
  1. Stage 3 rechecks all alive jobs
  2. Automatically copies databases to `frontend/api/`
  3. Sets up Git LFS (if not already configured)
  4. Commits and pushes to git repository
  5. All without manual intervention

## Configuration

### Required Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Then configure:

```bash
# REQUIRED: Your frontend git repository URL
# SSH format (recommended): git@github.com:username/frontend-repo.git
# HTTPS format: https://github.com/username/frontend-repo.git
FRONTEND_GIT_REMOTE_URL=git@github.com:username/frontend-repo.git

# OPTIONAL: Branch to push to (default: main)
FRONTEND_GIT_BRANCH=main

# OPTIONAL: Deployment strategy (default: true)
FRONTEND_GIT_FRESH_APPROACH=true
```

### Deployment Strategies

#### 1. Fresh Approach (Default - Recommended)
- **Setting**: `FRONTEND_GIT_FRESH_APPROACH=true`
- **How it works**:
  - Removes `.git` directory
  - Reinitializes fresh repository
  - Force pushes changes
- **Benefits**:
  - Keeps repository size small
  - No git history accumulation
  - Faster over time
- **Drawbacks**:
  - Loses git history
  - Requires force push permissions

#### 2. Incremental Approach
- **Setting**: `FRONTEND_GIT_FRESH_APPROACH=false`
- **How it works**:
  - Adds changes to existing repository
  - Creates incremental commits
  - Regular push (no force)
- **Benefits**:
  - Preserves git history
  - Standard git workflow
- **Drawbacks**:
  - Repository size grows over time
  - May need cleanup eventually

## Setup for GitHub Pages

### 1. Create a Frontend Repository

```bash
# On GitHub, create a new repository
# Example: https://github.com/username/job-market-frontend
```

### 2. Configure GitHub Pages

1. Go to repository Settings
2. Navigate to Pages section
3. Set source to "Deploy from a branch"
4. Select branch: `main` (or your configured branch)
5. Select folder: `/ (root)`
6. Save

### 3. Configure the Application

```bash
# In your .env file
# SSH format (recommended - no password needed with SSH keys)
FRONTEND_GIT_REMOTE_URL=git@github.com:username/job-market-frontend.git

# Or HTTPS format (requires personal access token)
# FRONTEND_GIT_REMOTE_URL=https://github.com/username/job-market-frontend.git

FRONTEND_GIT_BRANCH=main
FRONTEND_GIT_FRESH_APPROACH=true
```

### 4. First Deployment

**Option A: Manual deployment**
```bash
python main.py
# Select option 9: "Push Frontend to Git"
```

**Option B: Wait for scheduled deployment**
- The system will automatically deploy after Stage 3 runs (daily at midnight)

### 5. Access Your Site

After deployment, your site will be available at:
```
https://username.github.io/job-market-frontend/
```

**Path Configuration**: The frontend automatically detects the correct API path based on the deployment environment:
- On GitHub Pages: `https://username.github.io/Job-Market-Frontend/api/data.db`
- On localhost: `http://localhost:8000/api/data.db`

No configuration needed - the detection is handled automatically in `js/config.js`!

## File Structure

```
job-market/
├── frontend/                    # Frontend directory (separate git repo)
│   ├── .git/                   # Git repository (managed automatically)
│   ├── .gitattributes          # Git LFS configuration (auto-created)
│   ├── api/                    # Database files (auto-copied, tracked with LFS)
│   │   ├── scrape.db          # Raw scraped data (stored in Git LFS)
│   │   └── data.db            # Processed data (stored in Git LFS)
│   ├── index.html             # Frontend entry point
│   ├── js/                    # JavaScript modules
│   └── ...
├── src/
│   ├── frontend_operations.py     # Database copy + git orchestration
│   ├── frontend_git_operations.py # Git operations module with LFS support
│   └── scheduled_scraper.py       # Modified to auto-deploy after Stage 3
└── .env                       # Your configuration
```

## Troubleshooting

### Issue: "Git LFS is not installed"

**Solution**: Install Git LFS on your system

**Ubuntu/Debian:**
```bash
sudo apt-get install git-lfs
```

**macOS:**
```bash
brew install git-lfs
```

After installation, the system will automatically configure LFS for database files.

### Issue: "No remote URL configured"

**Solution**: Set `FRONTEND_GIT_REMOTE_URL` in your `.env` file

**SSH format (recommended):**
```bash
FRONTEND_GIT_REMOTE_URL=git@github.com:username/repo.git
```

**HTTPS format:**
```bash
FRONTEND_GIT_REMOTE_URL=https://github.com/username/repo.git
```

### Issue: Authentication failed when pushing

**Solution Options:**

**Option 1: Use SSH (recommended)**
1. Set up SSH keys on your GitHub account
2. Use SSH URL format:
   ```bash
   FRONTEND_GIT_REMOTE_URL=git@github.com:username/repo.git
   ```

**Option 2: Use Personal Access Token (PAT) with HTTPS**
1. Generate a PAT on GitHub (Settings → Developer settings → Personal access tokens)
2. Use it in the URL:
   ```bash
   FRONTEND_GIT_REMOTE_URL=https://USERNAME:TOKEN@github.com/username/repo.git
   ```

### Issue: Force push rejected

**Solution**: Enable force push for the branch or use incremental approach

```bash
FRONTEND_GIT_FRESH_APPROACH=false
```

## Testing

A test script is provided to verify the setup:

```bash
python test_frontend_git.py
```

This tests:
- Database copying to frontend/api
- Git initialization and operations
- Commit creation

## Architecture

### Modules

1. **`src/frontend_git_operations.py`**
   - Low-level git operations
   - Handles init, add, commit, push
   - Supports both fresh and incremental approaches

2. **`src/frontend_operations.py`**
   - High-level orchestration
   - Copies databases
   - Calls git operations
   - Used by both menu and scheduler

3. **`src/scheduled_scraper.py`**
   - Modified `run_stage_3_only()` function
   - Calls `copy_databases_and_push()` after Stage 3

### Data Flow

```
Stage 3 Completion
       ↓
copy_databases_and_push()
       ↓
    ┌──────────────────────────┐
    │                          │
    ↓                          ↓
Copy Databases          Git Operations
    ↓                          ↓
frontend/api/*.db       frontend/.git
    ↓                          ↓
    └──────────→ Push ────────→ Remote Repo
                                    ↓
                              GitHub Pages
```

## Logs and Monitoring

- **Error logs**: `logs/scraper_YYYY-MM-DD.log`
- **Git operations**: Logged to error log only on failures
- **Console output**: Shows progress during execution

## Best Practices

1. **Test first**: Use the manual menu option to test deployment before relying on automation
2. **Monitor logs**: Check error logs after first automated deployment
3. **Backup**: Keep database backups (automatic with scheduled scraper)
4. **Repository size**: Use fresh approach to keep repo small
5. **Security**: Never commit your `.env` file (already in `.gitignore`)

## Related Documentation

- [Frontend README](frontend/README.md) - Frontend application details
- [Main README](README.md) - Complete project documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide

## Support

If you encounter issues:
1. Check error logs in `logs/`
2. Verify `.env` configuration
3. Test with manual deployment first
4. Review git remote permissions
