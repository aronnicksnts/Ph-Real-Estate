#Scrapes all the current available regions and cities within the said regions in Lamudi
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from p_tqdm import p_map
import pandas as pd


#Get all region name
URL = "https://www.lamudi.com.ph/sitemap/house-for-buy-locations/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find_all("a", class_="sitemap-link")
regions = []
#Gets all regions in the results and creates a list
#of the region names
for region in results:
    #Gets Region name from href
    regionhref = region['href'].split('/')[3].lower()
    regions.append(regionhref)
#Free memory by deleting unneeded variables
del page, soup, results

#Saves all Cities to a DataFrame
def getCities(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("a", class_="sitemap-link")
    cities = []
    #Gets Region name from URL
    regionName = url.split('/')[4].split('cities')[0][:-1]
    for city in results:
        #Gets the City Name
        cityhref = city['href'].split('/')[4].lower()
        cities.append({"regionName": regionName, "cityName": cityhref})
    df = pd.DataFrame(cities, columns=["regionName", "cityName"])
    return df


#Gets all cities in a particular region and stores them in
#a CSV file with two columns, the region's name and the city's href
regionLinks = []
for region in regions:
    URL = f"https://www.lamudi.com.ph/sitemap/{region}-cities-house-for-buy/"
    regionLinks.append(URL)

#Runs getCities by Pooling
if __name__ == "__main__":
    print("Getting All Cities in All Regions")
    with Pool(2) as p:
        df = pd.DataFrame(columns=["regionName", "cityName"])
        data = p_map(getCities, regionLinks)
    pd.concat(data, axis=0).to_csv("csv files\\CityData.csv", index=False)

