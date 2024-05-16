import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import streamlit as st
import os


def scrape_products(shop_url, currency, google_product_category):
    # Send a GET request to the shop URL
    response = requests.get(shop_url)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all the product elements
    products = soup.find_all('div', class_='ProductList-item')
    
    # Create a list to store the product data
    product_data = []
    
    for product in products:
        # Extract the product information
        id = product['data-item-id']
        product_type = product['data-item-id']
        product_page_link = product.find('a', class_='ProductList-item-link')['href']
        
        # Check if the product page link starts with a valid scheme
        if not product_page_link.startswith(('http://', 'https://')):
            product_page_link = urljoin(shop_url, product_page_link)
        
        title = product.find('h1', class_='ProductList-title').text.strip()
        sku = product['data-item-id']
        price_element = product.find('div', class_='product-price')
        price = ''
        sale_price = ''
        if price_element:
            price_text = price_element.text.strip()
            if 'Original Price:' in price_text:
                price = price_text.split('Original Price:')[1].strip()
            if 'Sale Price:' in price_text:
                sale_price = price_text.split('Sale Price:')[1].split('Original')[0].strip()
        on_sale = 'sale' in product['class']
        stock = 'in stock'
        availability = 'in stock'
        condition = 'new'
        visible = True
        image_link = product.find('img', class_='ProductList-image')['data-src']

        # Append the currency to the prices
        price = f"{currency} {price}" if price else ''
        sale_price = f"{currency} {sale_price}" if sale_price else ''
        
        # Send a GET request to the product page
        product_response = requests.get(product_page_link)
        product_soup = BeautifulSoup(product_response.content, 'html.parser')
        
        # Extract the product description
        description_element = product_soup.find('div', class_='ProductItem-details-excerpt')
        description = description_element.text.strip() if description_element else ''
        
        # Append the product data to the list
        product_data.append([
            id, product_type, product_page_link, title, description,
            sku, '', '', '', '', '', '', '', '', '', '', '', '', 
            price, sale_price, on_sale, stock, google_product_category, availability, condition, '', '', '', '', visible,
            image_link
        ])
    
    return product_data

# Streamlit app
st.title("Squarespace Digital Product Export")

# Input fields
shop_url = st.text_input("Enter the shop URL")
currency = st.text_input("Enter the currency")
google_product_category = st.text_input("Enter the Google product category")

if st.button("Download Digital Product Catalog as CSV"):
    if shop_url:
        # Scrape the product data
        product_data = scrape_products(shop_url, currency, google_product_category)
        
        # Define the CSV file path
        csv_file_path = 'product_data.csv'
        
        # Define the CSV headers
        csv_headers = [
            'id', 'product_type', 'link', 'title', 'description',
            'SKU', 'variant_names', 'variant_values', 'Option Name 2', 'Option Value 2',
            'Option Name 3', 'Option Value 3', 'Option Name 4', 'Option Value 4',
            'Option Name 5', 'Option Value 5', 'Option Name 6', 'Option Value 6', 
            'price', 'sale_price', 'On Sale', 'Stock', 'google_product_category', 
            'availability', 'condition', 'Weight', 'Length', 'Width', 'Height', 'Visible',
            'image_link'
        ]
        
        # Write the product data to the CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(csv_headers)
            writer.writerows(product_data)
        
        st.success(f"Product data has been exported to {csv_file_path}")
        
        # Display the product data in the app
        st.table(product_data)
    else:
        st.warning("Please enter a shop URL.")






