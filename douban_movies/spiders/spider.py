import scrapy
from urllib.parse import urlencode
import re
import json
from douban_movies.items import DoubanMoviesItem
import time

class MovieSpider(scrapy.Spider):

    name = 'douban_movies'

    def __init__(self):
        # self.cats = []
        self.cate_ajax_url='https://movie.douban.com/j/search_tags?type=movie&source='
        self.base_ajax_url = 'https://movie.douban.com/j/search_subjects?type=movie&'

    def start_requests(self):
        yield scrapy.Request(self.cate_ajax_url,callback=self.get_category)

    def get_category(self,response):
        jsonresponse = json.loads(response.body_as_unicode())
        cats = jsonresponse['tags']
        for cat in cats:
            page=0
            while page<=500:
                dict = {
                    'tag':cat,
                    'sort':'time',
                    'page_limit':20,
                    'page_start':page
                }
                page += 20
                url = self.base_ajax_url+urlencode(dict)
                yield scrapy.Request(url,callback=self.parse_json,meta=dict)


    def parse_json(self,response):
        jsonresponse = json.loads(response.body_as_unicode())
        contents = jsonresponse['subjects']
        print(response.url)
        print('正在爬取{}类型下的第{}页'.format(response.meta['tag'],(response.meta['page_start']/20)+1))
        if len(contents)>0:
            for content in contents:
                data = {
                    'title':content['title'],
                    'url' : content['url']
                }
                time.sleep(5)
                yield scrapy.Request(data['url'],callback=self.parse,meta=data)

    def parse(self, response):
        item = DoubanMoviesItem()
        item['movie_name'] = response.meta['title']
        item['url'] = response.url
        info = response.css('#info')
        try:
            item['director'] = info.css('[rel="v:directedBy"]::text').extract_first()
        except:
            item['director'] = None
        item['actors'] = info.css('.actor [rel="v:starring"]::text').extract()
        item['genre'] = info.css('[property="v:genre"]::text').extract()
        item['language'] = re.search(r'语言:\<\/span\>(.*)\<br\>',info.extract_first()).group(1)
        item['country'] = re.search(r'地区:\<\/span\>(.*)\<br\>',info.extract_first()).group(1)
        item['runtime'] = info.css('[property="v:runtime"]::text').extract_first()
        item['release_time'] = info.css('[property="v:initialReleaseDate"]::text').extract_first()
        rate_info = response.css('#interest_sectl')
        item['rate'] = rate_info.css('[property="v:average"]::text').extract_first()
        item['rate_people'] = rate_info.css('[property="v:votes"]::text').extract_first()
        yield item