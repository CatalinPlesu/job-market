# Issue 4: Deployment Pipeline Automation

## Title
Implement GitHub Actions Workflow for Automated Deployment

## Labels
`enhancement`, `devops`, `github-actions`

## Description

### Objective
Create an automated deployment pipeline that generates fresh JSON files, builds the SPA, and deploys to GitHub Pages daily.

### Scope
- GitHub Actions workflow for daily deployment
- JSON generation step
- Frontend build step
- File preservation (keep .git, CNAME, etc.)
- Deployment to gh-pages branch
- Error handling and rollback
- Verification and monitoring

### Context
The deployment pipeline orchestrates the entire system, running daily after the scraper completes. It must:
1. Generate JSON API files from fresh databases
2. Build static SPA assets
3. Deploy to GitHub Pages without downtime
4. Preserve critical files (.git, CNAME)

**Deployment target:** `gh-pages` branch on `CatalinPlesu/job-market` repo.

### Input Requirements
- JSON generator implementation (Issue #1)
- Frontend build setup (Issue #3)
- Access to repository databases
- GitHub Actions runner environment

### Output Definition

**Workflow File:**
`.github/workflows/deploy-pages.yml`

**Deployment Schedule:**
- Daily at 00:30 UTC (after scraper completes)
- Manual trigger via `workflow_dispatch`

**gh-pages Branch Structure:**
```
/
├── index.html              # SPA entry
├── assets/                 # JS, CSS
├── api/                    # JSON files
│   ├── jobs/
│   └── analysis/
├── .nojekyll              # Disable Jekyll
└── CNAME                   # Custom domain (if configured)
```

### Independence
- Requires JSON generator and frontend to be implemented
- Can test workflow with mock implementations
- Can use staging branch for testing before production

### Integration Points

**Calls:** JSON generator
- Command: `python -m json_generator --output pages/api`
- Exit code check for success/failure

**Calls:** Frontend build
- Command: `cd frontend && npm run build`
- Output: `frontend/dist/`

**Deploys to:** GitHub Pages
- Method: Force push to gh-pages branch
- Preservation: Keep .git, CNAME, .nojekyll

### Success Criteria
- [ ] Deployment completes in <10 minutes
- [ ] Zero downtime during deployment
- [ ] All files preserved correctly
- [ ] Site accessible immediately after deployment
- [ ] API endpoints return valid JSON
- [ ] Rollback works if deployment fails
- [ ] Deployment logs captured
- [ ] Can trigger manually via workflow_dispatch
- [ ] Scheduled deployments run reliably

### What This Does NOT Depend On
- Specific implementation details of JSON generator or frontend
- Just needs working entry points and expected outputs

### References
- **Specification:** `planning/github-pages-pseudo-api/04-deployment-automation.md`
- **Architecture:** `planning/github-pages-pseudo-api/01-architecture-strategy.md`
- **JSON generator interface:** Issue #1
- **Frontend build interface:** Issue #3

### Implementation Hints
1. Start with basic workflow (checkout, setup Python/Node)
2. Add JSON generation step
3. Add frontend build step
4. Implement file preservation logic
5. Add deployment to gh-pages
6. Add error handling and verification
7. Test with manual trigger first
8. Enable scheduled runs
