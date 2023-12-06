import requests
from bs4 import BeautifulSoup as bs
import logging
import pandas as pd
import os
import sys
import random
import time

city = "Chicago_IL"

#using multiple user agents to avoid request blocking
user_agents = [
    #'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',                   #chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.41',   #edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.277'  #opera
]

BASE_DIR = os.getcwd()
logging.basicConfig(filename=os.path.join(BASE_DIR, "scraper_multiple_logs.log") , level=logging.INFO)

description = []
price = []
address = []
amount_reduced = []
link = []

for count in range(1,11):
    url = f"https://www.realtor.com/realestateandhomes-search/{city}/pg-{count}"
    
    headers = {
    'User-Agent': random.choice(user_agents),
    'Accept-Language': 'en-US,en;q=0.9'
    }
    
    response = requests.get(url, headers=headers)
    
    #adding delay in requests to avoid ip blocking
    time.sleep(2)
    
    soup = bs(response.text, features='lxml')
    try:
        response = requests.get(url, headers=headers)
        status = response.status_code

        #check for error in the response
        if status==400 or status==401 or status==403 or status==404:
            logging.error("Bad Request or Unauthorized or Forbidden or Not Found. Terminating execution!")
            sys.exit()

        soup = bs(response.text, features='lxml')

        logging.info(f" Finding all properties on page {count}...")
        all_properties = soup.find_all("div", class_="BasePropertyCard_propertyCardWrap__Z5y4p")

        #property_info = []
        for i,each_property in enumerate(all_properties):
            card_content = each_property.find("div", class_="CardContent__StyledCardContent-rui__sc-7ptz1z-0 dsJFdl card-content card-content")

            if card_content:    
                #extracting description
                logging.info(f" Collecting description of property {i+1} from page {count}...")
                description.append(card_content.find("div", class_="base__StyledType-rui__sc-108xfm0-0 kpUjhd message").text)

                #extracting prices
                logging.info(f" Collecting price of property {i+1} from page {count}...")
                price.append(card_content.find("div", class_="Pricestyles__StyledPrice-rui__btk3ge-0 bvgLFe card-price").text)

                #extracting addresses
                logging.info(f" Collecting address of property {i+1} from page {count}...")
                address_div = card_content.find("div", class_="card-address truncate-line")
                if address_div:
                    address_parts = address_div.find_all("div", class_="truncate-line")
                    #address.append(" ".join([part.text.strip() for part in address_parts]))
                    address.append(" ".join([part.text for part in address_parts]))
                else:
                    logging.warning(f" Address not found of property {i+1} on page {count}!!!")
                    address.append("Address not found")

                #extracting amount reduced
                logging.info(f" Collecting reduced amount of property {i+1} from page {count}...")
                reduced_amount_div = card_content.find("div", class_="card-reduced-amount")
                if reduced_amount_div:
                    reduced_amount = reduced_amount_div.find("div", class_="Pricestyles__StyledPrice-rui__btk3ge-0 bvgLFe").text
                    amount_reduced.append(reduced_amount)
                else:
                    amount_reduced.append("Amount has not reduced")

                #extracting links
                logging.info(f" Collecting web link of property {i+1} from page {count}...")
                anchor_tag = card_content.find("a", class_="LinkComponent_anchor__0C2xC")
                if anchor_tag:
                    href = anchor_tag.get("href")
                    link.append(f"https://www.realtor.com/{href}")
                else:
                    logging.warning(f" Link not found of property {i+1} on page {count}!!!")
                    link.append("Link not found")

            else:
                logging.error(f" Request timed out. Card content not found. Terminating execution!")
                print("Request timed out. Card content not found. Terminating execution!")
                sys.exit()
                
        data = {
            "Address": address,
            "Price": price,
            "Description": description,
            "Amount_Reduced": amount_reduced,
            "Link": link
            }

        #creating a pandas dataframe from the extracted data
        logging.info(" Saving extracted data into dataframe...")
        df = pd.DataFrame(data)

        #saving file as csv
        logging.info(" Saving data as a CSV file...")
        df.to_csv(f"realestate_data_of_{city}.csv")
    
    #catching exceptions
    except Exception as e:
        print(e)