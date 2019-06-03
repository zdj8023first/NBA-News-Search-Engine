# _*_ coding: utf-8 _*_
# __author__ = zdj
# __date__ = 2019/5/23
# __time__ = 下午2:55
# __ide__ = PyCharms

from scrapy.cmdline import execute

import os
import sys
# import redis
#
# redis_cli = redis.StrictRedis()
# redis_cli.set("")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute(['scrapy', 'crawl', 'news'])
# execute(['scrapy', 'crawl', 'bbs'])
