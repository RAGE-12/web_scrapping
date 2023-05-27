import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def scrape_product_details(url):
    if not url.startswith('http'):
        url = urljoin(base_url, url)
    try:
        response = requests.get(url)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')

        description_element = soup.find('div', {'id': 'productDescription'})
        description = description_element.text.strip() if description_element else ''

        asin_element = soup.find('th', text='ASIN')
        asin = asin_element.find_next_sibling('td').text.strip() if asin_element else ''

        product_description = soup.find('div', {'id': 'productDescription'})
        product_description = product_description.text.strip() if product_description else ''

        manufacturer = soup.find('a', {'id': 'bylineInfo'})
        manufacturer = manufacturer.text.strip() if manufacturer else ''

        return {
            'Description': description,
            'ASIN': asin,
            'Product Description': product_description,
            'Manufacturer': manufacturer
        }
    except requests.exceptions.RequestException as e:
        print("An error occurred while making the request:", e)
        return None

def scrape_multiple_pages(base_url, num_pages, max_products):
    scraped_data = {
        'product_urls': [],
        'product_names': [],
        'product_prices': [],
        'ratings': [],
        'review_counts': []
    }

    products_count = 0
    page = 1

    while products_count < max_products and page <= num_pages:
        url = f"{base_url}&page={page}"

        response = requests.get(url)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')

        product_urls = [urljoin(base_url, a['href']) for a in soup.select('.a-link-normal.a-text-normal')]
        product_names = [h2.text.strip() for h2 in soup.select('.a-size-medium.a-color-base.a-text-normal')]
        product_prices = [span.text.strip() for span in soup.select('.a-price-whole')]
        ratings = [span.text.strip() for span in soup.select('.a-icon-alt')]
        review_counts = [span.text.strip() for span in soup.select('.a-size-base')]

        num_products = min(max_products - products_count, len(product_urls))
        scraped_data['product_urls'].extend(product_urls[:num_products])
        scraped_data['product_names'].extend(product_names[:num_products])
        scraped_data['product_prices'].extend(product_prices[:num_products])
        scraped_data['ratings'].extend(ratings[:num_products])
        scraped_data['review_counts'].extend(review_counts[:num_products])

        products_count += num_products
        page += 1
        time.sleep(1)

    return scraped_data

base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
num_pages = 20
max_products = 200
scraped_data = scrape_multiple_pages(base_url, num_pages, max_products)

csv_file = 'scraped_data.csv'

header = ['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews',
          'Description', 'ASIN', 'Product Description', 'Manufacturer']

with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(header)

    for i in range(len(scraped_data['product_urls'])):
        if i < len(scraped_data['product_names']):
            product_url = scraped_data['product_urls'][i]
            product_name = scraped_data['product_names'][i]
            product_price = scraped_data['product_prices'][i]
            rating = scraped_data['ratings'][i]
            review_count = scraped_data['review_counts'][i]

            additional_info = scrape_product_details(product_url)
            if additional_info is None:
                additional_info = {}

            row = [product_url, product_name, product_price, rating, review_count] + list(additional_info.values())

            writer.writerow(row)

print("Scraped data has been saved to", csv_file)