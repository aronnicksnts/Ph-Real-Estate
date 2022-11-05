# Scrapes all available houses, apartments, and condominium listings 
# for sale and for rent in each of the cities
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import tqdm
import pandas as pd

propertyTypes = ["house", "apartment", "condominium"]
offerTypes = ['buy', 'rent']

#urlTemplate  "https://www.lamudi.com.ph/{region}/{city-name}/{barangayName}/{propertyTypes}/{offerTypes}/?page={pageNumber}"

df = pd.read_csv("BarangayData.csv")