# Deployment Automation Specification

## Document Purpose
This specification defines the automated deployment pipeline for regenerating JSON API files and deploying the static site to GitHub Pages. The system must handle daily updates without downtime while preserving necessary files.

## System Responsibilities

### Core Functions
1. Trigger JSON generation from fresh databases
2. Build static SPA assets
3. Prepare deployment directory with proper structure
4. Preserve critical files (.git, workflows, CNAME)
5. Deploy to GitHub Pages (gh-pages branch)
6. Handle errors and rollback if needed
7. Monitor deployment success

### Out of Scope
- Database scraping or processing
- JSON generation logic (calls it as a module)
- SPA development (builds existing code)
- GitHub Pages configuration (assumes configured)

## Deployment Architecture

### GitHub Pages Setup
```
Repository: CatalinPlesu/job-market
Branch: gh-pages (or main with /docs folder)
URL: https://catalinplesu.github.io/job-market/

Structure on gh-pages branch:
/
├── index.html              # SPA entry point
├── assets/                 # JS, CSS, images
│   ├── index-abc123.js
│   ├── index-def456.css
│   └── ...
├── api/                    # JSON API files
│   ├── jobs/
│   │   ├── index.json
│   │   ├── page-1.json
│   │   ├── page-2.json
│   │   └── ...
│   └── analysis/
│       ├── index.json
│       ├── salary-overview.json
│       └── ...
├── .nojekyll              # Disable Jekyll processing
├── CNAME                   # Custom domain (if configured)
└── README.md              # Optional: About this site
```

### Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Trigger (Daily 00:30 UTC)                │
│              or Manual via workflow_dispatch                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Checkout Repository (main branch)                 │
│  - Clone with full history                                  │
│  - Access to databases/scrape.db and databases/data.db      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Generate JSON API Files                           │
│  - Run: python -m json_generator                            │
│  - Output: pages/api/ directory                             │
│  - Duration: ~30 seconds for 10,000 jobs                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Build Frontend SPA                                │
│  - cd frontend && npm ci && npm run build                   │
│  - Output: frontend/dist/ directory                         │
│  - Duration: ~1-2 minutes                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Prepare Deployment Directory                      │
│  - Checkout gh-pages branch (or create if doesn't exist)    │
│  - Preserve: .git/, .github/, CNAME, .nojekyll             │
│  - Clear everything else                                    │
│  - Copy frontend/dist/* to root                             │
│  - Copy pages/api/ to api/                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Commit and Push                                   │
│  - git add .                                                │
│  - git commit -m "Deploy: YYYY-MM-DD HH:MM UTC"            │
│  - git push origin gh-pages (force if needed)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Wait for GitHub Pages Deployment                 │
│  - GitHub automatically deploys gh-pages branch             │
│  - Usually completes in 1-2 minutes                         │
│  - Monitor deployment status via API (optional)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 7: Verify Deployment                                 │
│  - Check site is accessible                                 │
│  - Verify API endpoints return valid JSON                   │
│  - Log deployment summary                                   │
└─────────────────────────────────────────────────────────────┘
```

## GitHub Actions Workflow

### Main Workflow File

**`.github/workflows/deploy-pages.yml`**
```yaml
name: Deploy to GitHub Pages

on:
  # Scheduled daily at 00:30 UTC (after scraper Stage 3 completes)
  schedule:
    - cron: '30 0 * * *'
  
  # Manual trigger with optional parameters
  workflow_dispatch:
    inputs:
      force_regenerate:
        description: 'Force regenerate all JSON (ignore cache)'
        required: false
        type: boolean
        default: false

# Permissions needed for GitHub Pages deployment
permissions:
  contents: write
  pages: write
  id-token: write

# Prevent concurrent deployments
concurrency:
  group: pages-deployment
  cancel-in-progress: false

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for gh-pages branch access
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install Python dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install frontend dependencies
        working-directory: frontend
        run: npm ci
      
      - name: Verify databases exist
        run: |
          if [ ! -f databases/scrape.db ]; then
            echo "Error: scrape.db not found"
            exit 1
          fi
          if [ ! -f databases/data.db ]; then
            echo "Error: data.db not found"
            exit 1
          fi
          echo "Databases verified"
      
      - name: Generate JSON API files
        run: |
          echo "Generating JSON API files..."
          python -m json_generator \
            --output pages/api \
            --force=${{ inputs.force_regenerate || 'false' }}
          
          echo "JSON generation complete"
          ls -lh pages/api/
      
      - name: Build frontend SPA
        working-directory: frontend
        run: |
          echo "Building frontend..."
          npm run build
          echo "Build complete"
          ls -lh dist/
      
      - name: Prepare deployment directory
        run: |
          echo "Setting up deployment..."
          
          # Create temp directory for deployment
          mkdir -p deploy_temp
          
          # If gh-pages branch exists, checkout and preserve .git
          if git show-ref --verify --quiet refs/remotes/origin/gh-pages; then
            echo "Checking out gh-pages branch..."
            git worktree add deploy_temp gh-pages
            
            # Preserve important files
            mkdir -p deploy_temp/.preserve
            [ -d deploy_temp/.git ] && cp -r deploy_temp/.git deploy_temp/.preserve/
            [ -f deploy_temp/CNAME ] && cp deploy_temp/CNAME deploy_temp/.preserve/
            [ -f deploy_temp/.nojekyll ] && cp deploy_temp/.nojekyll deploy_temp/.preserve/
            
            # Clear everything else
            cd deploy_temp
            git rm -rf . || true
            cd ..
            
            # Restore preserved files
            [ -d deploy_temp/.preserve/.git ] && cp -r deploy_temp/.preserve/.git deploy_temp/
            [ -f deploy_temp/.preserve/CNAME ] && cp deploy_temp/.preserve/CNAME deploy_temp/
            [ -f deploy_temp/.preserve/.nojekyll ] && cp deploy_temp/.preserve/.nojekyll deploy_temp/
            rm -rf deploy_temp/.preserve
          else
            echo "Creating new gh-pages branch..."
            git worktree add deploy_temp -b gh-pages
            cd deploy_temp
            git rm -rf . || true
            cd ..
          fi
          
          # Copy frontend build
          echo "Copying frontend assets..."
          cp -r frontend/dist/* deploy_temp/
          
          # Copy API files
          echo "Copying API files..."
          mkdir -p deploy_temp/api
          cp -r pages/api/* deploy_temp/api/
          
          # Ensure .nojekyll exists
          touch deploy_temp/.nojekyll
          
          # Create README
          cat > deploy_temp/README.md << 'EOF'
          # Job Market Moldova - Public Site
          
          This branch contains the deployed static site for GitHub Pages.
          Do not edit directly - changes are automatically deployed from main branch.
          
          Last deployed: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
          EOF
          
          echo "Deployment directory prepared"
          du -sh deploy_temp/
      
      - name: Commit and push to gh-pages
        run: |
          cd deploy_temp
          
          # Configure git
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          
          # Add all changes
          git add .
          
          # Check if there are changes
          if git diff --staged --quiet; then
            echo "No changes to deploy"
            exit 0
          fi
          
          # Commit
          COMMIT_MSG="Deploy: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
          git commit -m "$COMMIT_MSG"
          
          # Push (force push to ensure consistency)
          echo "Pushing to gh-pages..."
          git push origin gh-pages --force
          
          echo "Deployment complete!"
      
      - name: Cleanup
        if: always()
        run: |
          git worktree remove deploy_temp || true
          rm -rf deploy_temp
      
      - name: Verify deployment
        run: |
          echo "Waiting for GitHub Pages to deploy..."
          sleep 60
          
          SITE_URL="https://catalinplesu.github.io/job-market"
          
          # Check if site is accessible
          if curl -f -s -o /dev/null "$SITE_URL"; then
            echo "✓ Site is accessible"
          else
            echo "✗ Site is not accessible"
            exit 1
          fi
          
          # Check if API is accessible
          if curl -f -s -o /dev/null "$SITE_URL/api/jobs/index.json"; then
            echo "✓ API is accessible"
          else
            echo "✗ API is not accessible"
            exit 1
          fi
          
          echo "Deployment verified successfully!"
      
      - name: Create deployment summary
        if: always()
        run: |
          cat >> $GITHUB_STEP_SUMMARY << 'EOF'
          ## Deployment Summary
          
          - **Status:** ${{ job.status }}
          - **Timestamp:** $(date -u +'%Y-%m-%d %H:%M:%S UTC')
          - **Site URL:** https://catalinplesu.github.io/job-market
          - **Branch:** gh-pages
          
          ### Deployment Metrics
          - JSON API size: $(du -sh pages/api/ | cut -f1)
          - Frontend size: $(du -sh frontend/dist/ | cut -f1)
          - Total deployment size: $(du -sh deploy_temp/ | cut -f1)
          
          ### Next Steps
          - Visit the site to verify changes
          - Check browser console for errors
          - Monitor analytics for traffic
          EOF
```

### Alternative: Separate Workflows

For more control, split into separate workflows:

**`.github/workflows/generate-json.yml`**
```yaml
name: Generate JSON API

on:
  schedule:
    - cron: '30 0 * * *'
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m json_generator --output pages/api
      - uses: actions/upload-artifact@v4
        with:
          name: api-json
          path: pages/api/
          retention-days: 7
```

**`.github/workflows/build-frontend.yml`**
```yaml
name: Build Frontend

on:
  push:
    paths:
      - 'frontend/**'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - working-directory: frontend
        run: |
          npm ci
          npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: frontend-dist
          path: frontend/dist/
          retention-days: 7
```

**`.github/workflows/deploy-pages.yml`**
```yaml
name: Deploy to Pages

on:
  workflow_run:
    workflows: ["Generate JSON API", "Build Frontend"]
    types:
      - completed
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/download-artifact@v4
        with:
          name: api-json
          path: pages/api/
      
      - uses: actions/download-artifact@v4
        with:
          name: frontend-dist
          path: frontend/dist/
      
      # ... rest of deployment steps
```

## File Preservation Strategy

### Critical Files to Preserve

1. **`.git/`** - Git repository metadata
   - **Why:** Required for git operations
   - **Preservation:** Never delete, copy during branch switch

2. **`CNAME`** - Custom domain configuration
   - **Why:** Custom domain settings (if configured)
   - **Preservation:** Copy before clearing, restore after

3. **`.nojekyll`** - Disable Jekyll processing
   - **Why:** GitHub Pages uses Jekyll by default; we need to disable it
   - **Preservation:** Create if missing, preserve if exists

4. **`.github/workflows/`** (optional)
   - **Why:** Keep deployment workflow in gh-pages for reference
   - **Preservation:** Copy if exists, not critical

### Preservation Script

```bash
#!/bin/bash
# preserve-files.sh

DEPLOY_DIR="$1"
PRESERVE_DIR="$DEPLOY_DIR/.preserve"

# Create preservation directory
mkdir -p "$PRESERVE_DIR"

# Files/directories to preserve
PRESERVE_ITEMS=(
  ".git"
  "CNAME"
  ".nojekyll"
)

echo "Preserving critical files..."
for item in "${PRESERVE_ITEMS[@]}"; do
  if [ -e "$DEPLOY_DIR/$item" ]; then
    cp -r "$DEPLOY_DIR/$item" "$PRESERVE_DIR/"
    echo "  ✓ Preserved $item"
  else
    echo "  - $item does not exist"
  fi
done

echo "Clearing deployment directory..."
cd "$DEPLOY_DIR"
# Remove everything except .git and .preserve
find . -mindepth 1 -maxdepth 1 -not -name '.git' -not -name '.preserve' -exec rm -rf {} +

echo "Restoring preserved files..."
for item in "${PRESERVE_ITEMS[@]}"; do
  if [ -e "$PRESERVE_DIR/$item" ]; then
    cp -r "$PRESERVE_DIR/$item" "$DEPLOY_DIR/"
    echo "  ✓ Restored $item"
  fi
done

# Cleanup
rm -rf "$PRESERVE_DIR"

echo "Preservation complete!"
```

## Error Handling & Rollback

### Error Detection

```yaml
- name: Validate JSON generation
  run: |
    # Check if JSON files were generated
    if [ ! -f pages/api/jobs/index.json ]; then
      echo "Error: Jobs index not generated"
      exit 1
    fi
    
    # Validate JSON syntax
    python -c "
    import json
    import sys
    try:
        with open('pages/api/jobs/index.json') as f:
            json.load(f)
        print('✓ JSON is valid')
    except Exception as e:
        print(f'✗ Invalid JSON: {e}')
        sys.exit(1)
    "
    
    # Check file sizes (should be reasonable)
    MAX_SIZE_MB=50
    SIZE_MB=$(du -sm pages/api | cut -f1)
    if [ $SIZE_MB -gt $MAX_SIZE_MB ]; then
      echo "Warning: API size ($SIZE_MB MB) exceeds threshold ($MAX_SIZE_MB MB)"
    fi
```

### Rollback Strategy

**Option 1: Keep Previous Deployment**
```yaml
- name: Tag current deployment before updating
  run: |
    cd deploy_temp
    git tag "deployment-$(date +%Y%m%d-%H%M%S)"
    git push origin --tags
```

**Option 2: Immediate Rollback on Error**
```yaml
- name: Deploy with rollback on failure
  id: deploy
  run: |
    cd deploy_temp
    git add .
    git commit -m "Deploy: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
    
    # Store current commit
    CURRENT_COMMIT=$(git rev-parse HEAD)
    
    # Push
    git push origin gh-pages --force || {
      echo "Push failed, rolling back..."
      git reset --hard HEAD~1
      exit 1
    }
  
- name: Verify deployment success
  if: steps.deploy.outcome == 'success'
  run: |
    # Verification steps...
  
- name: Rollback on verification failure
  if: failure() && steps.deploy.outcome == 'success'
  run: |
    echo "Deployment verification failed, rolling back..."
    cd deploy_temp
    git reset --hard HEAD~1
    git push origin gh-pages --force
```

## Monitoring & Notifications

### Deployment Notifications

**Slack/Discord Webhook:**
```yaml
- name: Notify deployment status
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Deployment ${{ job.status }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Deployment Status:* ${{ job.status }}\n*Timestamp:* $(date -u)\n*URL:* https://catalinplesu.github.io/job-market"
            }
          }
        ]
      }
```

### Deployment Logs

```yaml
- name: Save deployment logs
  if: always()
  run: |
    mkdir -p logs
    cat > logs/deployment-$(date +%Y%m%d-%H%M%S).log << EOF
    Deployment Status: ${{ job.status }}
    Timestamp: $(date -u +'%Y-%m-%d %H:%M:%S UTC')
    JSON API size: $(du -sh pages/api/ | cut -f1)
    Frontend size: $(du -sh frontend/dist/ | cut -f1)
    Commit: $(cd deploy_temp && git rev-parse HEAD)
    EOF
  
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: deployment-logs
    path: logs/
```

### Health Checks

**Post-Deployment Verification:**
```python
# scripts/verify_deployment.py
import requests
import sys

SITE_URL = "https://catalinplesu.github.io/job-market"

def check_endpoint(path):
    url = f"{SITE_URL}{path}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return True, response.status_code
    except Exception as e:
        return False, str(e)

endpoints = [
    "/",
    "/api/jobs/index.json",
    "/api/analysis/index.json",
]

all_ok = True
for endpoint in endpoints:
    ok, status = check_endpoint(endpoint)
    if ok:
        print(f"✓ {endpoint}: {status}")
    else:
        print(f"✗ {endpoint}: {status}")
        all_ok = False

sys.exit(0 if all_ok else 1)
```

## Performance Optimization

### Caching Strategies

**Cache Dependencies:**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'  # Cache pip dependencies

- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'  # Cache npm dependencies
```

**Incremental JSON Generation (Future Enhancement):**
```python
# json_generator/incremental.py

def detect_changed_jobs(previous_state, current_state):
    """
    Compare previous and current job states.
    Returns: (new_jobs, modified_jobs, deleted_jobs)
    """
    # ... implementation

def incremental_update(output_dir):
    """
    Only regenerate pages that contain changed jobs.
    Update index.json with new metadata.
    """
    # ... implementation
```

### Parallel Processing

```yaml
- name: Generate JSON API files (parallel)
  run: |
    # Split job generation across multiple processes
    python -m json_generator --parallel --workers 4
```

## Testing Strategy

### Local Testing

**Test Deployment Script:**
```bash
#!/bin/bash
# test-deploy.sh

# Simulate deployment locally
echo "Testing deployment process..."

# 1. Generate JSON
python -m json_generator --output test_pages/api

# 2. Build frontend
cd frontend && npm run build && cd ..

# 3. Prepare deployment
mkdir -p test_deploy
cp -r frontend/dist/* test_deploy/
cp -r test_pages/api test_deploy/

# 4. Start local server
cd test_deploy
python -m http.server 8000 &
SERVER_PID=$!

# 5. Verify endpoints
sleep 2
curl -f http://localhost:8000/ || echo "✗ Index failed"
curl -f http://localhost:8000/api/jobs/index.json || echo "✗ API failed"

# 6. Cleanup
kill $SERVER_PID
cd ..
rm -rf test_deploy test_pages

echo "Test complete!"
```

### CI Testing

```yaml
name: Test Deployment

on:
  pull_request:
    paths:
      - 'json_generator/**'
      - 'frontend/**'
      - '.github/workflows/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - # ... setup steps
      - name: Test JSON generation
        run: python -m json_generator --output test_api
      - name: Test frontend build
        run: cd frontend && npm run build
      - name: Verify outputs
        run: |
          test -f test_api/jobs/index.json
          test -f frontend/dist/index.html
```

## Configuration

### Environment Variables

```yaml
env:
  # Deployment configuration
  DEPLOY_BRANCH: gh-pages
  SITE_URL: https://catalinplesu.github.io/job-market
  
  # JSON generator options
  JSON_OUTPUT_DIR: pages/api
  JOBS_PER_PAGE: 100
  
  # Build options
  FRONTEND_DIR: frontend
  FRONTEND_BUILD_CMD: npm run build
```

### Secrets (if needed)

```yaml
# For private deployments or external services
secrets:
  DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Success Criteria

- [ ] Deployment completes in <10 minutes
- [ ] Zero downtime during deployment
- [ ] All files preserved correctly
- [ ] Site accessible immediately after deployment
- [ ] API endpoints return valid JSON
- [ ] Rollback works if deployment fails
- [ ] Deployment logs captured and stored
- [ ] Notifications sent on success/failure
- [ ] Can trigger manually via workflow_dispatch
- [ ] Scheduled deployments run reliably

## Integration Points

### Upstream: JSON Generator
- **Interface:** Python module called via CLI
- **Input:** Database files
- **Output:** JSON files in specified directory
- **Error handling:** Exit code 0 for success, non-zero for failure

### Upstream: Frontend Build
- **Interface:** npm scripts
- **Input:** Source code in frontend/
- **Output:** Built assets in frontend/dist/
- **Error handling:** Build fails exit non-zero

### Downstream: GitHub Pages
- **Interface:** Git push to gh-pages branch
- **Deployment:** Automatic by GitHub
- **Monitoring:** Check site accessibility after deployment

## Timeline

**Week 1: Basic Workflow**
- Set up GitHub Actions workflow file
- Implement basic deployment steps
- Test with sample data

**Week 2: File Preservation & Error Handling**
- Implement file preservation logic
- Add error detection and rollback
- Test various failure scenarios

**Week 3: Optimization & Monitoring**
- Add caching for dependencies
- Implement health checks
- Set up notifications
- Performance testing

## Open Questions for Implementer

1. Use gh-pages branch or main branch with /docs folder?
2. Force push every time or try to preserve commit history?
3. How long to wait before verifying deployment (GitHub Pages lag)?
4. Should we implement blue-green deployment for zero downtime?
5. Archive old deployments or just use git history?

## References

- GitHub Actions docs: https://docs.github.com/en/actions
- GitHub Pages docs: https://docs.github.com/en/pages
- JSON generation spec: `02-json-api-generation.md`
- Frontend spec: `03-spa-frontend-structure.md`
- Architecture: `01-architecture-strategy.md`
