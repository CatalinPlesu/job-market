// --- Debug Script for jobber.md ---
console.log("Highlighting job links and pagination on jobber.md");

// Selector for job links based on config
const jobLinkSelector = 'a.mui-8ugpds';
// Selector for pagination links (general pattern based on config)
// This might need fine-tuning per site after inspection if the pattern is complex
const paginationSelector = 'a[href*="page-"]';

// --- Determine First Page URL ---
const currentUrl = window.location.href;
let firstPageUrl = null;

// Attempt to construct the first page URL based on the detected pattern
// This is a heuristic and might not work perfectly for every URL structure
if (currentUrl.includes('page-')) {
    // If the pattern is found in the current URL, try replacing the page number part
    // Example: If pattern is 'page=' and URL is '.../page=3', replace 'page=3' part
    // Example: If pattern is 'jobs-moldova/' and URL is '.../jobs-moldova/2', replace the number part
    const regexPattern = new RegExp(/page\-\d+/, 'i'); // Use the escaped regex from Python
    firstPageUrl = currentUrl.replace(regexPattern, 'page-1');
} else {
    // If the pattern is not in the current URL, assume the base URL (without page info) is the first page
    // This is often true for sites like delucru.md where ?page=1 is the same as no page param
    // Or construct based on the template provided in the config
    firstPageUrl = 'https://jobber.md/jobs/page-1/';
    // Replace the placeholder again, just in case the template itself was used
    firstPageUrl = firstPageUrl.replace('{{page}}', '1'); // Double braces to escape in Python format string
}

console.log("Potential First Page URL (copy and paste into address bar):", firstPageUrl);

// Function to highlight an element
function highlightElement(element) {
  if (element && !element.style.outline) { // Only highlight if not already highlighted
    element.style.outline = '3px solid red';
    element.style.outlineOffset = '2px';
    element.style.backgroundColor = 'rgba(255, 0, 0, 0.2)'; // Optional: semi-transparent background
    // Store original styles to potentially revert later
    element.dataset.originalOutline = element.style.outline;
    element.dataset.originalOutlineOffset = element.style.outlineOffset;
    element.dataset.originalBg = element.style.backgroundColor;
  }
}

// Function to remove highlight
function removeHighlight(element) {
  if (element && element.dataset.originalOutline) {
    element.style.outline = element.dataset.originalOutline || '';
    element.style.outlineOffset = element.dataset.originalOutlineOffset || '';
    element.style.backgroundColor = element.dataset.originalBg || '';
    delete element.dataset.originalOutline;
    delete element.dataset.originalOutlineOffset;
    delete element.dataset.originalBg;
  }
}

// Find and highlight job links
const jobLinks = document.querySelectorAll(jobLinkSelector);
console.log(`Found ${jobLinks.length} job links matching selector "${jobLinkSelector}".`);
jobLinks.forEach(link => highlightElement(link));

// Find and highlight pagination links
const paginationLinks = document.querySelectorAll(paginationSelector);
console.log(`Found ${paginationLinks.length} potential pagination links matching selector "${paginationSelector}".`);
paginationLinks.forEach(link => highlightElement(link));

// Optional: Add a helper function to remove highlights
window.removeJOBBER_MDHighlights = function() {
    jobLinks.forEach(removeHighlight);
    paginationLinks.forEach(removeHighlight);
    console.log("Highlights removed for jobber.md.");
};

console.log("Highlighting complete. Check the console for counts and the potential first page URL. Run removeJOBBER_MDHighlights() to remove highlights.");