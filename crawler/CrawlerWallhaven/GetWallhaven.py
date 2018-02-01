# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import threading
import time
import os
        
def Get_WallHaven(getUrl, dsctUrl, num):
    global gimagelist
    global gCondition
    for i in range(22, num):
        print(i)
        url = getUrl+str(i)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        content = requests.get(url, headers=headers, stream=True)
        # 获取a标签链接
        soup = BeautifulSoup(content.text, 'html.parser').findAll('img', class_='lazyload')
        for img in soup:
            imgUrl = 'https://alpha.wallhaven.cc/wallpapers/full/wallhaven-' + img['data-src'][-10:]
            imgInfo = requests.get(imgUrl, headers=headers, stream=True)
            if imgInfo.status_code == 200:
                gimagelist.append(imgUrl)  # 添加下载图片URL列表
                # path = dsctUrl+img['data-src'][-10:]  # 拼接文件名
                # open(path, 'wb').write(imgInfo.content)  # 保存图片
                

def download_pic(url):
    path = '/Users/yemingming/Desktop/Crawler/CrawlerWallhaven/wallhaven/'+url[-10:]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    mgInfo = requests.get(url, headers=headers, stream=True)
    open(path, 'wb').write(mgInfo.content)
    print('图片下载完成：%s ' % path[-10:], time.strftime("%Y-%m-%d %H:%M:%S"))    # chunk_size = 1024  # 单次请求最大值
    
class Producer(threading.Thread):
    def run(self):
        print('%s started' % threading.current_thread())
        global gimagelist
        global gCondition
        for j in range(1):  # 我默认循环一次，你也可以改很多
            searchurl = ''
            if searchurl not in visited:  # 如果没有访问过
                gCondition.acquire()  # 上锁
                gCondition.notify_all()  # 唤醒所有等待的消费者
                gCondition.release()  # 释放锁
                visited.add(searchurl)  # 标记为已访问过


class Consumer(threading.Thread):
    def run(self):
        print('%s started' % threading.current_thread())
        while True:
            global gimagelist
            global gCondition
            gCondition.acquire()  # 上锁
            while len(gimagelist)==0:
                gCondition.wait()  # 有则等待
            url=gimagelist.pop()
            gCondition.release()
            download_pic(url)  # 下载图片
            
                
if __name__ == '__main__':
    # 图片的url
    gimagelist = []
    # 用来存放已经搜过的页面的url
    visited = set()
    # 线程相关
    gCondition = threading.Condition()
    # 爬取网站地址
    getUrl = 'https://alpha.wallhaven.cc/random?page='  # random随机，toplist按排名
    # 文件存放地址
    dsctUrl = '/Users/yemingming/Desktop/Crawler/CrawlerWallhaven/wallhaven/'
    # 页数
    num =25
    Get_WallHaven(getUrl, dsctUrl, num)
    Producer().start()
    for i in range(10):  # 十个消费者线程数
        Consumer().start()