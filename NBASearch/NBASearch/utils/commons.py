# _*_ coding: utf-8 _*_
# __author__ = zdj
# __date__ = 2019/5/23
# __time__ = 下午8:43
# __ide__ = PyCharm

import hashlib



def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


# 解析bbs中的回复数和浏览数
def get_statics(statics):
    statics = statics.replace("\xa0", "").split("/")
    statics = list(map(int, statics))
    return statics


if __name__ == "__main__":
    print (get_md5("https://voice.hupu.com/nba/2434968.html".encode("utf-8")))
    int_statics = get_statics("5\xa0/\xa0264544")

    print("this is the common function file")
