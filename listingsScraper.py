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
# Data that were unable to be scraped
unscrapedData = []

# Returns the links to be visited in a dictionary form with cities
def addCity(cityData, propType, offerType):
    links = {}
    # URL TEMPLATE
    # https://www.lamudi.com.ph/{region}/{city}/{prop type}/{offer type}/?page={page number}
    for i in range(1,(cityData[key] // 30) + 1):
        url = f"https://www.lamudi.com.ph/{cityData['regionName']}/{cityData['cityName']}/{propType}/{offerType}/?page={i}"
        links[url] = [propType, offerType]
    return links

# Returns the links to be visited in a dictionary form with barangays
def addBrgy(brgyData, propType, offerType, numList):
    links = {}
    # URL TEMPLATE
    # https://www.lamudi.com.ph/{region}/{city}/{brgyName}/{prop type}/{offer type}/?page={page number}
    for i in range(1,(numList // 30) + 1):
        url = f"https://www.lamudi.com.ph/{brgyData['regionName']}/{brgyData['cityName']}/{brgyData['barangayName']}" \
        f"/{propType}/{offerType}/?page={i}"
        links[url] = [propType, offerType]
    return links

def addLinks(url, numList):
    links = {}
    # URL TEMPLATE
    # https://www.lamudi.com.ph/{region}/{city}/{brgyName}/{prop type}/{offer type}/?page={page number}
    for i in range(1,(numList // 30) + 1):
        tempUrl = f"{url}/?page={i}"
        links[tempUrl] = [propType, offerType]
    return links

# Gets number of listings in the URL given
def getNumList(url):
    randomProxy = proxy[random.randint(0, len(proxy)-1)]
    
    page = requests.get(url, proxies={'http': f"http://{randomProxy['ip']}:{randomProxy['port']}"})
    if page.status_code != 200:
        unscrapedData.append(url)
        print("Unscraped: ", url)
        return None
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find('span', class_ = 'CountTitle-number')
    if results:
        numList = results.getText().replace(",", "")
    else:
        numList = 0
    return int(numList)

# Processes cities with more than 2900 listings, checks each of the brgys to see
# if they have less than 2900 listings and adds them to a dictionary which would be added to
# the masterlist of links
def procBrgys(brgyData, propType, offerType):
    # Checks if number of listing in the brgy is < 2900, if it is add it to the list
    url = f"https://www.lamudi.com.ph/{brgyData['regionName']}/{brgyData['cityName']}" \
        f"/{brgyData['barangayName']}/{propType}/{offerType}/"
    numListBrgy = getNumList(url)
    if numListBrgy < 2900:
        return addBrgy(brgyData, propType, offerType, numListBrgy)
    # Number of listings < 2900, process further, split it into different
    else:
        brgyLists = {}
        priceRanges = [[0,2500000], [2500001, 5000000], [5000001, 7500000], [7500001, 10000000],
        [10000001, 15000000], [15000001, 20000000], [20000001, 30000000], [30000001, 99999999999]]
        for priceRange in priceRanges:
            url = f"https://www.lamudi.com.ph/{brgyData['regionName']}/{brgyData['cityName']}" \
        f"/{brgyData['barangayName']}/{propType}/{offerType}/price:{priceRange[0]}-{priceRange[1]}"
            numListBrgy = getNumList(url)

            if numListBrgy < 2900 and numListBrgy > 0:
                brgyLists.update(addLinks(url, numListBrgy))
            elif numListBrgy > 2900:
                fileName = brgyData['barangayName']
                brgyData = [brgyData]
                brgyData = pd.DataFrame.from_dict(brgyData)
                brgyData.to_csv(f"csv files\\unscrapedData\\{fileName}.csv")
        return brgyLists


# Gets the details that a listing has their price, title, amenities, etc.
def getListingInfo(listInfo):
    url = listInfo[0]
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

    # Not stored properly
    # description = soup.find('div', class_='ViewMore-text-description')
    # description = description.getText()

    propertyType = listInfo[1][0]
    offerType = listInfo[1][1]


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

# Gets the listings available from the URL given
def getListingLinks(listInfo):
    url = listInfo[0]
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
        listingLinks[link['href']] = [listInfo[1][0], listInfo[1][1]]
    return listingLinks

# Gets the base URL for the listing
if __name__ == "__main__":
    # Getting links from each of the region 
    for region in regionData.to_dict('records'):
        # Add the number of pages needed to traverse the number of available listings per region
        # Add an extra 10 pages for assurance (In the case that new listings were made whilst scraping)
        for key in region.keys():
            if key == 'regionName': 
                continue
            print(f"Getting {region['regionName']} {key}")
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
                        brgyData = brgyData.loc[(brgyData['cityName'] == city['cityName'])]
                        for brgy in brgyData.to_dict('records'):
                            allLinks = {**allLinks, **procBrgys(brgy, propType, offerType)}
    
    allListingLinks = {}
    # Confirmation of all links
    pd.DataFrame(allLinks.items(), columns=['Link', 'PropOffer',]).to_csv('csv files\\AllLinks.csv')
    print("Getting all Links for Listings")
    with Pool(16) as p:
        data = p_map(getListingLinks, allLinks.items())

    # Adds the listingLinks created from data together into the allListingLinks
    for listingLinks in data:
        allListingLinks.update(listingLinks)
    # Save all listing links to a csv in case of crashing
    pd.DataFrame(allListingLinks.items(), columns=['Link', 'PropOffer']).to_csv('csv files\\AllListingLinks.csv')
    print("Getting all Listing data")
    with Pool(16) as p:
        data = p_map(getListingInfo, allListingLinks.items())
    pd.concat(data, axis=0).fillna('void').to_excel('csv files\\DataGathered.xlsx')
    

with open('unscrapedData.json', 'w') as f:
    json.dump(unscrapedData, f)