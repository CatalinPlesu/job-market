# Frontend Deployment Guide

## Overview
This guide explains how to deploy the Moldova Job Market frontend SPA to various hosting platforms.

## Prerequisites

1. Generate API JSON files:
```bash
python -m json_generator --output pages/api
```

2. The frontend files are in the `frontend/` directory
3. API data should be at `/api/` path relative to the frontend

## Deployment Options

### Option 1: GitHub Pages (Recommended)

#### Method A: Manual Deployment
1. Generate API files to `pages/api/`:
```bash
python -m json_generator --output pages/api
```

2. Copy frontend files to `pages/`:
```bash
cp -r frontend/* pages/
```

3. Commit and push to GitHub:
```bash
git add pages/
git commit -m "Update frontend and API data"
git push origin main
```

4. Enable GitHub Pages in repository settings:
   - Go to Settings > Pages
   - Source: Deploy from branch `main`
   - Folder: `/pages`
   - Save

5. Your site will be available at: `https://username.github.io/job-market/`

#### Method B: GitHub Actions (Automated)
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:  # Manual trigger

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Generate API files
        run: |
          python -m json_generator --output pages/api
      
      - name: Copy frontend
        run: |
          cp -r frontend/* pages/
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./pages
```

### Option 2: Netlify

1. Create a `netlify.toml` in the repository root:

```toml
[build]
  publish = "pages"
  command = "python -m json_generator --output pages/api && cp -r frontend/* pages/"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. Connect your GitHub repository to Netlify
3. Deploy!

### Option 3: Vercel

1. Create a `vercel.json` in the repository root:

```json
{
  "buildCommand": "python -m json_generator --output pages/api && cp -r frontend/* pages/",
  "outputDirectory": "pages",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

2. Connect your GitHub repository to Vercel
3. Deploy!

### Option 4: Static Hosting (Apache/Nginx)

1. Generate API files locally:
```bash
python -m json_generator --output pages/api
```

2. Copy frontend to pages:
```bash
cp -r frontend/* pages/
```

3. Upload `pages/` directory to your web server

4. Configure web server:

**Apache** - Create `.htaccess` in `pages/`:
```apache
RewriteEngine On
RewriteBase /
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^.*$ index.html [L,QSA]
```

**Nginx** - Add to server config:
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

## Project Structure After Deployment

```
pages/
├── index.html           # Frontend HTML
├── app.js               # Frontend JavaScript
├── README.md            # Frontend docs
└── api/
    ├── jobs/
    │   ├── index.json
    │   ├── page-1.json
    │   ├── page-2.json
    │   └── {id}/
    │       └── detail.json
    └── analysis/
        ├── index.json
        └── *.json
```

## Environment Configuration

The frontend uses hash-based routing (`#/`) by default, which works on all platforms without server configuration.

To use history API routing (cleaner URLs):
1. Update `app.js` routing configuration
2. Configure server rewrites (see above)

## Testing Deployment Locally

1. Generate API files:
```bash
python -m json_generator --output pages/api
```

2. Copy frontend:
```bash
cp -r frontend/* pages/
```

3. Start local server:
```bash
cd pages
python -m http.server 8000
```

4. Open: http://localhost:8000

## Continuous Deployment

### Daily Updates
To keep job data fresh, set up automated regeneration:

**GitHub Actions** (recommended):
- Runs daily
- Generates new API files
- Deploys automatically

**Cron Job** (self-hosted):
```bash
# Add to crontab
0 0 * * * cd /path/to/job-market && python -m json_generator --output pages/api
```

## Troubleshooting

### API Files Not Loading
- Check that `/api/` path is accessible
- Verify CORS headers if hosting API separately
- Check browser console for errors

### Routing Issues
- Hash routing (`#/`) works everywhere
- History API routing needs server rewrites
- Check `.htaccess` or Nginx config

### CDN Resources Blocked
- CDNs are loaded from:
  - jsdelivr.net (DaisyUI)
  - tailwindcss.com (Tailwind)
  - unpkg.com (Mithril.js)
  - jsdelivr.net (Chart.js)
- Check firewall/ad-blocker settings

### Performance Issues
- Enable gzip compression on server
- Use CDN for static assets
- Consider `.json.gz` for API files

## Security Considerations

1. **No Secrets in Frontend**: Never include API keys or secrets
2. **Data Sanitization**: Ensure JSON generator removes sensitive data
3. **HTTPS**: Always use HTTPS in production
4. **CORS**: Configure properly if API is on different domain

## Monitoring

Track deployment success:
- GitHub Actions logs
- Netlify/Vercel dashboards
- Server access logs
- Google Analytics (optional)

## Rollback

If issues occur:

**GitHub Pages**: Revert commit and push
**Netlify/Vercel**: Use dashboard to rollback
**Self-hosted**: Restore previous `pages/` directory

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review [frontend/README.md](../frontend/README.md)
- Open an issue on GitHub
