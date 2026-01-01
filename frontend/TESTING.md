# Frontend Testing Checklist

## Manual Testing Guide

### Prerequisites
1. Generate API data:
   ```bash
   python -m json_generator --output frontend/api
   ```

2. Start local server:
   ```bash
   cd frontend
   python -m http.server 8000
   ```

3. Open browser: http://localhost:8000

## Test Cases

### 1. Home Page (/)
- [ ] Page loads without errors
- [ ] "Moldova Job Market" title displays
- [ ] Statistics card shows total jobs count
- [ ] "Browse Jobs" button navigates to /jobs
- [ ] Navigation menu works
- [ ] Theme toggle switches between light/dark
- [ ] Footer displays correctly
- [ ] Mobile: All elements are responsive

### 2. Jobs Page (/jobs)
- [ ] Page loads with job listings
- [ ] Jobs display in extra slim format (HN style)
- [ ] Each job shows:
  - [ ] Index number
  - [ ] Title (clickable)
  - [ ] Company badge
  - [ ] Location
  - [ ] Salary (if available)
  - [ ] Posting date
- [ ] Page count displays correctly
- [ ] Pagination controls work:
  - [ ] Next button loads page 2
  - [ ] Previous button goes back
  - [ ] Buttons disabled at boundaries
- [ ] Mobile: Jobs list is readable and clickable

### 3. Filtering
#### Basic Filters
- [ ] Job Function filter shows options
- [ ] Selecting filter updates job list instantly
- [ ] Filtered count displays correctly
- [ ] Seniority filter works
- [ ] City filter works
- [ ] Remote Work filter works
- [ ] Industry filter works
- [ ] Company filter works

#### Advanced Filters
- [ ] "Show More" button reveals advanced filters
- [ ] Employment Type filter works
- [ ] Contract Type filter works
- [ ] Department filter works
- [ ] Specialization filter works
- [ ] Education Level filter works
- [ ] Company Size filter works
- [ ] "Show Less" button hides advanced filters

#### Filter Badges
- [ ] Active filters appear as badges above filters
- [ ] Each badge shows filter name and value
- [ ] Clicking X on badge removes that filter
- [ ] "Clear All" button removes all filters
- [ ] Removing filters updates job list

#### Hierarchical Filtering
- [ ] Multiple filters work together (AND logic)
- [ ] Filter options remain relevant when other filters active
- [ ] Available options count updates dynamically
- [ ] No jobs found message when filters too restrictive

### 4. Job Detail Page (/jobs/:id)
- [ ] Clicking job title navigates to detail page
- [ ] "Back to Jobs" button works
- [ ] Job title and company display
- [ ] Badges show: company, location, seniority

#### Parsed Tab
- [ ] Tab is selected by default
- [ ] Salary section shows correctly
- [ ] Requirements section displays:
  - [ ] Education level
  - [ ] Years of experience
  - [ ] Languages (as badges)
  - [ ] Hard skills (as badges)
  - [ ] Soft skills
- [ ] Responsibilities list displays
- [ ] Benefits show as badges
- [ ] All sections handle missing data gracefully

#### Raw Tab
- [ ] Clicking "Raw View" tab switches view
- [ ] Original title displays
- [ ] Original company displays
- [ ] Original language displays
- [ ] Source site displays
- [ ] Scraped timestamp displays
- [ ] Original description shows in preformatted text
- [ ] "View Original Posting" link opens in new tab

### 5. Analysis Dashboard (/analysis)
- [ ] Page loads without errors
- [ ] Statistics cards display:
  - [ ] Total jobs analyzed
  - [ ] Jobs with salary
  - [ ] Unique companies
- [ ] Info alert shows (when data not generated)
- [ ] Available analyses list displays
- [ ] Each analysis card shows:
  - [ ] Title
  - [ ] ID
  - [ ] Temporal badge (if applicable)
  - [ ] "View" button
- [ ] Clicking "View" loads analysis data (console)

### 6. Navigation
- [ ] All navbar links work:
  - [ ] Home (/)
  - [ ] Jobs (/jobs)
  - [ ] Analysis (/analysis)
- [ ] Logo/title links to home
- [ ] Browser back/forward buttons work
- [ ] URL hash updates correctly (#/jobs, #/jobs/1, etc.)
- [ ] Direct URL access works (refresh on any page)
- [ ] Mobile: Hamburger menu works (if applicable)

### 7. Theme Toggle
- [ ] Light theme (default):
  - [ ] White background
  - [ ] Dark text
  - [ ] Proper contrast
- [ ] Dark theme:
  - [ ] Dark background
  - [ ] Light text
  - [ ] Proper contrast
- [ ] Theme persists across page navigation
- [ ] All components respect theme
- [ ] DaisyUI components use theme colors

### 8. Responsive Design
#### Desktop (1920x1080)
- [ ] Layout uses full width (container)
- [ ] Filters show in 3 columns
- [ ] Job listings readable
- [ ] Navigation horizontal
- [ ] All elements properly spaced

#### Tablet (768x1024)
- [ ] Layout adapts to 2 columns
- [ ] Filters stack properly
- [ ] Navigation still horizontal
- [ ] Touch targets adequate
- [ ] No horizontal scroll

#### Mobile (375x667)
- [ ] Layout uses 1 column
- [ ] Filters stack vertically
- [ ] Navigation stacks/collapses
- [ ] Job cards full width
- [ ] Text remains readable
- [ ] Buttons touch-friendly
- [ ] No content cut off

### 9. Performance
- [ ] Initial page load <2 seconds
- [ ] Filter updates instant (<100ms)
- [ ] Page transitions smooth
- [ ] No console errors
- [ ] No console warnings (CDN blocks expected)
- [ ] Smooth scrolling
- [ ] No layout shift on load

### 10. Error Handling
- [ ] Invalid job ID shows appropriate message
- [ ] Missing API files show error
- [ ] Network errors handled gracefully
- [ ] 404s handled properly
- [ ] Console shows helpful error messages

### 11. Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

### 12. Accessibility
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible
- [ ] Labels present for form elements
- [ ] Semantic HTML used
- [ ] Alt text for images (if any)
- [ ] Color contrast sufficient
- [ ] Skip navigation available

## Automated Testing (Future)

### Unit Tests
- [ ] Filter matching logic
- [ ] Utility functions (formatSalary, formatDate)
- [ ] State management
- [ ] API client

### Integration Tests
- [ ] Component rendering
- [ ] User interactions
- [ ] Routing
- [ ] Data fetching

### E2E Tests
- [ ] Complete user flows
- [ ] Multi-step interactions
- [ ] Cross-page navigation

## Performance Testing

### Lighthouse Scores (Target)
- [ ] Performance: >90
- [ ] Accessibility: >90
- [ ] Best Practices: >90
- [ ] SEO: >90

### Metrics
- [ ] First Contentful Paint <1.5s
- [ ] Time to Interactive <2.5s
- [ ] Largest Contentful Paint <2.5s
- [ ] Cumulative Layout Shift <0.1

## Security Testing
- [ ] No secrets in code
- [ ] No XSS vulnerabilities
- [ ] Sanitized data from API
- [ ] HTTPS in production
- [ ] Proper CORS configuration

## Test Results

### Test Date: ___________
### Tester: ___________
### Environment: ___________
### Browser: ___________
### Issues Found: ___________

## Notes
- CDN blocking by ad blockers is expected in some environments
- For production testing, ensure CDNs are accessible
- Test with real generated data, not just sample data
- Test both empty and populated data scenarios
