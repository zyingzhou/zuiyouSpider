#! /usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Author: zhiying
Data: 2018-12-01
URL: www.zhouzying.com
Description: 最右APP数据爬取

"""
import requests
from requests import RequestException
import hashlib
import time
import json


# 获取数据
def get_data(uri, msg):

    sign = messagesdigest(msg)
    url = uri + str(sign)
    headers = {"User-Agent": "okhttp/3.11.0 Zuiyou/4.7.1"}
    byte_data = msg.encode('utf-8')
    try:
        r = requests.post(url, headers=headers, data=byte_data)
        # print(r.json())
        return r.json()

    except RequestException as e:
        print(e)


# 消息摘要算法加密
def messagesdigest(msg):

    # 消息的混淆,在消息后面添加字符串“ZDY0MTBlODcx”
    msgs = msg + 'ZDY0MTBlODcx'

    msg_ls = list(msgs)
    # 混淆后消息的前十个字符
    str_head = msg_ls[0:10]
    # 混淆后消息的后十个字符
    str_foot = msg_ls[len(msg_ls) - 10:len(msg_ls)]
    # 将前十个字符和后十个字符进行交换
    del msg_ls[0:10]
    del msg_ls[len(msg_ls)-10:len(msg_ls)]
    msg_ls = str_foot + msg_ls + str_head
    mixedmsg = ''
    for i in range(len(msg_ls)):
        mixedmsg += str(msg_ls[i])
    # 用于显示首尾是否正常颠倒
    # print(mixedmsg)
    # mixedmsg = 'Y0MTBlODcx"all","auto":1,"tab":"推荐","direction":"homebutton","c_types":[1,3,2,8,7,9,11],"sdk_ver":{"tt":"1.9.6.3","tx":"4.19.574","tt_aid":"5004095","tx_aid":"1107850635"},"ad_wakeup":1,"h_ua":"Mozilla\/5.0 (Linux; Android 7.1.2; MI 5X Build\/N2G47H; wv) AppleWebKit\/537.36 (KHTML, like Gecko) Version\/4.0 Chrome\/67.0.3396.87 Mobile Safari\/537.36","h_av":"4.7.3","h_dt":0,"h_os":25,"h_app":"zuiyou","h_model":"MI 5X","h_did":"866655030396869_02:00:00","h_nt":1,"h_m":116456192,"h_ch":"xiaomi","h_ts":1543834422778,"token":"TfKbNCRqAec6tUN7wn3-JSGqoTcO1QytGiEBG2E1jQvCYBqj-TcCLYxVzUKtxgpDii503","android_id":"57b9b8465c2e440b"}ZD{"filter":'

    # 消息摘要算法加密,得到sign
    # 先将混淆后的信息按utf-8编码成byte
    data = mixedmsg.encode('utf-8')

    digest = hashlib.md5()
    digest.update(data)
    sign = digest.hexdigest()

    # 返回消息摘要算法加密得到的sign值
    return sign


# unix时间戳
def unixtime():
    """

    :return: unix时间戳
    """
    time_string = '{:.3f}'.format(time.time()).replace('.', '')
    return eval(time_string)


# 获取全部弹幕
def danmu(pid, vid):

    def parse_chunked_data(t):
        data = {"pid":pid,"vid":vid,"t":t,"h_av":"4.7.3","h_dt":0,"h_os":25,"h_app":"zuiyou","h_model":"MI 5X","h_did":"866655030396869_02:00:00","h_nt":1,"h_m":116456192,"h_ch":"xiaomi","h_ts":unixtime(),"token":"TeKfNCRqAec6tUN7wn3-JSGqoTTXBsx0YTPoKXva9q6z94jiDk2da1MuSuhRdh-G8Bp3-","android_id":"57b9b8465c2e440b"}
        sign = messagesdigest(str(data))
        # 弹幕地址
        url = 'http://dmapi.izuiyou.com/danmaku/list?sign=' + str(sign)
        headers = {"User-Agent": "okhttp/3.11.0 Zuiyou/4.7.1"}
        try:
            r = requests.post(url, headers=headers, data=json.dumps(data))
            response = r.json()
            if response["ret"] == 1:
                chunked_danmu = response["data"]["list"]
                parser_danmu(chunked_danmu)
                # print('{}\n\n'.format(chunked_danmu))
                print("\n")
                # 判断弹幕是否加载完成的标志,1为未完成,0为完成
                more = response["data"]["more"]
                # 下次弹幕加载的开始时间
                t = response["data"]["t"]
                return more, t
            else:
                print("sign签名出错哦！出错pid={},vid={}\n请稍后重试！".format(pid, vid))

        except RequestException as e:
            print(e)

    t = 0
    more, t, = parse_chunked_data(t)
    while more == 1:
        more, t = parse_chunked_data(t)


# 首页推荐内容解析
def parser(items):

    nums = len(items['data']['list'])
    # 用于提取视频中的pid, vid
    # video = []
    for i in range(nums):
        item = items['data']['list'][i]
        # print("{}\n".format(item))
        # 发布人姓名
        if 'memeber' in item:

            name = item['member']['name']
        else:
            name = ""

        # 内容
        if "content" in item:
            content = item['content']
        else:
            content = ''
        # 内容分享次数
        if "share" in item:

            share = item['share']
        else:
            share = ""
        # 评论次数
        if "comments" in item:

            comments = item['reviews']
        else:
            comments = ""
        # 喜欢的次数
        if "likes" in item:

            likes = item['likes']
        else:
            likes = ""

        # 顶的次数
        if "up" in item:

            up = item['up']
        else:
            up = ""
        # 踩的次数
        if "down" in item:

            down = item['down']
        else:
            down = ""
        show = {"name": name, "content": content, "share": share, "comments": comments, "likes": likes, "up": up,
                "down": down}
        print("第{}条：{}".format(i, show))

        if 'videos' in item:
            # 提取段子中的视频信息
            pid = item["id"]
            # 视频id
            vid = list(item['videos'].keys())[0]

            yield pid, eval(vid)


# 视频弹幕解析
def parser_danmu(danmu_data):
    if danmu_data is not None:
        for i in range(len(danmu_data)):
            item = danmu_data[i]
            # 弹幕的评论者,已经失效
            # user = item["member"]["name"]
            # 用户id
            userid = item["id"]
            # 弹幕内容
            content = item["text"]
            print("{},用户ID{}: {}".format(i, userid, content))


def main():
    # 手机端首页推荐地址
    uri = 'http://api.izuiyou.com/index/recommend?sign='
    msg = '{"filter":"all","auto":0,"tab":"推荐","direction":"up","c_types":[1,3,2,8,7,9,11],"sdk_ver":{"tt":"1.9.6.3","tx":"4.19.574","tt_aid":"5004095","tx_aid":"1107850635"},"ad_wakeup":1,"h_ua":"Mozilla\/5.0 (Linux; Android 7.1.2; MI 5X Build\/N2G47H; wv) AppleWebKit\/537.36 (KHTML, like Gecko) Version\/4.0 Chrome\/67.0.3396.87 Mobile Safari\/537.36","h_av":"4.7.3","h_dt":0,"h_os":25,"h_app":"zuiyou","h_model":"MI 5X","h_did":"866655030396869_02:00:00","h_nt":1,"h_m":116456192,"h_ch":"xiaomi","h_ts":1543834422778,"token":"TfKbNCRqAec6tUN7wn3-JSGqoTcO1QytGiEBG2E1jQvCYBqj-TcCLYxVzUKtxgpDii503","android_id":"57b9b8465c2e440b"}'

    items = get_data(uri, msg)
    for pid, vid in parser(items):
        danmu(pid, vid)


if __name__ == '__main__':
    j = 1
    while True:
        print("第{}次加载的段子\n".format(j))
        main()
        j += 1
        
