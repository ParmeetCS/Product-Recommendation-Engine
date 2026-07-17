from playwright.sync_api import sync_playwright, TimeoutError
import pandas as pd
import time

def scrapping(product_name):
    product = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            locale="en-US",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()

        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        
        for attempt in range(3):
            try:
                print(f"Navigating to eBay home page (attempt {attempt+1}/3)...")
                page.goto("https://www.ebay.com/", wait_until="domcontentloaded", timeout=45000)
                break
            except Exception as e:
                print(f"Failed to load eBay: {e}")
                if attempt < 2:
                    page.wait_for_timeout(3000)
                else:
                    print("Could not connect to eBay after 3 attempts.")

        page.wait_for_timeout(2000)

       
        search_input = page.locator("input[type='text'][name='_nkw']")
        if search_input.count() > 0:
            print(f"Searching for '{product_name}'...")
            try:
                search_input.fill(product_name)
                page.wait_for_timeout(1000)
                search_input.press("Enter")
            except Exception as e:
                print(f"Error searching via search input: {e}")
        else:
            print("Search input not found, navigating directly...")
            for attempt in range(3):
                try:
                    page.goto(f"https://www.ebay.com/sch/i.html?_nkw={product_name}", wait_until="domcontentloaded", timeout=45000)
                    break
                except Exception as e:
                    print(f"Direct navigation failed: {e}")
                    if attempt < 2:
                        page.wait_for_timeout(3000)

        try:
            page.wait_for_load_state("domcontentloaded", timeout=20000)
        except Exception as e:
            print(f"Load state wait timed out: {e}")
        page.wait_for_timeout(5000)

            
        items = page.locator("li.s-item")
        layout_type = "classic"
        
        if items.count() <= 1:
            su_items = page.locator(".su-card-container")
            if su_items.count() > 0:
                items = su_items
                layout_type = "new"

        count = items.count()
        print(f"Found {count} items using {layout_type} layout.")

        for i in range(count):
            item = items.nth(i)

            try:
                if layout_type == "new":
                    title = item.locator(".s-card__title").first.text_content(timeout=2000).strip()
                    if title.lower() == "shop on ebay":
                        continue

                    try:
                        price = item.locator(".s-card__price").first.text_content(timeout=1000).strip()
                    except:
                        price = ""

                    
                    shipping = ""
                    try:
                        attr_rows = item.locator(".s-card__attribute-row")
                        for j in range(attr_rows.count()):
                            row_text = attr_rows.nth(j).text_content(timeout=500).strip()
                            if "shipping" in row_text.lower() or "free" in row_text.lower():
                                shipping = row_text
                                break
                    except:
                        pass

                    try:
                        condition = item.locator(".s-card__subtitle").first.text_content(timeout=1000).strip()
                    except:
                        condition = ""

                    try:
                        link = item.locator("a.s-card__link").first.get_attribute("href")
                    except:
                        link = ""

                    try:
                        image = item.locator(".s-card__image").first.get_attribute("src")
                    except:
                        image = ""

                else:  
                    title = item.locator(".s-item__title, .s-item_title").first.text_content(timeout=2000).strip()
                    if title.lower() == "shop on ebay":
                        continue

                    try:
                        price = item.locator(".s-item__price, .s-item_price").first.text_content(timeout=1000).strip()
                    except:
                        price = ""

                    try:
                        shipping = item.locator(".s-item__shipping").first.text_content(timeout=1000).strip()
                    except:
                        shipping = ""

                    try:
                        condition = item.locator(".SECONDARY_INFO").first.text_content(timeout=1000).strip()
                    except:
                        condition = ""

                    try:
                        link = item.locator("a.s-item__link").first.get_attribute("href")
                    except:
                        link = ""

                    try:
                        image = item.locator("img").first.get_attribute("src")
                    except:
                        image = ""

                product.append({
                    "Title": title,
                    "Price": price,
                    "Shipping": shipping,
                    "Condition": condition,
                    "Image": image,
                    "URL": link
                })

            except Exception as e:
                print(f"Error scraping item {i}: {e}")

        
        browser.close()
        df = pd.DataFrame(product)
        file_name = f"data/Ebay_{product_name}.csv"
        
        df.to_csv(file_name, index=False)
     
        print(df.head())

if __name__ == "__main__":
    import sys
    query = "laptop"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    scrapping(query)