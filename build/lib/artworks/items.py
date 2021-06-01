# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArtworksItem(scrapy.Item):
    # define the fields for your item here
    url = scrapy.Field()
    artist = scrapy.Field()
    title = scrapy.Field()
    image = scrapy.Field()
    height = scrapy.Field()
    width = scrapy.Field()
    description = scrapy.Field()
    categories = scrapy.Field()
