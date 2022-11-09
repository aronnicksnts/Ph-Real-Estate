# Scrapes the number of houses, condominiums, and aparments
# for sale and for rent in each of the cities
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from p_tqdm import p_map
import pandas as pd
import random
import json
propertyTypes = ["house", "apartment", "condominium"]
offerTypes = ['buy', 'rent']

#Rotate IP
proxy = pd.read_csv("csv files\\Free_Proxy_List.csv")
proxy = proxy.to_dict('records')
#urlTemplate  "https://www.lamudi.com.ph/{region}/{city-name}/{barangayName}/{propertyTypes}/{offerTypes}"

dfOrig = pd.read_csv("CityData.csv")
unscrapedData = []

# URL Template City https://www.lamudi.com.ph/{regionName}/{cityName}/{propertyType}/{offerType}/
def getNumPropertiesCity(data):
    url = f"https://www.lamudi.com.ph/{data['regionName']}/{data['cityName']}/" \
    f"/{data['propertyType']}/{data['offerType']}"

    #Gets a random Proxy to use to get the page request
    randomProxy = proxy[random.randint(0, len(proxy)-1)]
    page = requests.get(url, proxies={'http': f"http://{randomProxy['ip']}:{randomProxy['port']}"})
    if page.status_code != 200:
        unscrapedData.append(data)
        print(data)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find("span", class_="CountTitle-number")
    if results:
        numList = results.getText().replace(",", "")
    else:
        numList = 0
    data = {"regionName": data['regionName'],
    "cityName": data['cityName'], 
    "propertyType": data['propertyType'], "offerType": data['offerType'],
    "numberOfListings": numList}
    df = pd.DataFrame([data.values()], columns= ["regionName", "cityName",
    "propertyType", "offerType", "numberOfListings"])
    return df

#Iterates through all available property type and offer type and checks each of the said unique combinations
if __name__ == "__main__":
    print("Getting All Available Listings per Property Type and Offer Type")
    allData = pd.DataFrame(columns= ["regionName", "cityName",
    "propertyType", "offerType", "numberOfListings"])
    with Pool(16) as p:
        for propertyType in propertyTypes:
            for offerType in offerTypes:
                dfMod = dfOrig
                dfMod['propertyType'] = propertyType
                dfMod['offerType'] = offerType
                data = p_map(getNumPropertiesCity, dfMod.to_dict('records'))
                allData = pd.concat([allData, pd.concat(data, axis=0)], ignore_index=True, axis=0)
    allData.to_csv("csv files\\CityDataExpanded.csv", index=False)

with open('unscrapedData.json', 'w') as f:
    json.dump(unscrapedData, f)