# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from NBASearch.utils.commons import get_statics, get_md5
from NBASearch.items import BBSItemLoader


class BbsSpider(scrapy.Spider):
    name = 'bbs'
    allowed_domains = ['bbs.hupu.com']
    start_urls = ['https://bbs.hupu.com/nba']

    def parse(self, response):
        """
        1. 从首页中获取首页中所有帖子的node
        2. 遍历所有node进行爬去
        3. 构造下一页的url
        4. 重复这一过程
        :param response:
        :return:
        """
        page_num =1 # 默认从第一页开始
        # 获取下一页并处理
        page_num = page_num + 1
        next_page = response.url + '-' + str(page_num)

        # bbs_urls = response.css(".truetit::attr(href)") # 这里得到的是相对路径
        # for url in bbs_urls:
        #     # url = parse.urljoin(response.url, url.extract())
        #     yield Request(url=parse.urljoin(response.url, url.extract()), callback=self.parse_detail)

        bbs_nodes = response.css(".for-list li")
        for node in bbs_nodes:
            statics = node.css(".ansour::text").extract_first("")
            url = node.css(".truetit::attr(href)").extract_first("")

            yield Request(url=parse.urljoin(response.url, url),
                          meta={"statics": statics},
                          callback=self.parse_detail)

        yield Request(url=parse.urljoin(response.url, next_page), callback=self.parse)

        pass

    def parse_detail(self, response):
        url = response.url
        title = response.css("h1::text").extract_first()
        statics = response.meta.get("statics","")
        statics = get_statics(statics)
        if statics:
            reply_nums = statics[0]
            view_nums = statics[1]
        else:
            reply_nums = view_nums = 0

        like_nums = response.css(".browse span:nth-child(2)::text").extract_first()
        post_time = response.css(".post-owner + span::text").extract_first()
        content = response.css(".quote-content").extract_first()
        recommend_nums = response.css("#Recers a::text").extract_first()

        pass
