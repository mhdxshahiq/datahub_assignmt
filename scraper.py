import asyncio
import random
import pandas as pd
from playwright.async_api import async_playwright

# The website we want to scrape
TARGET_URL = "https://www.adidas.co.in/women-shoes-outlet"

async def run_my_scraper():
    # Open the browser
    async with async_playwright() as p:
        user_folder = "./my_session"
        browser_context = await p.chromium.launch_persistent_context(
            user_folder,
            headless=False, # We want to see the browser window
            args=["--disable-blink-features=AutomationControlled"], # Helps hide that this is a bot
            viewport={'width': 1280, 'height': 800}
        )
        
        page = browser_context.pages[0]
        product_list = []
        
        print("Opening the Adidas website...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        
        # Accept Tracking popup
        await asyncio.sleep(5) 
        try:
            accept_button = page.get_by_text("ACCEPT TRACKING")
            if await accept_button.is_visible():
                await accept_button.click()
                print("Clicked the accept button.")
        except:
            print("No popup found")

    
        print("Waiting 15 seconds for the page to load")
        await asyncio.sleep(15)

        # 4. Scrape multiple pages
        for current_page_number in range(1, 8): #want 7 pages
            print(f"Working on Page {current_page_number}...")

            #7 Scroll Rule
            #the shoes to load on the screen
            for i in range(1, 8):
                await page.mouse.wheel(0, 800) #scroll down 800 pixels
                print(f"Scroll {i} of 7 done")
                await asyncio.sleep(1.5)

            #Collect the data from the page
            all_cards = await page.query_selector_all('article[data-testid="plp-product-card"]')
            print(f"Found {len(all_cards)} shoes on this page.")

            for card in all_cards:
                name_tag = await card.query_selector('.name')
                sale_tag = await card.query_selector('[data-testid="main-price"]')
                mrp_tag = await card.query_selector('[data-testid="original-price"]')
                link_tag = await card.query_selector('a[data-testid="product-card-description-link"]')

                #found a name, we save the detail
                if name_tag:
                    shoe_name = await name_tag.inner_text()
                    
                    #if there is no sale price, it maybe sold out
                    sale_price = await sale_tag.inner_text() if sale_tag else "N/A"
                    mrp_price = await mrp_tag.inner_text() if mrp_tag else sale_price
                    
                    #get the link to the shoe
                    relative_url = await link_tag.get_attribute('href') if link_tag else ""
                    full_url = "https://www.adidas.co.in" + relative_url

                    #adding info to our list
                    product_list.append({
                        "URL": full_url,
                        "Product Name": shoe_name.strip(),
                        "Brand": "Adidas",
                        "Sale Price": sale_price.replace("Sale price", "").strip(),
                        "MRP": mrp_price.replace("Original price", "").strip()
                    })

            #Click the 'Next' button to go to the next page
            next_btn = page.locator('a[data-testid="pagination-next-button"]')
            
            if current_page_number < 7: # Don't click 'Next' on the last page
                if await next_btn.is_visible():
                    print("Clicking the Next button...")
                    await next_btn.scroll_into_view_if_needed()
                    await next_btn.click()
                    await asyncio.sleep(8) #wait for the new page to load
                else:
                    print("no Next button. Stopping.")
                    break

        #save everything to a CSV file
        print("Saving data to Final_dataset.csv")
        df = pd.DataFrame(product_list)
        df.drop_duplicates(subset=['URL'], inplace=True) # Remove any double entries
        df.to_csv("Final_dataset.csv", index=False)
        
        print("All done")
        await asyncio.sleep(5)
        await browser_context.close()


if __name__ == "__main__":
    asyncio.run(run_my_scraper())