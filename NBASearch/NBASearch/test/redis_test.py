# _*_ coding: utf-8 _*_
# __author__ = zdj
# __date__ = 2019/5/24
# __time__ = 下午2:50
# __ide__ = PyCharm
import redis

redis_cli = redis.StrictRedis()
redis_cli.incr("news_count")
