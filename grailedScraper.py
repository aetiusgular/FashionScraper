import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from playwright.sync_api import sync_playwright




HEADERS = {
  'accept': 'application/json',
  'accept-encoding': 'gzip, deflate, br, zstd',
  'accept-language': 'en-US,en;q=0.9',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15'
}




def get_product_links(query):
  search_url = f"https://www.grailed.com/shop?query={query}"
  print(f"Fetching links from: {search_url}")
 
  product_links = []
 
  with sync_playwright() as p:
      print("Launching browser...")
      browser = p.chromium.launch(headless=True)
      page = browser.new_page(
          user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15'
      )
     
      try:
          print("Navigating to page...")
          page.goto(search_url, wait_until="load", timeout=30000)
          print("Page loaded, waiting for product links...")
         
          # Wait a bit for dynamic content to load
          page.wait_for_timeout(3000)
         
          # Wait for product links to load
          page.wait_for_selector('a[href*="/listings/"]', timeout=15000)
          print("Product links found!")
         
          # Get all product links
          link_elements = page.locator('a[href*="/listings/"]').all()
          print(f"Found {len(link_elements)} product links")
         
          for link in link_elements:
              link_href = link.get_attribute('href')
              if link_href:
                  if "https" in link_href:
                      full_url = link_href
                  else:
                      full_url = "https://grailed.com" + link_href
                 
                  if full_url not in product_links:
                      product_links.append(full_url)
      except Exception as e:
          print(f"Error fetching page: {e}")
      finally:
          browser.close()
          print("Browser closed")
 
  return product_links




def extract_product_info(product_url):
  response = requests.get(product_url, headers=HEADERS)


  soup = BeautifulSoup(response.text, "html.parser")


  script_tag = soup.find('script', id="__NEXT_DATA__")


  data = json.loads(script_tag.string)
  initial_data = data['props']['pageProps']
  product_data = initial_data['listing']
  seller_data = product_data['seller']


  product_info = {
      "id": product_data['id'],
      "name": product_data['title'],
      "Designer": product_data['designerNames'],
      "price": product_data['price'],
      "orignal price": product_data['priceDrops'],
      "sold": product_data['sold'],
      "soldAt": product_data['soldAt'],
      "soldPrice": product_data['soldPrice'],
      "description": product_data['description'],
      "size": product_data['size'],
      "category": product_data['category'],
      "condition": product_data['condition'],
      "color etc.": product_data['traits'],
      "shipping": product_data['shipping'],
      "photosURlS": product_data['photos']
  }


  seller_info = {
      "user": seller_data['username'],
      "rating": seller_data['sellerScore']['ratingAverage']
  }


  return product_info, seller_info
def main():
  OUTPUT_FILE = "product_info.jsonl"
 
  with open(OUTPUT_FILE, 'w') as file:
      while True:
          print(f"\n--- Fetching search page ---")
          links = get_product_links("rick owens")
         
          if not links:
              print("No more links. Stopping.")
              break
         
          print(f"Processing {len(links)} products from page...")
          for i, link in enumerate(links, 1):
              try:
                  product_info, seller_info = extract_product_info(link)
                  if product_info:
                      data = {**product_info, **{"seller": seller_info}}
                      file.write(json.dumps(data) + "\n")
                      print(f"  [{i}/{len(links)}] ✓ Saved: {product_info.get('name', 'Unknown')}")
              except Exception as e:
                  print(f"  [{i}/{len(links)}] ✗ Failed to process {link}. Error: {e}")
 
  print(f"\nDone! Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
  main()

