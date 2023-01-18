from scrapy.spiders import CrawlSpider, Spider
import pandas as pd

from bearspace_project.items import BearspaceProjectItem


class ArtworksDataframe(object):
    def close_spider(self, spider):
        if isinstance(spider, CrawlSpider):
            artworks = spider.bearspace_parser.artworks
        elif isinstance(spider, Spider): # Executes only when parser is run on a single URL
            artworks = spider.artworks
        
        artworks_df = pd.DataFrame(artworks, columns=['url', 'name', 'media', 'height', 'width', 'price'])
        print(artworks_df)
        
        return artworks_df
