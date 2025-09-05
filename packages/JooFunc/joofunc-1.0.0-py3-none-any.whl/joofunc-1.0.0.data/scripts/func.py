
import os,re,math,urllib3,requests,faker,shutil,re
import sys,time
from urllib.parse import unquote
if sys.version_info[:2] >= (3, 0):
    from urllib.request import build_opener
else:
    from urllib2 import build_opener

from concurrent.futures import ThreadPoolExecutor
import math
import time
import requests
import os
import re
from faker import Faker
from typing_extensions import Self

requestOBJ = build_opener()
requestOBJ.addheaders = [("User-Agent", faker.Faker().user_agent())]

from bidi.algorithm import get_display
from arabic_reshaper import reshape

from JooFunc.errors import (
    UrlNotFoundError,InternetConnectionError,
    InternetTimeOut,CheckFromUrlConnection
)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

total_sent_length = 0
total_recv_length = 0
total_length = 0

def rlen(response):
    len_of_meth = len(response.request.method)
    len_of_addr = len(response.request.url)
    len_of_head = len('\r\n'.join('{}{}'.format(k, v) for k, v in response.request.headers.items()))
    len_of_body = len(response.request.body if response.request.body else [])

    return len_of_meth + len_of_addr + len_of_head + len_of_body

def header_size(headers):
    return sum(len(key) + len(value) + 4 for key, value in headers.items()) + 2
def calcTotalSize(r):
    request_line_size = len(r.request.method) + len(r.request.path_url) + 12
    request_size = request_line_size + header_size(r.request.headers) + int(r.request.headers.get('content-length', 0))
    response_line_size = len(r.response.reason) + 15
    response_size = response_line_size + header_size(r.headers) + int(r.headers.get('content-length', 0))
    return request_size + response_size
def req(**reqParams:dict) -> dict | str | bytes | object:
    global total_sent_length
    global total_recv_length
    global total_length
    url = reqParams['url']
    method = 'get' if not 'method' in reqParams else reqParams['method']
    output = '' if not 'out' in reqParams else reqParams['out']
    session = requests if not 'ses' in reqParams else reqParams['ses']
    headers = {'User-Agent':getUserAgent()} if not 'h' in reqParams else reqParams['h']
    cookies = '' if not 'c' in reqParams else reqParams['c']
    redircet = False if not 'redirect' in reqParams else reqParams['redirect']
    try:
        if method=='get':
            req = session.get(
                url=url,
                headers=headers,
                allow_redirects=redircet,
                cookies=cookies,
                timeout=30
            )
            
        elif method=='post': 
            req = session.post(
                url=url,
                headers=headers,
                allow_redirects=redircet,
                cookies=cookies,
                timeout=30
            )
        elif method=='head': 
            req = session.head(
                url=url,
                headers=headers,
                allow_redirects=redircet,
                cookies=cookies,
                timeout=30
            )
    except requests.exceptions.ConnectionError: raise InternetConnectionError(url)
    except requests.exceptions.ConnectTimeout: raise InternetTimeOut(url)
    except requests.exceptions.ReadTimeout: raise InternetTimeOut(url)
    except requests.exceptions.InvalidURL: raise CheckFromUrlConnection(url)
    except: raise
    req.raise_for_status()
    
    total_sent_length += rlen(req)
    total_recv_length += len(req.content)
    # total_length+= calcTotalSize(req)
    if output=='json': return req.json()
    elif output=='text': return req.text
    elif output=='binary': return req.content
    elif output=='headers': return req.headers
    else: return req

def getTotalBytesConnection():
    return {
        'upload':total_sent_length,
        'download':total_recv_length,
        'total':total_length
    }

def getUserAgent(): return faker.Faker().user_agent()
def SearchReg(string,data): return re.search(string,data).group(1)


def arabic_print(text): return get_display(reshape(text))  

def get_filesize(url: str,session=requests,headers={}) -> int:
    try:
        return int(requestOBJ.open(url).headers["Content-Length"])
    except:
        try:
            return int(session.head(url, stream=True).headers['Content-Length'])
        except:
            try: return int(session.get(url, stream=True).headers['Content-Length'])
            except: return 0

def get_filename_url(url:str,response_Headers:dict) -> str:
    try:
        filename = remove_char(re.findall(
            "filename=\"(.+)\";", response_Headers['Content-Disposition'])[0])
    except:
        filename = url.split('/')[-1]
    return filename

def convertSeconds(sec): return time.strftime('%H:%M:%S', time.gmtime(sec))
def get_regex(pattern,search_str,element=0) -> str | list | None:
    if element==0:
        try: return re.findall(pattern,search_str)[0]
        except: return None
    return re.findall(pattern,search_str)

def search_regex(pattern:str,search_str:str,group=1) -> str | None:
    try: return re.search(pattern,search_str).group(group)
    except: return None
def convert_size1(size_bYT):
    if size_bYT == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bYT, 1024)))
    p = math.pow(1024, i)
    s = round(size_bYT / p, 2)
    return "%s %s" % (s, size_name[i])

def convert_size(bytes, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(bytes) < 1024.0:
            return '%3.1f %s%s' % (bytes, unit, suffix)
        bytes /= 1024.0

    return '%.1f %s%s' % (bytes, 'Y', suffix)

def ConvertNumbers(n):
    millnames = ['',' Thousand',' Million',' Billion',' Trillion']
    n = float(n)
    millidx = max(0,min(len(millnames)-1,int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

def remove_char(st:str):
    s = ''
    chars = ['\\','/',"'",'"',",","<",">","|","?",":",'*','.','-','`','~']
    for i in chars:
        st = st.replace(i,'')
    return unquote(st.replace('\\u0026','&'),encoding='utf-8')

def encrypt(text):
    key = 23
    """Encrypts text using a ceaser cypher"""
    encrypted = ""
    r=1
    for char in text:
        if char.isalpha():
            encrypted += chr((ord(char) + key - 97) % 26 + 97)+str(r)
            r+=2
        r+=3
    return encrypted[:25].replace('_','')

def getSize(url,session=requests,headers='') -> int:
    try: return int(req(
            method='head',out='headers',ses=session,url=url,h=headers,redirect=True
        )['Content-Length'])
    except: raise UrlNotFoundError(url)
def getHeaders(url,session=requests,headers='') -> dict:
    # try:
    return req(
            method='head',out='headers',ses=session,url=url,h=headers,redirect=True
        )
    # except: raise UrlNotFoundError(url)

def makeFile(path:str):
    try: os.mkdir(path)
    except:
        try: os.makedirs(path)
        except:
            try:
                open(path,'w')
            except: pass


def removePath(path:str):
    try: shutil.rmtree(path)
    except: pass


def moveFile(path_from:str,path_to:str):
    try: shutil.move(path_from,path_to)
    except: pass
def getCurrentPath() -> str:
    return os.path.abspath(os.getcwd()).replace('\\','/')+'/'

def exUrlArgs(url:str) -> list or None:
    args = {}
    try:
        for value in url[url.index('?')+1:].split('&'):
            params = value.split('=')
            args[params[0]] = params[1]
        return args
    except: return None
def PathExist(path:str,size=0) -> bool:
    p = os.path
    if size:
        return (p.exists(path) and p.getsize(path)==size)
    return p.exists(path)



import proglog

def combine_audio(vid,aud,out):
    # from moviepy.editor import *
    # videoclip = VideoFileClip(vid)
    # videoclip.audio = CompositeAudioClip([AudioFileClip(aud)])
    # videoclip.write_videofile(
    #     out,
    #     # logger=proglog.TqdmProgressBarLogger(print_messages=False),
    #     # threads =20
    # )

    # import subprocess
    # process =subprocess.Popen(
    #     ["ffmpeg",'-y', '-i',vid,'-i',aud, '-c','copy', out],
    #     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)
    # counter=1
    # for line in process.stdout:
    #     print(counter,": ",line)
    #     counter+=1

    # import ffmpeg
    # input_video = ffmpeg.input(vid)
    # input_audio = ffmpeg.input(aud)
    # ffmpeg.concat(input_video, input_audio, v=1, a=1).output(out,overwrite=True).run()

    from ffmpeg_progress_yield import FfmpegProgress

    ff = FfmpegProgress(
        ["ffmpeg",'-y', '-i',vid,'-i',aud, '-c','copy', out]
    )
    for progress in ff.run_command_with_progress():
        print(f"Adding Audio: {progress}/100 ",end='\r')


def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def pause(): os.system('pause')
def isPath(path:str) -> bool: return os.path.exists(path)

def findall_reg(pattern:str,text:str,compile=False) -> list:
    if compile:
        return re.findall(re.compile(pattern),text)
    return re.findall(pattern,text)


class RequestHeaderClass:
    def __init__(self,url:str,session:requests,headers:dict) -> None:
        self._url = url
        self._session = session
        try:
            self._headers =  requestOBJ.open(url).headers
        except:
            try:
                self._headers = session.head(url, stream=True).headers
            except:
                try: self._headers = session.get(url, stream=True).headers
                except: raise ValueError(f"Can`t Connect To Server: {url}")

    @property
    def filesize(self) -> int:
        try: return int(self._headers['Content-Length'])
        except: return 0

    @property
    def formated_filesize(self) -> str:
        try: return convert_size(int(self._headers['Content-Length']))
        except: return "0 B"
        
    @property
    def filename(self) -> str:
        try:
            return remove_char(re.findall(
                "filename=\"(.+)\";", self._headers['Content-Disposition'])[0])
        except:
            return self._url.split('/')[-1]

    @property
    def method(self) -> str:
        pass

    @property
    def isRange(self) -> bool:
        return ('Accept-Ranges' in self._headers and  self._headers['Accept-Ranges'] == 'bytes')
    
    @property
    def url(self) -> str: return self._url

    @property
    def content_data(self) -> requests:
        return self._session.get(self._url,stream=True,headers=self._headers)

def get_home_dir() -> str | None:
    return os.path.expanduser('~').replace('\\','/')+"/"

def formatDate(date:str) -> str:
    return date[:4]+"-"+date[4:6]+"-"+date[6:]