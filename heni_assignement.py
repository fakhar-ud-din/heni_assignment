# %% [markdown]
# 1. Parsing HTML (allow 8 mins)
# Task You will scrape and process simple html page located here candidateEvalData/webpage.html
# 
# Output A dataframe of 1 row and 7 columns where the columns are:
# 
# The name of the artist (Peter Doig)
# The name of the painting (The Architect's Home in the Ravine)
# Price realised in GBP (11 282 500)
# Price realised in USD (6 370 908)
# Estimates in GBP (10 000 000 , 15 000 000)
# Estimate in USD (14 509 999 , 21 764999)
# The url of the image of the painting
# Saledate of the painting (2016-02-11)

# %%
#import modules
from lxml import html
import re
import requests
import pandas as pd
from datetime import datetime

#get html and tree
html_page_link = 'candidateEvalData/webpage.html'
tree = html.parse(html_page_link)


# parse artist name
def artist_name():
    """
        Find the artist name and filter only text using re
        return: list containing name
    """
    raw_name = tree.xpath('//*[@class="lotName"]/text()')[0]
    return re.findall(r'(.*?)\(', raw_name)


#parse painting name
def painting_name():
    """
        Find the painting name
        return: list containing name
    """
    return tree.xpath('//*[@class="itemName"]/i/text()')


#parse price GBP
def gbp_price():
    """
        Find the price in gbp and filter the currency keyword (GBP)
        return: list containing price
    """
    gbp_price_x = '//*[contains(@id, "PriceRealizedPrimary")]/text()'
    raw_gbp_price = tree.xpath(gbp_price_x)[0]
    return re.findall(r'GBP(.*)', raw_gbp_price)


#parse price US
def usd_price():
    """
        Find the price in usd and filter the currency keyword (USD)
        return: list containing price
    """
    usd_price_x = '//*[contains(@id, "PriceRealizedSecondary")]/text()'
    raw_usd_price = tree.xpath(usd_price_x)[0]
    return re.findall(r'USD(.*)', raw_usd_price)


#parse price GBP est
def est_gbp_price():
    """
        Find the est price in gbp and filter the currency keyword (GBP)
        return: list containing price
    """
    gbp_est_price_x = '//*[contains(@id, "PriceEstimatedPrimary")]/text()'
    return [tree.xpath(gbp_est_price_x)[0].replace('GBP', '')]


#parse price US est
def est_usd_price():
    """
        Find the est price in usd and filter the currency keyword (USD)
        return: list containing price
    """
    usd_est_price_x = '//*[contains(@id, "PriceEstimatedSecondary")]/text()'
    raw_est_usd_price = tree.xpath(usd_est_price_x)[0]
    return [' - '.join(re.findall(r'(\d+,\d+,\d+)', raw_est_usd_price))]


#image link
def product_image_url():
    """
        Finds the product iamge
        return: list containing image URL
    """
    return tree.xpath('//*[@id="imgLotImage"]/@src')

#sale date
def art_saledate():
    """
        Find the saleprice and change the format to required pattern
        return: list containing sale date
    """
    sale_date_x = '//*[contains(@id, "SaleDate")]/text()'
    date = tree.xpath(sale_date_x)[0].rstrip(', ')
    return [datetime.strptime(date, "%d %B %Y").strftime("%Y-%m-%d")]


product = {
    'artist_name': artist_name(),
    'painting_name': painting_name(),
    'gbp_price': gbp_price(),
    'usd_price': usd_price(),
    'gbp_est_price': est_gbp_price(),
    'usd_est_price': est_usd_price(),
    'art_image_url': product_image_url(),
    'saledate': art_saledate()
}

art_df = pd.DataFrame(product)

# %% [markdown]
# 2. Regex (allow 12 mins)
# For each example below, write a regex to process the string in rawDim to extract the height, width and the depth (as float64 integers).
# 
# Bonus: Is there a single regex for all 5 examples ?

# %%
import pandas as pd
dim_df = pd.read_csv("candidateEvalData/dim_df_correct.csv")
dim_df

# %%
########### reg expressions
# loading modules
import re
import pandas as pd

"""
    Regex matching only particular row
"""
regexes = {
    0: r'(.*?)cm',
    1: r'(.*?)cm',
    2: r'(.*?)cm',
    3: r'Image.*?\((.*?)cm',
    4: r'(.*?)in'
}
"""
    Bonus Regex
"""
bonus_regex = r"((?<![\/])(?:\d+(?:[.,]\d+)?(?:\s|x|×|by)*)+?)(?=cm|in)"
dims = []

for row in range(len(dim_df)):
    # Following commented line uses particular regex
    # raw_dims = re.findall(regexes[row], dim_df['rawDim'][row])[0]
    raw_dims = re.findall(bonus_regex, dim_df['rawDim'][row])[0]
    raw_dims = raw_dims.replace(',', '.').replace(' ', '')
    
    filtered_dims = re.split('×|x|by', raw_dims)
    converted_dims = [pd.to_numeric(dim) * 2.54 if 'by' in raw_dims else dim for dim in filtered_dims]
    
    columns = ['height', 'width'] if len(converted_dims) < 3 else ['height', 'width', 'depth']   
    dim_df.loc[row, columns] = converted_dims

dim_df['height'] = dim_df['height'].astype('float')
dim_df['width'] = dim_df['width'].astype('float')
dim_df['depth'] = dim_df['depth'].astype('float')

dim_df

# %% [markdown]
# 4. Data (allow 5 mins)
# There is a nycflights13 database with the following tables:
# 
# flights connects to planes via a single variable, tailnum.
# flights connects to airlines through the carrier variable.
# flights connects to airports in two ways: via the origin and dest variables.
# flights connects to weather via origin (the location), and year, month, day, and hour (the time).
# Joins
# Task 1 : Describe inner join, left join, right join, full join.
# 
# Task 2 : Write the SQL to do the following:
# 
# Add full airline name to the flights dataframe and show the arr_time, origin, dest and the name of the airline.
# 
# Filter resulting data.frame to include only flights containing the word JetBlue
# 
# Summarise the total number of flights by origin in ascending.
# 
# Filter resulting data.frame to return only origins with more than 100 flights.
# 
# Your final dataframe would look like this
# 
# origin	numFlights
# JFK	148
# Output: SQL query (no need to execute)
# 
# See data below

# %% [markdown]
# Task1: Describe inner join, left join, right join, full join.
# The “join” keyword is used to combine multiple tables based on some key mapping, i.e primary_key = foreign_key
# Considering we have table A and table B, and we join tableB to tableA, we will have 4 joins which can be used as follows,
# Inner Join:
# 		This join combines all the “common rows” from both of the tables, excluding all nulls. Every row matched against tableA.a_id = tableB.a_id in table A and table B will appear in the final result including all or specified columns of table B.
# Left Join:
# 		This join will list every row from tableA, and skip any rows that exist only in tableB. This will show any nulls in tableB if there are any.
# Right Join:
# 		This join will list every row from tableB, and skip any rows that exist only in tableA. This will show any nulls in tableB if there are any.
# Full Join:
# 		Full join is also known as full outer join, which could help explaining it more clearly. This particular join lists every row from both tables. This might result in some nulls in the final result where either table columns would be filled with values, and nulls for the other table columns.
# 

# %% [markdown]
# Task2:
# 
# 1:
# 	SELECT arr_time, origin, dest, ai.name
# 	FROM flights AS f
# 	INNER JOIN airlines AS ai 
# 	ON ai.carrier = f.carrier
# 
# 2:
# 	SELECT arr_time, origin, dest, ai.name
# 	FROM flights AS f
# 	INNER JOIN airlines AS ai 
# 	ON ai.carrier = f.carrier
# 	WHERE ai.name LIKE ‘JetBlue%’
# 
# 3:
# 	SELECT f.origin, COUNT(*) AS “numFlights”
# 	FROM flights AS f
# 	INNER JOIN airlines AS ai 
# 	ON ai.carrier = f.carrier
# 	WHERE ai.name LIKE ‘JetBlue%’
# 	GROUP BY f.origin
# 	ORDER BY f.origin
# 
# 4:
# 	SELECT f.origin, COUNT(*) AS “numFlights”
# 	FROM flights AS f
# 	INNER JOIN airlines AS ai 
# 	ON ai.carrier = f.carrier
# 	WHERE ai.name LIKE ‘JetBlue%’
# 	GROUP BY f.origin
# 	HAVING COUNT(*) > 100
# 	ORDER BY f.origin
# 


