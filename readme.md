# App tui menu workflow

Meanings:
TUI Menu entris - [m] 
Docs on details of implementation - [d] 

Entries:
- [m] 1. Print Config
    - [d] Prints config.py config.py contents
    - [d] Prints config.json contents
- [m] 2. Generate Scraper config
    -[d] in config.py i will have settings to reach out to an LLM api
    -[d] i will use all links of sites in config list of sites to generate config.json
        -[d] i will use something equivalent to curl in python i htink it is beatusoup as it is a server side rendered app
        -[d] will tell teh ai with a prompt to identify 2 things:
            1.[d] selector to select all job items on any page, to be the generic selector 
            2.[d] method to navigate pages ex base url +number to incremept page 
        -[d] will fetch a page using page selector and will tell ai to give me all selectors which woudl give all useful data about a job.
            here is possible to give it 2 or 3 pages, to make sure that we don't miss any selector.
-[m] 3. Generate Debug javascript
    -[d] generates a self contained javascript that can be injectd by hadn in console, and it will have the effect of colorizing the text that will be selected in a distinct way to see how if it woks well 
    -[d] this will be in a genraatd floder js/sitename, because each site probably will have differnt selectors
- [m] 4. Scrape data
    - [d] scraped data shoudl be stored in a sqlite database, separate talbes per site, and the config should think of the structure for the tables of sites, as they might be different.
    - [d] the scraping process state should be cached in a state.json in case the program crashes, to be albe to reload it witht problems, for this purpose you can use tinydbd json database for easy, it shuld store all the state to be able to relaod it , on ce it finishes it should remove and clean this file so we know it woked well
    - [d] should  respect robots.txt not to get me banned regrading delay not to ddos their service.
    - [d] if no rule is set for their site, lets assume 1 s to be polite. 
    - [d] but we can do the scraping in paralelle on all sites at same time as it shoud not conflict and cause problems
    - [d] scraping is a process of 2 steps, which are followign
    - [d] 1. step 1. shoud use the json config to navigate on each page of jobs, page + number and collect url of job postings, and to stop when a page + number is 404 or an error no such page exists
    - [d] 2. step 2. should use the list of job postins to scrape them and to parse them using the config rules generated.
- [m] 5. Analyze data
- [m] 6. Generate website
