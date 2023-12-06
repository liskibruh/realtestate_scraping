import requests
from bs4 import BeautifulSoup as bs
import logging
import pandas as pd
import os
import sys

city = "Chicago_IL"

url = f"https://www.realtor.com/realestateandhomes-search/{city}"

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
'Accept-Language': 'en-US;q=1.0,en;q=0.9'
}

BASE_DIR = os.getcwd()
logging.basicConfig(filename=os.path.join(BASE_DIR, "scraper_logs_new.log") , level=logging.INFO)

try:
    response = requests.get(url, headers=headers)
    soup = bs(response.text, features='lxml')
    
    logging.info(" Finding all properties...")
    all_properties = soup.find_all("div", class_="BasePropertyCard_propertyCardWrap__Z5y4p")
    
    description = []
    price = []
    address = []
    amount_reduced = []
    link = []
    #property_info = []
    for i,each_property in enumerate(all_properties):
        card_content = each_property.find("div", class_="CardContent__StyledCardContent-rui__sc-7ptz1z-0 dsJFdl card-content card-content")
    
        if card_content:    
            #extracting description
            logging.info(f" Collecting description of property {i+1}...")
            description.append(card_content.find("div", class_="base__StyledType-rui__sc-108xfm0-0 kpUjhd message").text)
        
            #extracting prices
            logging.info(f" Collecting price of property {i+1}...")
            price.append(card_content.find("div", class_="Pricestyles__StyledPrice-rui__btk3ge-0 bvgLFe card-price").text)
        
            #extracting addresses
            logging.info(f" Collecting address of property {i+1}...")
            address_div = card_content.find("div", class_="card-address truncate-line")
            if address_div:
                address_parts = address_div.find_all("div", class_="truncate-line")
                #address = " ".join([part.text.strip() for part in address_parts])
                #address.append(" ".join([part.text.strip() for part in address_parts]))
                address.append(" ".join([part.text for part in address_parts]))
            else:
                logging.warning(" Address not found!!!")
                address.append("Address not found")
            
            #extracting amount reduced
            logging.info(f" Collecting reduced amount of property {i+1}...")
            reduced_amount_div = card_content.find("div", class_="card-reduced-amount")
            if reduced_amount_div:
                reduced_amount = reduced_amount_div.find("div", class_="Pricestyles__StyledPrice-rui__btk3ge-0 bvgLFe").text
                amount_reduced.append(reduced_amount)
            else:
                amount_reduced.append("Amount has not reduced")
            
            #extracting links
            logging.info(f" Collecting web link of property {i+1}...")
            anchor_tag = card_content.find("a", class_="LinkComponent_anchor__0C2xC")
            if anchor_tag:
                href = anchor_tag.get("href")
                link.append(f"https://www.realtor.com/{href}")
            else:
                logging.warning(f" Link not found!!!")
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

#catcing exceptions
except Exception as e:
    print(e)