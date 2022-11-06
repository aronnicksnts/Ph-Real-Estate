# Scrapes all available houses, apartments, and condominium listings 
# for sale and for rent in each of the cities
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from p_tqdm import p_map
import pandas as pd

propertyTypes = ["house", "apartment", "condominium"]
offerTypes = ['buy', 'rent']

#urlTemplate  "https://www.lamudi.com.ph/{region}/{city-name}/{barangayName}/{propertyTypes}/{offerTypes}/?page={pageNumber}"

dfOrig = pd.read_csv("BarangayData.csv")

#Gets the number of available listings in a particular barangay, property type
#and offer Type
def getPropertiesAvailable(data):
    url = f"https://www.lamudi.com.ph/{data['regionName']}/{data['cityName']}/{data['barangayName']}" \
    f"/{data['propertyType']}/{data['offerType']}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find("span", class_="CountTitle-number")
    data = {"regionName": data['regionName'],
    "cityName": data['cityName'], "barangayName": data['barangayName'], 
    "propertyType": data['propertyType'], "offerType": data['offerType'],
    "numberOfListings": results.getText().replace(",", "")}
    df = pd.DataFrame([data.values()], columns= ["regionName", "cityName", "barangayName",
    "propertyType", "offerType", "numberOfListings"])
    return df

#Iterates through all available property type and offer type and checks each of the said unique combinations
if __name__ == "__main__":
    print("Getting All Available Listings per Property Type and Offer Type")
    allData = pd.DataFrame(columns= ["regionName", "cityName", "barangayName",
    "propertyType", "offerType", "numberOfListings"])
    with Pool(8) as p:
        for propertyType in propertyTypes:
            for offerType in offerTypes:
                dfMod = dfOrig
                dfMod['propertyType'] = propertyType
                dfMod['offerType'] = offerType
                data = p_map(getPropertiesAvailable, dfMod.to_dict('records'))
                allData = pd.concat([allData, pd.concat(data, axis=0)], ignore_index=True, axis=0)
    allData.to_csv("BarangayDataExpanded.csv", index=False)