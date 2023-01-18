import re

from scrapy.spiders import CrawlSpider, Spider, Rule
from scrapy.linkextractors import LinkExtractor

from bearspace_project.items import BearspaceProjectItem


def clean(list_or_str):
    if isinstance(list_or_str, list):
        return [clean(item) for item in list_or_str]
    
    return list_or_str.strip().replace('\xa0', ' ')


class BearspaceParser(Spider):
    name = 'bearspace-parse'
    
    # Holds all availalble artworks, 
    # Later used in pipelines to return a dataframe
    artworks = []
    
    # Description keywords to filter out the relevant media
    description_keywords = [
        'spray', 'canvas', 'board', 'paint', 
        'oil', 'enamel', 'pigements', 'pigment', 'resin',
        'acrylic', 'print', 'digital', 'sculpture', 'art'      
    ]
    
    def parse(self, response, *args, **kwargs):
        """
            Process an artwork's page, if it is available for purchase (in stock),
            We scrape other details and save in artworks
            
            returns: scrapy item
        """
        if not self.in_stock(response):
            self.logger.info(f"Out of Stock product Dropped!\nURL: {response.url}")
            return
        
        item = BearspaceProjectItem()
        
        item['url'] = self.product_url(response)
        item['name'] = self.product_name(response)
        item['media'] = self.product_media(response)
        item['price'] = self.product_price(response)
        
        self.product_dimensions(item, response)
        
        self.artworks.append([
            item['url'], item['name'], item['media'], 
            item['height'], item['width'], item['price']
        ])
        
        return item
    
    def in_stock(self, response):
        """
            Checks stock status/ availability of the item
            returns: boolean
        """
        cart_btn = response.css('[data-hook="add-to-cart"] ::text').get()
        return cart_btn.lower() == 'add to cart'

    def product_url(self, response):
        """
            URL of the artwork page
            returns: string url
        """
        return response.url
    
    def product_name(self, response):
        """
            Extracts and filter any characters/ spaces from the name
            returns: string name
        """
        return clean(response.css('[data-hook=product-title] ::text').get())
    
    def product_media(self, response):
        """
            Extracts description based on the defined keywords
            returns: string description
        """
        raw_description = response.css('[data-hook="description"] ::text').getall()
        product_descriptions = [
            desc for desc in raw_description 
            if any(kw in desc.lower() for kw in self.description_keywords)
        ]
        
        return " ".join(clean(product_descriptions))
    
    def product_dimensions(self, item, response):
        """
            Finds and filters the dimesions from the description,
            Assign same value to height and width, in case of a circle
            
            returns: None
        """
        dimension_re = r'((?:(?<=x)|(?<=x\s))\d+(?:[.,]\d+)?|\d+(?:[.,]\d+)?(?=x|\sx|w|h|d|cm))'
        raw_dimension= " ".join(response.css('[data-hook=description] ::text').getall()).lower()
        dimensions = re.findall(dimension_re, raw_dimension)
        
        if len(dimensions) < 2:
            dimensions.append(dimensions[0]) 
            
        item['height'] = dimensions[1]
        item['width'] = dimensions[0]
    
    def product_price(self, response):
        """
            Finds the price of the art and filters the currency symbol
            returns: string price
        """
        raw_price = response.css('[data-hook=formatted-primary-price]::text').get()
        return raw_price.replace('£', '')


class BearspaceCrawler(CrawlSpider):
    name = 'bearspace-crawl'
    start_urls = ['https://www.bearspace.co.uk/purchase']
    allowed_domains = ['bearspace.co.uk']
    
    custom_settings = {
        # Adding delay to slightly slow down the crawling speed, 
        # to avoid any minor blocking
        'DOWNLOAD_DELAY': 0.5
    }
    
    bearspace_parser = BearspaceParser()
    
    listings_css = ['[data-hook=product-list-pagination-link-seo-link]']
    products_css = ['[data-hook=product-list-grid-item]']
    
    rules = (
        Rule(LinkExtractor(restrict_css=listings_css)),
        Rule(LinkExtractor(restrict_css=products_css), callback='parse_item'),
    )
    
    def parse_item(self, response, *args, **kwargs):
        """
            This method calls the parse of Parse Class, which return a scraped item
            return: scrapy item
        """
        yield self.bearspace_parser.parse(response, args, kwargs)
