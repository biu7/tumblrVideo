import os

import requests
from lxml import etree
import json
import re
import threading
import datetime

proxies = {
    'http': 'http://localhost:1080',
    'https': 'http://localhost:1080',
}



basedir = os.path.abspath(os.path.dirname(__name__))
baseurl = 'https://vtt.tumblr.com/%s.mp4'

def Handler(start,end,url,filename):

    headers = {
        'Range':'bytes=%d-%d' % (start,end),
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',

    }
    print(url)
    session = requests.Session()

    r = requests.get(url,headers=headers,proxies=proxies,stream=True)
    print(r.headers)
    with open(filename,'r+b') as fp:
        fp.seek(start)
        var = fp.tell()
        fp.write(r.content)


def downloadfile(url,num_thread=1):
    print(url)
    response_head = requests.head(url,proxies=proxies)

    filename = url.split('/')[-1]
    try:
        filesize = int(response_head.headers['content-length'])
    except KeyError:
        return

    fp = open(filename,'wb')
    fp.truncate(filesize)
    fp.close()

    part = filesize // num_thread
    for i in range(num_thread):
        start = part * i
        if i == num_thread-1:
            end = filesize
        else:
            end = start + part

        t = threading.Thread(target=Handler,kwargs={'start':start,'end':end,'url':url,'filename':filename})
        t.setDaemon(True)
        t.start()

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()
    print('%s 下载完成' % filename)


def save(urls):
    for url in urls:
        splits = url.split('/')
        try:
            int(splits[-1])
            filename = splits[-2]
        except ValueError:
            filename = splits[-1]
        finally:
            print('正在下载视频%s' % filename)
            video = requests.get(url,proxies=proxies,stream=True)
            filepath = os.path.join(basedir,filename)
            with open(filepath,'wb') as f:
                for v in video.iter_content(chunk_size=512):
                    if v:
                        f.write(v)
            print('%s 下载完成') % filename


def parse(response):
    urls = []
    posts = json.loads(response[22:-2])['posts']
    for i in range(len(posts)):
        if posts[i]['type'] == 'video':
            content = posts[i]['video-player-500']
            src = re.findall('src="(.*?)"', content)[0]
            path = src.split('/')
            try:
                int(path[-1])
                url = baseurl % (path[-2] + '_' + path[-1])
            except ValueError:
                url = baseurl % path[-1]
            finally:
                urls.append(url)
    return urls

def make_response(url):

    response = requests.get(url,proxies=proxies);
    return response.text



if __name__ == '__main__':
    list = ['nicesujingege', 'liesanglun', 'fuckopfff', '752574823', 'maydaylxy', 'perfectcollectorcycle', 'jsmchuren21', 'ilovefate', 'yangyaojing', 'starmmmmm', 'mdzz-pipixia', 'teammix-9527', '377346055', 'tiantai1', 'hinbsksksbjdjd', '78878878787', 'missyourselfagain', '880066', 'kkkrrrjjj', 'bluekitteh0', 'zzaini123', 'passeryu', 'realys', 'mygfanspagehk', 'hot-sexy-fit-girls-blog']
    for name in list:

        # name = input('输入博客名')
        url = 'http://%s.tumblr.com/api/read/json?start=0&num=500' % name
        response = make_response(url)
        urls = parse(response)
        print(urls)
        for url in urls:
            downloadfile(url)
    # save(urls)