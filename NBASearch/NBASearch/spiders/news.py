# -*- coding: utf-8 -*-
# __author__ = zdj
# __date__ = 2019/5/23
# __time__ = 下午2:55
# __ide__ = PyCharms

import scrapy
from scrapy.http import Request
from urllib import parse
from NBASearch.items import NewsItem, NewsItemLoader
from NBASearch.utils.commons import get_md5


class NewsSpider(scrapy.Spider):
    name = 'news'
    # 这里必须是网站的域名, 在这找个几个小时的错误, shit！以后有问题直接去Google，不要瞎想
    allowed_domains = ['voice.hupu.com']
    start_urls = ['https://voice.hupu.com/nba/2427207.html']

    def parse_detail(self, response):

        """
        1. 获取文章页的第一条新闻的url
        2. 然后把它交给自定义的parse_detail 函数进行解析
        :param response:
        :return:
        """
        first_url = response.css("h4:only-child a::attr(href)").extract_first()

        yield Request(url=parse.urljoin(response.url, first_url), callback=self.parse_detail)

    # 这样每次开始前总会做重复的工作，有没有什么方法

    def parse(self, response):
        """
        1. 这里用来处理每一条具体新闻页面
        2. 并且获取下一页的url，然后继续解析下一页
        :param response:
        :return:
        """
        # # # 通过css选择器获取内容
        # url = response.url
        # title = response.css(".headline::text").extract_first()
        # create_time = response.css("#pubtime_baidu::text").extract_first()
        # source = response.css("#source_baidu a::text").extract_first()
        # source_url = response.css("#source_baidu a::attr(href)").extract_first()
        # content = response.css(".artical-main-content").extract_first()
        #
        # # 获取下一页的url,并去掉 #next
        next_url = response.css(".btn-next::attr(href)").extract_first()[:-5]

        # 对news进行赋值
        news_item = NewsItem()
        item_loader = NewsItemLoader(item=NewsItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_md5", get_md5(response.url))
        item_loader.add_css("title", ".headline::text")
        item_loader.add_css("create_time", "#pubtime_baidu::text")
        item_loader.add_css("source", "#source_baidu a::text")
        item_loader.add_css("source_url", "#source_baidu a::attr(href)")
        item_loader.add_css("content", ".artical-main-content")

        news_item = item_loader.load_item()

        yield news_item
        if next_url:
            yield Request(url=next_url, callback=self.parse)




