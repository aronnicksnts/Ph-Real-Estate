# Scrapes all available listing links in the website of lamudi given the filters.
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from p_tqdm import p_map
import pandas as pd
import random
import json
from functools import reduce

proxy = pd.read_csv("csv files\\Free_Proxy_List.csv")
proxy = proxy.to_dict('records')

cityData = pd.read_csv("csv files\\CityDataExpanded.csv")

# Regions that are to be processed where the link of the listings would be scraped
# Regions that have more than 0 listings and less than 2900 would be included in this list.
regionData = cityData.groupby("regionName").sum().reset_index(level=0)


# URL TEMPLATE
# https://www.lamudi.com.ph/{region}/{prop type}/{offer type}/?page={page number}

# All links that needs to be visited by the program
allLinks = []
# Getting links from each of the region that have less than 2900 listings available in that certain region
for region in regionData.to_dict('records'):
    # Add the number of pages needed to traverse the number of available listings per region
    # Add an extra 10 pages for assurance (In the case that new listings were made whilst scraping)
    for key in region.keys():
        if key == 'regionName': 
            continue
        if region[key] < 2900 and region[key] > 0:
            for i in range(1,(region[key] // 30) + 11):
                propType = key.split('-')[0]
                offerType = key.split('-')[1]
                allLinks.append(f"https://www.lamudi.com.ph/{region['regionName']}/{propType}/{offerType}/?page={i}")

