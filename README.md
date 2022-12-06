# About

The following github repositories explores the data available at [lamudi](lamudi.com.ph). The website gives available houses, condominiums, apartments, commercial, 
land for sale and for rent in the Philippines. The available data was then scraped, specifically houses, condominiums, and apartments for sale and for rent around the 
Philippines. 

## Methodology

The methodology of this project is split into several different parts.

### Understanding of the website:

To extract the data from lamudi, the website was first explored to give insight on how the website is structured. 

A total of ---,--- properties were for sale and --,--- properties were for rent at the time of retrieval (As of November 9, 2022). These properties could be grouped on
their specific location. Locations are grouped as follows: Region, City, Barangay. Furthermore, filters could be added as to search for a more specific listing.
Filters can include but is not limited to the price, number of bedrooms, number of bathrooms, floor area, land size, and available amenities (if any).

When looking through listings, the number of available listings per page is at maximum 30 listings. And the maximum number of pages available to be given by the website is 100 pages. Going beyond page 100 gives out an error. As the maximum listings that can be given through particular filters is 3000 listings, 
extractions of the total listings per city is extracted. Afterwards, city listings with more than 3000 listings per rent/sale is further divided into their respective
barangays. If the number of listings is still beyond 3000, the listings in that particular barangay would be subdivided further to specific price ranges until listings can go below 3000 listings.

### Preminilary Data Understanding:

In total, there are 74 available regions and a total of 1483 cities. The number of available listings were scraped depending on the property type (Condominium, Apartment, or House) and their offer type (Sale or Rent). These listings were then aggregated to a file named *CityDataExpanded*.

To visualize the data on the aggregated data, it was copied on over to *Initial Summary*. On the sheet *summary* shows the number of regions with no available listing depending on the property type and offer type. The data of the available listings per city was aggregated to their respective regions and the total number of available listings per property type and offer type was obtained. From here, a total of 444 unique filters (region, property type, and offer type was permutated) was obtained. Of these **444** filters, a total of **208** of them had no listings available in them and a total of 11 had more than 2900 listings in them. 2900 was considered as the limit as to account for new listings within the area.

With this, the 208 unique filters would be discarded and would not be used to find available listings and the 7 unique filters with more than 2900 listings would be split further to their respective cities, if the number of available listings is still beyond 2900, it would be further split into each barangay. Furthermore, if the listings is still beyond 2900 on each barangay, more filters would be applied until less than 2900 listings are available.

On each of the listings, the location of the listing is included with their own description, details which includes various facts about the listing such as the land size, floor area, number of bathrooms and bedrooms, etc. and additional amenities if any. 

With this, a csv file would be created per property and offer type (a total of 6) which would contain the listings
- Title
- Location
- Details
- Amenities

If a property does not have a detail or amenities included, the cell would be left blank.

### Gathering of the Data:

Python was used to scrape the data off the website. To speed up the processing of scraping off the listings, multiprocessing was used. The code at *listingScraper.py* is the main python file to scrape the data off Lamudi. The preqrequisite of this python file is having the Free_Proxy_List.csv which provides the proxies that would be used for the requests of the websites, CityDataExpanded which provides the number of available listings in a particular City and Region, and BarangayData.csv which provides what barangays are there in a particular City.

The python file checks the CityDataExpanded for the available number of available listings in a particular region and city. If the number of listings available in a region is in total, less than 2900, the webpages to get the listings url are added to a master list which contains all of the URLs that contains the listings URL. If, however, the listings is more than 2900, we drill down into the region and use their particular cities to get the listings. Additionally, if the city has more than 2900 listings, we drill down further with the city's barangays, and finally, if the listings is still more than 2900 in each of the barangay, we drill down further with additional filters such as the price. 

Once all of these URLs are gathered, they are visited one-by-one where the listing URLs in the master list is gathered. These gathered URLs are then stored in another list. The gathered URL would be the one that would contain the details of the listings such as the title, location, details, and amenities. Once all of these URLs are gathered, they are then processed and the data would be stored in a pandas DataFrame. Afterwards, it would be exported to a CSV file.

### Understanding of the gathered data
In total 77808 listings were gathered from lamudi with a total of 148 columns. There is a total of 6 main columns, the link for the listing, the title of the listing, the location of the listing, the price, the property type of the listing (a house, condominium, or apartment), and the offer of the listing (buying or renting). The other columns describes the details and amenities of that particular listing, a sample of this would be the number of bedrooms available, number of bathrooms, floor area, land size, if a maid's room is available, etc. 

It can be noted that a lot of the details and amenities are void depending on the property type. When a property type is a house, it usually would not include amenities that a condominium offers. As such, cleaning of the data gathered is essential as the data was stored only on a single excel file.

### Data Cleaning Process

For the start of the data cleaning process, the notebook *dataCleaning.ipynb* was used.

Once the data has been loaded into the notebook via pandas, the column name was inspected. From the column names, the Floor area was repeated multiple times due to the different special characters used to make ^2. With this, these columns were renamed and the columns were renamed to standard ASCII code which only included english characters.

Afterwards, the string 'void' in the data which was used to indicate that that particular data was empty was replaced with numpy.nan. Afterwards, the duplicate columns of the floor area and land size was inspected.

From the inspection, it appeared that the values in the duplicate columns coincided with the original column where-in if the original floor area and land size has an empty row, one of the duplicate rows would have the data for it. Thus, these columns were then concatenated into a single column and the duplicate columns were removed.

Afterwards, data conversion was done with the data of land size and floor area. Commas were removed and any special characters were removed so that the value could be converted into an integer.

Other columns were also cleaned, where the commas and special characters were removed so that the column could be properly converted into a integer or float. The column *Available from* was converted into a datetime format, Build (Year) into an integer format.

Location was the one next cleaned in the process. The location string would sometimes have whitespace that separates the location inputted by the client and the location put by the website. With this, as the data inputted by the client is not consistent, it was removed from the dataset and only the location inputted by the website was kept. A column named *Unnamed: 136* was also removed as when investigated, it appears that it only showed an empty amenity in the listing. 

With this, initial cleaning has been completed, the dataset was then split into three categories depending on their property type: house, apartment, and condominium.

The unique values per column was checked to see if the nan values could be replaced with another default values. Looking into it, it appears that the nan values in most of the columns could be changed to a default value of 0 as the nan usually entailed that the amenity or detail was not available for the listing.

Afterwards, the number of empty rows per column was taken for each of the property, and if the column had more than 50% missing data for the property, that particular column was removed. And if the number of missing data is less than 10%, the rows with the missing data were removed instead.

The datasets were all then saved into their own separate csv files.
