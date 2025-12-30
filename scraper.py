import asyncio
import random
import pandas as pd
from playwright.async_api import async_playwright

# The only URL we need
URL = "https://www.adidas.co.in/women-shoes-outlet"

async def run_scraper():
    async with async_playwright() as p:
        #persistent context to avoid being blocked
        context = await p.chromium.launch_persistent_context(
            "./browser_session",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = context.pages[0]
        data = []
        
        print("Opening Adidas...")
        await page.goto(URL, wait_until="domcontentloaded")
        
        #handle the Privacy Modal
        await asyncio.sleep(5) 
        try:
            await page.get_by_text("ACCEPT TRACKING").click()
        except:
            pass

        #manual check wait
        print("Waiting 15s for manual verification...")
        await asyncio.sleep(15)

        for current_page in range(1, 8):
            print(f"Scraping Page {current_page}...")

            #7 Scroll to load products
            for _ in range(7):
                await page.mouse.wheel(0, 800)
                await asyncio.sleep(1.5)

            #extracting the 5 required fields
            cards = await page.query_selector_all('article[data-testid="plp-product-card"]')
            for card in cards:
                name = await card.query_selector('.name')
                sale = await card.query_selector('[data-testid="main-price"]')
                mrp = await card.query_selector('[data-testid="original-price"]')
                link = await card.query_selector('a[data-testid="product-card-description-link"]')

                if name:
                    sale_txt = await sale.inner_text() if sale else "N/A"
                    all_link = await link.get_attribute('href') if link else ""
                    
                    data.append({
                        "URL": "https://www.adidas.co.in" + all_link,
                        "Product Name": (await name.inner_text()).strip(),
                        "Brand": "Adidas",
                        "Sale Price": sale_txt.replace("Sale price", "").strip(),
                        "MRP": (await mrp.inner_text()).replace("Original price", "").strip() if mrp else sale_txt
                    })

            #next Page Navigation
            next_btn = page.locator('a[data-testid="pagination-next-button"]')
            if current_page < 7 and await next_btn.is_visible():
                await next_btn.click()
                await asyncio.sleep(8)
            else:
                break

        #Save to CSV
        pd.DataFrame(data).to_csv("Final_dataset.csv", index=False)
        print("Saved to Final_dataset.csv")
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())