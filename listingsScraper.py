# Scrapes all available listing links in the website of lamudi given the filters.
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from p_tqdm import p_map
import pandas as pd
import random
import json
from functools import reduce
import re

proxy = pd.read_csv("csv files\\Free_Proxy_List.csv")
proxy = proxy.to_dict('records')

cityData = pd.read_csv("csv files\\CityDataExpanded.csv")
brgyData = pd.read_csv("csv files\\BarangayData.csv")
# Regions that are to be processed where the link of the listings would be scraped
# Regions that have more than 0 listings and less than 2900 would be included in this list.
regionData = cityData.groupby("regionName").sum().reset_index(level=0)

# All links that needs to be visited by the program, with their property type and offer type
allLinks = {}

# Returns the links to be visited in a dictionary form with cities
def addCity(cityData, propType, offerType):
    links = {}
    # URL TEMPLATE
    # https://www.lamudi.com.ph/{region}/{city}/{prop type}/{offer type}/?page={page number}
    for i in range(1,(cityData[key] // 30) + 6):
        url = f"https://www.lamudi.com.ph/{cityData['regionName']}/{cityData['cityName']}/{propType}/{offerType}/?page={i}"
        links[url] = [propType, offerType]
    return links

# Returns the links to be visited in a dictionary form with barangays
def addBrgy(brgyData, propType, offerType):
    links = {}
    # URL TEMPLATE
    # https://www.lamudi.com.ph/{region}/{city}/{brgyName}/{prop type}/{offer type}/?page={page number}
    for i in range(1,(cityData[key] // 30) + 6):
        url = f"https://www.lamudi.com.ph/{brgyData['regionName']}/{brgyData['cityName']}/{brgyData['barangayName']}" \
        f"/{propType}/{offerType}/?page={i}"
        links[url] = [propType, offerType]
    return links

# Gets number of listings in a particular barangay depending on the property type and offer type
def getNumListBrgy(brgyData, propType, offerType):
    url = f"https://www.lamudi.com.ph/{brgyData['regionName']}/{brgyData['cityName']}" \
    f"/{brgyData['barangayName']}/{propType}/{offerType}/"
    randomProxy = proxy[random.randint(0, len(proxy)-1)]
    page = requests.get(url, proxies={'http': f"http://{randomProxy['ip']}:{randomProxy['port']}"})
    
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find('span', class_ = 'CountTitle-number')
    if results:
        numList = results.getText().replace(",", "")
    else:
        numList = 0
    return numList


# Getting links from each of the region 
for region in regionData.to_dict('records'):
    # Add the number of pages needed to traverse the number of available listings per region
    # Add an extra 10 pages for assurance (In the case that new listings were made whilst scraping)
    for key in region.keys():
        if key == 'regionName': 
            continue

        # Getting links from regions with less than 2900 listings available
        # URL TEMPLATE
        # https://www.lamudi.com.ph/{region}/{prop type}/{offer type}/?page={page number}
        if region[key] < 2900 and region[key] > 0:
            propType = key.split('-')[0]
            offerType = key.split('-')[1]
            for i in range(1,(region[key] // 30) + 6):
                url = f"https://www.lamudi.com.ph/{region['regionName']}/{propType}/{offerType}/?page={i}"
                allLinks[url] = [propType, offerType]
        
        # Getting links from regions with more than 2900 listings available
        elif region[key] > 2900:
            # Check cities of the region if they have more than 2900 listings, if not use the city 
            cities = cityData.loc[cityData['regionName'] == region['regionName']]

            for city in cities[['regionName', 'cityName', key]].to_dict('records'):
                propType = key.split('-')[0]
                offerType = key.split('-')[1]
                if city[key] < 2900 and city[key] > 0:
                    allLinks = {**allLinks, **addCity(city, propType, offerType)}
                elif city[key] > 2900:
                    # Use scraped Barangay Data and check their number of listings
                    pass
                

allListingLinks = {}
# Gets the base URL for the listing
def getListingLinks(url):
    randomProxy = proxy[random.randint(0, len(proxy)-1)]
    page = requests.get(url, proxies={'http': f"http://{randomProxy['ip']}:{randomProxy['port']}"})
    if page.status_code != 200:
        unscrapedData.append(url)
        print("Unscraped: ", url)

    soup = BeautifulSoup(page.content, "html.parser")

    links = soup.find_all('div', class_='row ListingCell-row ListingCell-agent-redesign')
    listingLinks = {}
    for link in links:
        link = link.find('a', href=True)
        listingLinks[link['href']] = [allLinks[url][0], allLinks[url][1]]

    return listingLinks
unscrapedData = []
# Gets the details of the listings
def getListingInfo(url):
    randomProxy = proxy[random.randint(0, len(proxy)-1)]
    page = requests.get(url, proxies={'http': f"http://{randomProxy['ip']}:{randomProxy['port']}"})
    if page.status_code != 200:
        unscrapedData.append(url)
        print("Unscraped: ", url)

    soup = BeautifulSoup(page.content, "html.parser")

    #All details have a padding of space, .strip() removes these paddings
    location = soup.find('h3', class_='Title-pdp-address')
    location = location.getText().strip()

    title = soup.find('h1', class_='Title-pdp-title')
    title = title.getText().strip()

    price = soup.find('div', class_='Title-pdp-price')
    price = price.getText().strip()
    price = re.sub('[^-~]', '', price)

    # Not stored properly
    # description = soup.find('div', class_='ViewMore-text-description')
    # description = description.getText()

    propertyType = allListingLinks[url][0]
    offerType = allListingLinks[url][1]

    details = soup.find_all('div', class_ = 'columns-2')
    allDetails = {}
    for detail in details:
        detailName = detail.find('div', class_='ellipsis').getText().strip()
        detailValue = detail.find(class_='last').getText().strip()
        allDetails[detailName] = detailValue
    amenities = soup.find_all('span', class_ = 'listing-amenities-name')
    allAmenities = {}
    for amenity in amenities:
        allAmenities[amenity.getText()] = 1

    #Put all other details in a single dictionary
    listingDetails = {'link': url, 'title': title, 'location': location,
    'price': price, 'propertyType': propertyType, 'offerType': offerType}
    #Convert all dictionaries to DataFrame to merge into one DF
    listingDetails = pd.DataFrame(listingDetails, index=[0])
    allDetails = pd.DataFrame(allDetails, index=[0])
    allAmenities = pd.DataFrame(allAmenities, index=[0])
    df = pd.concat([listingDetails, allDetails, allAmenities], axis=1)
    return df

allLinks = {'https://www.lamudi.com.ph/apartment/rent/': ['apartment', 'rent']}
if __name__ == "__main__":
    print("Getting all Links for Listings")
    with Pool(8) as p:
        data = p_map(getListingLinks, allLinks.keys())
    
    allListingLinks = data
    print("Getting all Listing data")
    with Pool(8) as p:
        data = p_map(getListingInfo, allListingLinks)
    pd.concat(data, axis=0).to_csv('trial.csv')
    

with open('unscrapedData.json', 'w') as f:
    json.dump(unscrapedData, f)