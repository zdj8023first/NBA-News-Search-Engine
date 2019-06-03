# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from NBASearch.models.es_types import NewsType
from w3lib.html import remove_tags
import redis
from elasticsearch_dsl.connections import connections

redis_cli = redis.StrictRedis()
es = connections.create_connection(NewsType._doc_type.using)


class NbasearchItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 定义自己itemloader,主要是为了设置默认的输出处理函数
class NewsItemLoader(ItemLoader):
    # 设置默认的输出处理函数
    default_output_processor = TakeFirst()


# 定义自己itemloader,主要是为了设置默认的输出处理函数
class BBSItemLoader(ItemLoader):
    # 设置默认的输出处理函数
    default_output_processor = TakeFirst()


# 去除title前后的空字符
def strip_str(value):
    return value.strip()


def gen_suggests(index, info_tuple):
    # 根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            # 这里去掉了单个字符的建议，我们认为单个的是没有什么意义的
            # 经过后台查看，这里产生的词效果不算很好，比如哈登就分析不出来是哈登，应该是版本比较老了
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            used_words = used_words.union(new_words)
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests


# 定义自己新闻类
class NewsItem(scrapy.Item):
    url = scrapy.Field()
    # 增加一个md5的值，用来当做id，这样可以去重
    url_md5 = scrapy.Field()
    title = scrapy.Field(
        input_processor=MapCompose(strip_str)
    )
    create_time = scrapy.Field()
    source = scrapy.Field()
    source_url = scrapy.Field()
    # 这里不用做去前后空的处理，因为是<div></div>
    content = scrapy.Field()

    def save_to_es(self):
        news = NewsType()
        news.url = self['url']
        news.meta.id = self['url_md5']
        news.title = self['title']
        news.create_time = self['create_time']
        news.source = self['source']
        news.source_url = self['source_url']
        # 这个函数功能有点小爽
        news.content = remove_tags(self['content'])

        news.suggest = gen_suggests(NewsType._doc_type.index, ((news.title, 10),))

        news.save()

        redis_cli.incr("news_count")
        return


class BBSItem(scrapy.Item):
    url = scrapy.Field()
    url_md5 = scrapy.Field()
    title = scrapy.Field()
    reply_nums = scrapy.Field()
    view_nums = scrapy.Field()
    like_nums = scrapy.Field()
    post_time = scrapy.Field()
    content = scrapy.Field()
    recommend_nums = scrapy.Field()