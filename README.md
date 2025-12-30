# Datahut Science Assignment: Adidas Scraper

This project is a Python-based web scraper built to collect product data from the **Adidas India Women's Shoes Outlet**.

---

## Technical Approach
* **Playwright**: Used because the site is **dynamic**. It allows the script to wait for JavaScript to fetch products that are not visible in the initial HTML.
* **Persistent Session**: I used a `browser_session` folder to save cookies. This mimics a real human user to bypass **403 Forbidden** security blocks.
* **7-Scroll Logic**: Implemented to handle **Lazy Loading**. The site only loads products as you scroll; 7 scrolls ensure the grid and "Next" button are fully detected.

## Data Collected
The following 5 attributes were extracted for each product:
* **URL**: Direct product link.
* **Product Name**: Name of the shoe.
* **Brand**: Hardcoded as "Adidas".
* **Sale Price**: The current price.
* **MRP**: Original price.

## Challenges & Solutions
* **Dynamic Content**: Handled by waiting for specific `data-testid` selectors.
* **Pagination**: Managed via a loop that clicks the "Next" button only after the 7-scroll loading is complete.
* **Bot Detection**: Bypassed using a persistent browser context instead of standard HTTP requests.

## Limitations
* **CAPTCHAs**: While the script waits 15 seconds for manual solving, it does not solve automatically.
* **Page Limit**: Set as 7 .

## How to Run
1. **Install tools**: `pip install playwright pandas`.
2. **Install Browser**: `playwright install chromium`.
3. **Execute**: `python scraper.py`.
