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
