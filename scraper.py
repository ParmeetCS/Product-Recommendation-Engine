from playwright.sync_api import sync_playwright
import pandas as pd

def get_text(locator, selector, default=""):
    loc = locator.locator(selector)
    if loc.count() > 0:
        return loc.first.text_content(timeout=1000).strip()
    return default

def get_attribute(locator, selector, attribute, default=""):
    loc = locator.locator(selector)
    if loc.count() > 0:
        return loc.first.get_attribute(attribute) or default
    return default

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

        print("Navigating to eBay home page...")
        page.goto("https://www.ebay.com/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(2000)

        search_input = page.locator("input[type='text'][name='_nkw']")
        if search_input.count() > 0:
            print(f"Searching for '{product_name}'...")
            search_input.fill(product_name)
            page.wait_for_timeout(1000)
            search_input.press("Enter")
        else:
            print("Search input not found, navigating directly...")
            page.goto(f"https://www.ebay.com/sch/i.html?_nkw={product_name}", wait_until="domcontentloaded", timeout=45000)

        page.wait_for_load_state("domcontentloaded", timeout=20000)
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

            if layout_type == "new":
                title = get_text(item, ".s-card__title")
                if title.lower() == "shop on ebay" or not title:
                    continue

                price = get_text(item, ".s-card__price")

                shipping = ""
                attr_rows = item.locator(".s-card__attribute-row")
                for j in range(attr_rows.count()):
                    row_text = attr_rows.nth(j).text_content(timeout=500).strip()
                    if "shipping" in row_text.lower() or "free" in row_text.lower():
                        shipping = row_text
                        break

                condition = get_text(item, ".s-card__subtitle")
                link = get_attribute(item, "a.s-card__link", "href")
                image = get_attribute(item, ".s-card__image", "src")

            else:  
                title = get_text(item, ".s-item__title, .s-item_title")
                if title.lower() == "shop on ebay" or not title:
                    continue

                price = get_text(item, ".s-item__price, .s-item_price")
                shipping = get_text(item, ".s-item__shipping")
                condition = get_text(item, ".SECONDARY_INFO")
                link = get_attribute(item, "a.s-item__link", "href")
                image = get_attribute(item, "img", "src")

            product.append({
                "Title": title,
                "Price": price,
                "Shipping": shipping,
                "Condition": condition,
                "Image": image,
                "URL": link
            })

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