# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanMoviesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    movie_name = scrapy.Field()
    url = scrapy.Field()
    director = scrapy.Field()
    actors = scrapy.Field()
    genre = scrapy.Field()
    country = scrapy.Field()
    language = scrapy.Field()
    release_time = scrapy.Field()
    runtime = scrapy.Field()
    rate = scrapy.Field()
    rate_people = scrapy.Field()
