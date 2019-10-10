import scrapy
from urllib.parse import urlencode
import re
import json
from douban_movies.items import DoubanMoviesItem
import time

class MovieSpider(scrapy.Spider):
    #爬虫名字，运行这个程序需要cd到程序文件目录下，输入scrapy crawl douban_movies
    name = 'douban_movies'

    def __init__(self):
        # self.cats = []
        #这个url是tags的ajax页面链接
        self.cate_ajax_url='https://movie.douban.com/j/search_tags?type=movie&source='
        #这个是基础ajax链接，通过增加后续的dict参数来补充成完整的url
        self.base_ajax_url = 'https://movie.douban.com/j/search_subjects?type=movie&'

    #首先访问标签页的网页
    def start_requests(self):
        #修改callback参数，将结果返回给get_category函数去进一步加工url
        yield scrapy.Request(self.cate_ajax_url,callback=self.get_category)

    def get_category(self,response):
        #将网页中的json文件取出
        jsonresponse = json.loads(response.body_as_unicode())
        cats = jsonresponse['tags']
        #遍历所有标签
        for cat in cats:
            page=0
            #25页
            while page<=500:
                dict = {
                    'tag':cat,
                    'sort':'time',#原本是有按热度、时间、评价排序可以选择的，选择一样就行
                    'page_limit':20,
                    'page_start':page
                }
                page += 20
                #利用urlencode库将dict包装成url形式
                url = self.base_ajax_url+urlencode(dict)
                #将结果返回给parse_json函数进一步处理，并将dict参数也一并传过去需要用
                yield scrapy.Request(url,callback=self.parse_json,meta=dict)

"""
上一个url返回的是json格式数据，所以下一步仍然是解析json文件
其中一个电影的数据结构如下：
0: {cover: "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2568737620.jpg",
    cover_x: 2766,
    cover_y: 4096,
    id: "26419635",
    is_new: true,
    playable: false,
    rate: "6.3",
    title: "高草丛中",
    url: "https://movie.douban.com/subject/26419635/"}

"""
    def parse_json(self,response):
        jsonresponse = json.loads(response.body_as_unicode())
        #保存在subjects下
        contents = jsonresponse['subjects']
##        print(response.url)
        print('正在爬取{}类型下的第{}页'.format(response.meta['tag'],(response.meta['page_start']/20)+1))
        #页面是否有内容，有则取出电影名和链接
        if len(contents)>0:
            for content in contents:
                data = {
                    'title':content['title'],
                    'url' : content['url']
                }
##                time.sleep(5)
                #接下来就是访问电影页面，并response交给parse解析，同时还是将data一同传下去
                yield scrapy.Request(data['url'],callback=self.parse,meta=data)

    #解析网页，并将所需信息保存至item
    def parse(self, response):
        #新建item类
        item = DoubanMoviesItem()
        #电影名字
        item['movie_name'] = response.meta['title']
        #url
        item['url'] = response.url
        #解析网页用的是scrapy自带的css选择器去解析
        info = response.css('#info')
        #导演
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
        #最后yield item就行了
        yield item
