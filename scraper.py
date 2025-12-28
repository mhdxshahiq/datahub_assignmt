import asyncio
import random
import pandas as pd
from playwright.async_api import async_playwright

# Requirements: URL, Product Name, Brand, Sale Price, MRP
TARGET_URL = "https://www.adidas.co.in/women-shoes-outlet"

async def scrape_adidas():
    async with async_playwright() as p:
        # Use Persistent Context to maintain session and bypass detection
        user_data_dir = "./browser_session"
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={'width': 1366, 'height': 768}
        )
        
        page = context.pages[0]
        all_products = []
        current_page = 1
        max_pages = 7 

        try:
            print(f"Navigating to {TARGET_URL}...")
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=90000)
            
            # --- 1. HANDLE PRIVACY MODAL ---
            await asyncio.sleep(5)
            accept_btn = page.get_by_text("ACCEPT TRACKING", exact=True)
            if await accept_btn.is_visible():
                await accept_btn.click()
                print("Privacy modal cleared.")

            # --- 2. HUMAN CHALLENGE PAUSE ---
            print(">>> Solve any security checks manually! Waiting 15s...")
            await asyncio.sleep(15) 

            while current_page <= max_pages:
                print(f"--- Scraping Page {current_page} ---")
                
                # --- 3. THE 7-SCROLL RULE ---
                # Scroll enough to trigger the 12-product grid detection
                for i in range(1, 8):
                    await page.mouse.wheel(0, random.randint(700, 1000))
                    await asyncio.sleep(random.uniform(0.8, 1.5))
                
                # --- 4. DATA EXTRACTION ---
                # Fetching the 5 required fields: URL, Name, Brand, Sale Price, MRP
                cards = await page.query_selector_all('article[data-testid="plp-product-card"]')
                print(f"Detected {len(cards)} products on page {current_page}.")

                for card in cards:
                    name_el = await card.query_selector('.name')
                    sale_el = await card.query_selector('[data-testid="main-price"]')
                    mrp_el = await card.query_selector('[data-testid="original-price"]')
                    link_el = await card.query_selector('a[data-testid="product-card-description-link"]')

                    if name_el:
                        name = await name_el.inner_text()
                        sale_price = await sale_el.inner_text() if sale_el else "Sold Out"
                        mrp = await mrp_el.inner_text() if mrp_el else sale_price
                        link = await link_el.get_attribute('href') if link_el else ""

                        all_products.append({
                            "URL": f"https://www.adidas.co.in{link}" if link.startswith('/') else link,
                            "Product Name": name.strip(),
                            "Brand": "Adidas",
                            "Sale Price": sale_price.replace("Sale price", "").strip(),
                            "MRP": mrp.replace("Original price", "").strip()
                        })

                # --- 5. PAGINATION (USING YOUR EXACT INSPECT DATA) ---
                # Targeting the specific data-testid you found
                next_button = page.locator('a[data-testid="pagination-next-button"]')
                
                if current_page < max_pages:
                    # Ensure we scroll to the button after the 12th product is detected
                    await next_button.scroll_into_view_if_needed()
                    if await next_button.is_visible():
                        print(f"Next button detected. Navigating to page {current_page + 1}...")
                        await next_button.click()
                        # Wait for the next grid of 12 products to render
                        await asyncio.sleep(random.uniform(6, 9))
                        current_page += 1
                    else:
                        print("Next button not found. Finishing.")
                        break
                else:
                    break

            # --- 6. PANDAS STRUCTURING ---
            df = pd.DataFrame(all_products)
            df.drop_duplicates(subset=['URL'], inplace=True)
            df.to_csv("Final_dataset.csv", index=False)
            print(f"Success! {len(df)} products saved to 'Final_dataset.csv'.")

        except Exception as e:
            print(f"Scraper Error: {e}")
        
        finally:
            print("Finished. Browser will remain open for 30s to verify.")
            await asyncio.sleep(30)
            await context.close()

if __name__ == "__main__":
    asyncio.run(scrape_adidas())