# Scrapes all barangays/villages within a particular city and stores them 
# in a JSON file
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from p_tqdm import p_map
import pandas as pd

#Gets all barangays in a particular city and stores them in a csv file
def getBarangays(city):
    url = f"https://www.lamudi.com.ph/sitemap/{city[2]}-areas-house-for-buy/"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("a", class_="sitemap-link")
    barangays = []
    #Gets Region name from URL
    for barangay in results:
        #Gets the City Name
        barangayhref = barangay['href'].split('/')[5].lower()
        barangays.append({"regionName": city[1], 'cityName': city[2], 
        'barangayName': barangayhref})
    df = pd.DataFrame(barangays, columns=["regionName", "cityName", "barangayName"])
    return df


cityData = pd.read_csv("CityData.csv")
#Runs getCities by Pooling
if __name__ == "__main__":
    print("Getting All Barangays in All Cities")
    with Pool(4) as p:
        df = pd.DataFrame(columns=["regionName", "cityName", "barangayName"])
        data = p_map(getBarangays, cityData.itertuples())
    pd.concat(data, axis=0).to_csv("csv files\\BarangayData.csv", index=False)