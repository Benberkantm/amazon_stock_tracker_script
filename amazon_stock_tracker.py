import os
import time
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pickle

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/91.0.864.59',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    return random.choice(user_agents)

def check_amazon_stock(url, retries=3):
    try:
        headers = {'User-Agent': get_random_user_agent()}
        response = requests.get(url, headers=headers, timeout=10)
        time.sleep(random.uniform(1, 3))  # Random delay
        
        if response.status_code != 200:
            logger.error(f"Error status code: {response.status_code} for URL: {url}")
            return "Unknown Product", False
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Multiple selectors for title
        title_selectors = [
            ('span', {'id': 'productTitle'}),
            ('h1', {'id': 'title'}),
            ('span', {'class': 'product-title-word-break'}),
            ('span', {'class': 'a-size-large product-title-word-break'}),
            ('span', {'class': 'a-size-medium a-color-base a-text-normal'})
        ]
        
        title = "Unknown Product"
        for selector in title_selectors:
            element = soup.find(selector[0], selector[1])
            if element:
                title = element.text.strip()
                break
        if title == "Unknown Product":
            logger.warning(f"Could not find product title for URL: {url}")
                
        # Multiple selectors for stock status
        stock_selectors = [
            ('div', {'id': 'availability'}),
            ('span', {'class': 'a-size-medium a-color-success'}),
            ('div', {'id': 'deliveryMessageMirId'})
        ]
        
        in_stock = False
        for selector in stock_selectors:
            element = soup.find(selector[0], selector[1])
            if element and any(x in element.text.lower() for x in ['in stock', 'ships', 'delivered']):
                in_stock = True
                break
        if not in_stock:
            logger.warning(f"Could not determine stock status for URL: {url}")
        
        logger.info(f"Successfully scraped {title} from URL: {url}")
        return title, in_stock
        
    except Exception as e:
        if retries > 0:
            wait_time = (4 - retries) * 2  # Exponential backoff
            logger.warning(f"Retrying {url} in {wait_time} seconds due to error: {str(e)}")
            time.sleep(wait_time)
            return check_amazon_stock(url, retries - 1)
        else:
            logger.error(f"Error checking {url} after retries: {str(e)}")
            return "Unknown Product", False

def load_cookies_from_chrome():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-data-dir=C:/Users/suley/AppData/Local/Google/Chrome/User Data")  # Adjust the path as needed
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.amazon.com")
    time.sleep(5)  # Wait for the page to load completely
    cookies = driver.get_cookies()
    driver.quit()
    return cookies

def apply_cookies_to_session(session, cookies):
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

def check_amazon_stock_selenium(url, cookies=None):
    try:
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        if cookies:
            driver.get("https://www.amazon.com")
            for cookie in cookies:
                driver.add_cookie(cookie)
        
        driver.get(url)
        time.sleep(random.uniform(1, 3))  # Random delay
        
        # Multiple selectors for title
        title_selectors = [
            (By.ID, 'productTitle'),
            (By.ID, 'title'),
            (By.CLASS_NAME, 'product-title-word-break'),
            (By.CLASS_NAME, 'a-size-large.product-title-word-break'),
            (By.CLASS_NAME, 'a-size-medium.a-color-base.a-text-normal')
        ]
        
        title = "Unknown Product"
        for by, value in title_selectors:
            try:
                element = driver.find_element(by, value)
                if element:
                    title = element.text.strip()
                    break
            except:
                continue
        if title == "Unknown Product":
            logger.warning(f"Could not find product title for URL: {url}")
                
        # Multiple selectors for stock status
        stock_selectors = [
            (By.ID, 'availability'),
            (By.CLASS_NAME, 'a-size-medium.a-color-success'),
            (By.ID, 'deliveryMessageMirId'),
            (By.CLASS_NAME, 'a-color-price')
        ]
        
        in_stock = False
        for by, value in stock_selectors:
            try:
                element = driver.find_element(by, value)
                if element:
                    text = element.text.lower()
                    if any(x in text for x in ['in stock', 'ships', 'delivered']):
                        in_stock = True
                    elif 'currently unavailable' in text or 'we don\'t know when or if this item will be back in stock' in text:
                        in_stock = False
                        break
            except:
                continue
        if not in_stock:
            logger.warning(f"Could not determine stock status for URL: {url}")
        
        logger.info(f"Successfully scraped {title} from URL: {url}")
        driver.quit()
        return title, in_stock
        
    except Exception as e:
        logger.error(f"Error checking {url} with Selenium: {str(e)}")
        return "Unknown Product", False

def main():
    main_file = 'amazon_products.xlsx'
    cookies_file = 'cookies.pkl'
    
    # Load cookies from Chrome if not already saved
    if not os.path.exists(cookies_file):
        cookies = load_cookies_from_chrome()
        with open(cookies_file, 'wb') as f:
            pickle.dump(cookies, f)
    else:
        with open(cookies_file, 'rb') as f:
            cookies = pickle.load(f)
    
    # Create new file if doesn't exist
    if not os.path.exists(main_file):
        df = pd.DataFrame({
            'URL': [],
            'Product Name': [],
            'In Stock': [],
            'Last Checked': []
        })
        df.to_excel(main_file, index=False)
    
    while True:
        try:
            # Read existing file
            df = pd.read_excel(main_file)
            
            # Update stock status
            for index, row in df.iterrows():
                title, in_stock = check_amazon_stock_selenium(row['URL'], cookies)
                df.loc[index, 'Product Name'] = title
                df.loc[index, 'In Stock'] = in_stock
                df.loc[index, 'Last Checked'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save updates
            df.to_excel(main_file, index=False)
            
            # Generate out-of-stock report
            out_of_stock = df[~df['In Stock']]
            if not out_of_stock.empty:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                report_name = f'out_of_stock_{timestamp}.xlsx'
                out_of_stock.to_excel(report_name, index=False)
                logger.info(f"Generated out-of-stock report: {report_name}")
            
            # Wait before next check
            logger.info("Waiting 1 hour before next check...")
            time.sleep(3600)
            
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            time.sleep(60)  # Wait 1 minute before retrying if error occurs

if __name__ == "__main__":
    logger.info("Starting Amazon stock monitoring...")
    main()