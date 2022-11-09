# About

The following github repositories explores the data available at [lamudi](lamudi.com.ph). The website gives available houses, condominiums, apartments, commercial, 
land for sale and for rent in the Philippines. The available data was then scraped, specifically houses, condominiums, and apartments for sale and for rent around the 
Philippines. 

## Methodology

Python was used in order to scrape the website with [BeautifulSoup](https://pypi.org/project/beautifulsoup4/).

### Understanding of the website:

To extract the data from lamudi, the website was first explored to give insight on how the website is structured. 

A total of 148,932 properties were for sale and 45,723 properties were for rent at the time of retrieval (As of November 9, 2022). These properties could be grouped on
their specific location. Locations are grouped as follows: Region, City, Barangay. Furthermore, filters could be added as to search for a more specific listing.
Filters can include but is not limited to the price, number of bedrooms, number of bathrooms, floor area, land size, and available amenities (if any).

When looking through listings, the number of available listings per page is at maximum 30 listings. And the maximum number of pages available to be given by the website 
is 100 pages. Going beyond page 100 gives out an error. As the maximum listings that can be given through particular filters is 3000 listings, 
extractions of the total listings per city is extracted. Afterwards, city listings with more than 3000 listings per rent/sale is further divided into their respective
barangays. If the number of listings is still beyond 3000, the listings in that particular barangay would be subdivided further until listings can go below
3000 listings.

### Preminilary Data Understanding:

In total, there are 74 available regions and a total of 1483 cities. The number of available listings were scraped depending on the property type (Condominium, Apartment, or House) and their offer type (Sale or Rent). These listings were then aggregated to a file named *CityDataExpanded - Aggregated*.

To visualize the data on the aggregated data, it was copied on over to *Initial Summary*. On the sheet *summary* shows the number of regions with no available listing depending on the property type and offer type. The data of the available listings per city was aggregated to their respective regions and the total number of available listings per property type and offer type was obtained. From here, a total of 444 unique filters (region, property type, and offer type was permutated) was obtained. Of these **444** filters, a total of **208** of them had no listings available in them and a total of 11 had more than 2900 listings in them. 2900 was considered as the limit as to account for new listings within the area.

With this, the 208 unique filters would be discarded and would not be used to find available listings and the 11 unique filters with more than 2900 listings would be split further to their respective cities, if the number of available listings is still beyond 2900, it would be further split into each barangay.

On each of the listings, the location of the listing is included with their own description, details which includes various facts about the listing such as the land size, floor area, number of bathrooms and bedrooms, etc. and additional amenities if any. 

With this, a csv file would be created per property and offer type (a total of 6) which would contain the listings
- Title
- Location
- Details
- Amenities

If a property does not have a detail or amenities included, the cell would be left blank.

### Gathering of the Data:

