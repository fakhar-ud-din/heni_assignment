import scrapy


class BearspaceProjectItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    height = scrapy.Field()
    width = scrapy.Field()
    price = scrapy.Field()
    media = scrapy.Field()