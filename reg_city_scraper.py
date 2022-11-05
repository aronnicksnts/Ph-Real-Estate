#Scrapes all the current available regions and regions in Lamudi
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import json
import tqdm


#Get all region name
URL = "https://www.lamudi.com.ph/sitemap/house-for-buy-locations/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find_all("a", class_="sitemap-link")
regions = {}
#Gets all regions in the results and creates a dictionary
#Where the regionName acts as the key and it contains the
#href name of the particular region
for region in results:
    regionName = region.get_text().split("in ")[1]
    regionName = regionName.replace(" ", "-")
    regionhref = region['href'].split('/')[3]
    regions[regionName] = regionhref
#Free memory by deleting unneeded variables
del page, soup, results
#Saves all cities of a particular region in a JSON file
def getCities(url, regionName):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("a", class_="sitemap-link")
    cities = {}
    for city in results:
        cityName = city.get_text().split("in ")[1]
        cityName = cityName.replace(" ", "-")
        cityhref = city['href'].split('/')[3]
        cities[cityName] = cityhref
    with open(f"{regionName}.json", "w") as write:
        json.dump(cities, write)
        write.close()


#Gets all cities in a particular region and stores them in
#a text file which is named as a JSON file with the
#region's name as the file name
#and contains the cities href name
regionLinks = []
for region in regions:
    URL = f"https://www.lamudi.com.ph/sitemap/{region}-cities-house-for-buy/"
    regionLinks.append(URL)

# with Pool(2) as p, tqdm.tqdm(total=len(regionLinks)) as pbar:
#     for link in p.imap_unordered(getCities(), regionLinks):
#         pbar.update()
