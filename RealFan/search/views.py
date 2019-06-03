from django.shortcuts import render
from django.views.generic.base import View
from search.models import NewsType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
import json
from datetime import datetime
import redis

redis_cli = redis.StrictRedis()


client = Elasticsearch(hosts=["127.0.0.1"])


# 首页热门搜索
class IndexView(View):
    def get(self, request):
        topn = redis_cli.zrevrangebyscore("search_set", "+inf", "-inf", start=0, num=5)
        return render(request, "index.html", {"topn": topn})


# 本功能完成, 输入时自动补全,搜索建议
class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s','')
        re_datas = []
        if key_words:
            s = NewsType.search()
            s = s.suggest('my_suggest', key_words, completion={
                "field":"suggest", "fuzzy":{
                    # 模糊搜索中对中文的边际距离应该怎么界定
                    # 以及这个模糊搜索究竟怎么影响结果
                    "prefix_length": 0,
                    "fuzziness": 0
                },
                "size": 10
            })
            # 第一次调试没有结果，没出来my_suggest的值，原因不明
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])
        return HttpResponse(json.dumps(re_datas), content_type="application/json")


# 搜索功能
class SearchView(View):
    def get(self, request):
        key_words = request.GET.get("q", "")

        # redis_cli.zincrby("search_set", key_words)
        # 这里，最新版本的已经变了
        redis_cli.zincrby("search_set", 1 , key_words)

        topn = redis_cli.zrevrangebyscore("search_set", "+inf", "-inf",start=0, num=5)

        page = request.GET.get("p", "0")
        try:
            page = int(page)
        except:
            page = 0

        news_count = redis_cli.get("news_count")
        start_time = datetime.now()
        response = client.search(
            index="nbasearch",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["title", "content"]
                    }
                },
                "from": page*10,
                "size": 10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "title": {},
                        "content": {},
                    }
                }
            }
        )
        end_time = datetime.now()
        last_seconds = (end_time-start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (total_nums%10) > 0:
            page_nums = int(total_nums/10) + 1
        else:
            page_nums = int(total_nums)/10
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                # 这里highlight默认取出来的是数组，转化一下
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]
            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[0:200]
            else:
                hit_dict["content"] = hit["_source"]["content"][0:400]

            hit_dict["create_time"] = hit["_source"]["create_time"]
            hit_dict["source"] = hit["_source"]["source"]
            hit_dict["source_url"] = hit["_source"]["source_url"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]
            hit_list.append(hit_dict)

        return render(request, "result.html", {"all_hits": hit_list,
                                               "key_words": key_words,
                                               "page": page,
                                               "total_nums": total_nums,
                                               "page_nums": page_nums,
                                               "last_seconds": last_seconds,
                                               "news_count": news_count,
                                               "topn": topn
                                               })
