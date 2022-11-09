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

regionData = pd.read_excel("Initial Summary.xlsx", "Region Summary")

# Regions that are to be processed where the link of the listings would be scraped
# Regions that have more than 0 listings and less than 2900 would be included in this list.
dataHouseBuy = regionData.loc[(regionData['Sum of house-buy'] > 0) & (regionData["Sum of house-buy"] < 2900)][['Region Name', 'Sum of house-buy']]
dataHouseRent = regionData.loc[(regionData['Sum of house-rent'] > 0) & (regionData["Sum of house-rent"] < 2900)][['Region Name', 'Sum of house-rent']]
dataAptBuy = regionData.loc[(regionData['Sum of apartment-buy'] > 0) & (regionData["Sum of apartment-buy"] < 2900)][['Region Name', 'Sum of apartment-buy']]
dataAptRent = regionData.loc[(regionData['Sum of apartment-rent'] > 0) & (regionData["Sum of apartment-rent"] < 2900)][['Region Name', 'Sum of apartment-rent']]
dataCondoBuy = regionData.loc[(regionData['Sum of condominium-buy'] > 0) & (regionData["Sum of condominium-buy"] < 2900)][['Region Name', "Sum of condominium-buy"]]
dataCondoRent = regionData.loc[(regionData['Sum of condominium-rent'] > 0) & (regionData["Sum of condominium-rent"] < 2900)][['Region Name', "Sum of condominium-rent"]]

# URL TEMPLATE
# https://www.lamudi.com.ph/{region}/{prop type}/{offer type}/?page={page number}

# Concatenating all data
dataMerge = [dataHouseBuy, dataHouseRent, dataAptBuy, dataAptRent, dataCondoBuy, dataCondoRent]
data_merged = reduce(lambda left,right: pd.merge(left,right, on=['Region Name'], how='outer'), dataMerge).fillna('void')

# This would contain all of the links that needs to be processed by the program, each of the data 
allLinks = []

for row in data_merged.itertuples(index=False):
    # Row 0-6 - Region Name, house-buy, house-rent, apartment-buy, apartment-rent, condo-buy, condo-rent
    pass