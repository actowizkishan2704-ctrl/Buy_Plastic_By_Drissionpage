from DrissionPage import ChromiumPage, ChromiumOptions
from concurrent.futures import ThreadPoolExecutor
import time
import json
import os
# --- Configuration ---
NUM_BROWSERS = 2  # Number of browser windows to open
TABS_PER_BROWSER = 3  # How many tabs each browser will handle concurrently
MAX_WORKERS = NUM_BROWSERS * TABS_PER_BROWSER

# A sample batch of URLs to scrape
with open("./product_urls.json", 'r') as f:
    product_urls = json.load(f)
os.makedirs("saved_pages/home", exist_ok=True)
os.makedirs("saved_pages/categories", exist_ok=True)
os.makedirs("saved_pages/products", exist_ok=True)
os.makedirs("saved_pages/combinations", exist_ok=True)

def scrape_worker(tab_obj, url):
    """
    The main logic executed per tab.
    Pass the specific tab object into this function.
    """
    try:
        print(f"[Start] Navigating to: {url} on Tab ID: {tab_obj.tab_id}")

        # Navigate and fetch your data here
        tab_obj.get(url)
        time.sleep(2)  # Simulate watching/waiting for data to load
        with open(f"saved_pages/products/product_{url.split("/")[-2].replace("-", "_")}.html","w",encoding="utf-8") as f:
                f.write(tab_obj.html)
        product_data=[]
        product_title = ''.join(tab_obj.ele("xpath://h1[contains(@class, 'productView-title')]").texts())

        radios=tab_obj.eles("xpath://div[@role='radiogroup']")
        combination_details=[]
        combo_no=1
        if len(radios)>=1:
            radio_1=radios[0].eles("xpath://div[contains(@class, 'form-option-wrapper')]//input")
            for color in radio_1:
                color.click()
                if len(radios)>=2:    
                    radio_2=radios[1].eles("xpath://div[contains(@class, 'form-option-wrapper')]//input")
                    for thick in radio_2:
                        thick.click()
                        if len(radios)>=3:
                            radio_3=radios[2].eles("xpath://div[contains(@class, 'form-option-wrapper')]//input")
                            for size in radio_3:
                                size.click() 
                                with open(f"saved_pages/combinations/product_{url.split("/")[-2].replace("-", "_")}.html","w",encoding="utf-8") as f:
                                    f.write(tab_obj.html)

                                combo_no += 1                       
                                sku_id=''.join(tab_obj.ele("xpath://dd[@data-product-sku]").texts())
                                prices=''.join(tab_obj.ele("xpath://div[@class='productView-product']//span[@data-product-price-without-tax]").texts())
                                current_stock = ''.join(tab_obj.ele("xpath://span[@data-product-stock]").texts())                            
                                combination_details.append({
                                        "sku_id":sku_id,
                                        "prices":prices,
                                        "stocks_count":current_stock
                                    })
                        else:        
                            with open(f"saved_pages/combinations/product_{url.split("/")[-2].replace("-", "_")}.html","w",encoding="utf-8") as f:
                                f.write(tab_obj.html)

                            combo_no += 1  
                            sku_id = ''.join(tab_obj.ele("xpath://dd[@data-product-sku]").texts())
                            prices = ''.join(tab_obj.ele("xpath://div[@class='productView-product']//span[@data-product-price-without-tax]").texts())
                            current_stock = ''.join(tab_obj.ele("xpath://span[@data-product-stock]").texts())                          
                            combination_details.append({
                                    "sku_id":sku_id,
                                    "prices":prices,
                                    "stocks_count":current_stock
                                })
                else:
                    with open(f"saved_pages/combinations/product_{url.split("/")[-2].replace("-", "_")}.html","w",encoding="utf-8") as f:
                        f.write(tab_obj.html)

                    combo_no += 1 
                    sku_id = ''.join(tab_obj.ele("xpath://dd[@data-product-sku]").texts())
                    prices = ''.join(tab_obj.ele("xpath://div[@class='productView-product']//span[@data-product-price-without-tax]").texts())
                    current_stock = ''.join(tab_obj.ele("xpath://span[@data-product-stock]").texts())                           
                    combination_details.append({
                                        "sku_id":sku_id,
                                        "prices":prices,
                                        "stocks_count":current_stock
                                    })
        product_data.append({
                "product_name":product_title,
                "product_details":combination_details
            })
            # all_combination_details.extend(product_data)
        tab_obj.close()

        title = tab_obj.title
        print(f"[Success] Title found: '{title}' from {url}")

    except Exception as e:
        print(f"[Error] Failed to scrape {url}: {e}")

def run_parallel_scraper(urls, num_browsers, tabs_per_browser):
    # 1. Initialize all required browser instances and allocate tabs
    browsers = []
    available_tabs = []

    print(f"Launching {num_browsers} browser windows...")
    for i in range(num_browsers):
        # Crucial: auto_port prevents browsers from clashing on the same port
        co = ChromiumOptions().auto_port()
        # Optional: Run headless if you don't want windows popping up everywhere
        # co.headless()

        browser = ChromiumPage(addr_or_opts=co)
        browsers.append(browser)

        # Create the required number of tabs for this specific browser
        for j in range(tabs_per_browser):
            if j == 0:
                # The first tab already exists by default
                available_tabs.append(browser.latest_tab)
            else:
                # Create extra concurrent tabs
                new_tab = browser.new_tab()
                available_tabs.append(new_tab)

    print(f"Total concurrent workers ready: {len(available_tabs)}")

    # 2. Distribute the workload across our pre-allocated tabs using ThreadPoolExecutor
    # We loop over the available tabs to map each URL to an isolated tab environment
    with ThreadPoolExecutor(max_workers=len(available_tabs)) as executor:
        futures = []

        # Zip/Cycle URLs over the available tab instances
        for idx, url in enumerate(urls):
            # Select a tab round-robin style
            assigned_tab = available_tabs[idx % len(available_tabs)]

            # Submit the task to the pool
            f = executor.submit(scrape_worker, assigned_tab, url)
            futures.append(f)

        # Wait for all tasks to complete
        for future in futures:
            future.result()

    # 3. Clean up and close all browsers
    print("Scraping completed. Closing all browsers...")
    for browser in browsers:
        browser.quit()

if __name__ == "__main__":
    # Prevent multi-threading execution issues on certain systems
    run_parallel_scraper(product_urls, NUM_BROWSERS, TABS_PER_BROWSER)