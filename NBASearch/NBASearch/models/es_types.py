# _*_ coding: utf-8 _*_
# __author__ = zdj
# __date__ = 2019/5/23
# __time__ = 下午7:01
# __ide__ = PyCharm

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, Completion, Keyword, Text

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


# 新闻在elastic中的type
class NewsType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    url = Keyword()
    title = Text(analyzer="ik_max_word")
    create_time = Keyword()
    source = Keyword()
    source_url = Keyword()
    content = Text(analyzer="ik_max_word")

    class Meta:
        index = "nbasearch"
        doc_type = "news"


if __name__ == "__main__":
    # 用来在elasticsearch中生成type
    NewsType.init()
