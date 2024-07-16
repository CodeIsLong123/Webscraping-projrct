import scrapy
from selenium import webdriver
import email
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import imaplib
import logging
from stack.items import StackItem
load_dotenv()   

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By



### Just a small script to get a hang of scrapy, this script scrapes the questions from the stackoverflow page
### Next i want to make a script that scrapes medium articles and integrate them into my notion page
### For this i need to use Selenium as well, to log into my medium account and scrape the articles

def setup_driver(): 
    driver = webdriver.Chrome()
    return driver



def load_credentials():
    
    email = os.getenv('EMAIL')
    password = os.getenv('GMAIL_PASSWORD')
    
    return email, password


def connect_to_gmail_imap(user, password):
    imap_url = 'imap.gmail.com'
    try:
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(user, password)
        mail.select('inbox')  


        status, data = mail.search(None, '(FROM "noreply@medium.com" SUBJECT "Sign in to Medium")')
        if status != 'OK' or not data[0]:
            logging.warning("Keine passenden E-Mails gefunden")
            return None

        latest_email_id = data[0].split()[-1]


        result, data = mail.fetch(latest_email_id, "(RFC822)")
        if result != 'OK':
            logging.error("Fehler beim Abrufen der E-Mail")
            return None

        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)

    
        html_content = None
        
        for part in email_message.walk():
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True).decode()
                break

        if not html_content:
            logging.warning("Kein HTML-Inhalt in der E-Mail gefunden")
            return None

        
        soup = BeautifulSoup(html_content, 'html.parser')
        signin_link = soup.find('a', class_='email-button', string='Sign in to Medium')

        if signin_link and 'href' in signin_link.attrs:
            cleaned_link = signin_link['href'].replace('&amp;', '&')
            logging.info(f"Sign-in Link gefunden: {cleaned_link}")
            print(cleaned_link)
            return cleaned_link
        else:
            logging.warning("Sign-in-Link nicht gefunden")
            return None

    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP Fehler: {e}")
        raise


class QuestionsScraperSpider(scrapy.Spider):
    name = 'stack'
    allowed_domains = ["medium.com"]
    start_urls = ["https://medium.com/m/signin", "https://medium.com"]
    driver = webdriver.Chrome()
    
    
    
    def parse(self, response):

        driver = setup_driver()
        driver.get(self.start_urls[0])
        driver.implicitly_wait(5)
        driver.find_element(
                By.XPATH,
                '//button[div="Sign in with email"]'
            ).click()

        time.sleep(2)
        
        button = driver.find_element(
            By.XPATH,
            '//input[@type="email"]'
        ).send_keys(os.getenv('EMAIL'))
        continue_button = driver.find_element(By.XPATH,
                                            './/button[text()="Continue"]'
                                            ).click()

        
        time.sleep(3)
        weiter_button = connect_to_gmail_imap(*load_credentials())
        driver.get(weiter_button)
        
        response = driver.page_source
        selector = Selector(text=response)

        # Extrahiere die gesamten Container
        containers = selector.xpath("//div[@class='gl la lb lc']")

        for container in containers:
            title = container.xpath(".//h2[contains(@class, 'am')]/text()").get().strip()
            link = container.xpath(".//a[./h2[contains(@class, 'am')]]/@href").get()
            
            print(f"Titel: {title}")
            print(f"Link: {link}")
            print("---")

        # for c in containers:
        #     print("-------------------------------------",c, "-------------------------------------")
        #     item = ItemLoader(
        #         item=StackItem(),
        #         response=response,
        #         selector=c
        #     )
            
            

        #     item.add_xpath(
        #             'title',
        #             './/h2/text()'
        #         )
        #     item.add_xpath(
        #             'link',
        #             './/div[@class="ly s"]//a/@href'
        #         )
        #     yield item.load_item()
            
            
            



        driver.quit()