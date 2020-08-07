# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/HistoricalArticlesToPdf

import os
import re
import math
import time
import json
import shutil
import psutil
import logging
import requests
from PIL import Image
from queue import Queue
from http import cookiejar
import urllib.parse as urlcode
import libs.sql.user_sql as UserSql
import libs.sql.wechat_sql as WechatSql
from libs.core.html2pdf import HtmlToPdfThreads

log = logging.getLogger(__name__)

class WechatTask(object):
    base_url = "https://mp.weixin.qq.com/cgi-bin/"
    start_login_url = base_url+"bizlogin?action=startlogin"
    getqrcode_url = base_url+"scanloginqrcode?action=getqrcode&random=%s"
    ask_url = base_url+"scanloginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1"
    login_url = base_url+"bizlogin?action=login"
    search_biz_url = base_url+"searchbiz"
    appmsg_url = base_url+"appmsg"
    referer = "https://mp.weixin.qq.com/"

    thread_list =[]
    img_path_dict = {}

    diz_list =[]

    def __init__(self,user_name, password, cookie, name, website_url,threads,out_path):
        self.user_name = user_name
        self.password = password
        self.cookie = cookie
        self.name = name.replace("\"","").replace(" ","")
        self.website_url = website_url
        self.task_queue = Queue()
        self.threads = threads
        self.out_path = out_path
        
    def start(self):
        self.__start_data__ = str(time.time).replace(".","")

        self.__create_dir__()
    
        self.__load_cookies__()

        self.__start_threads__()
        
        for thread in self.thread_list:
            thread.join()
        self.__print__()

        self.__delete_file__()

    def __create_dir__(self):       
        self.out_qrcode_path =  os.path.join(self.out_path,"qrcode")
        if not os.path.exists(self.out_qrcode_path):
            os.makedirs(self.out_qrcode_path)

        self.wx_cookie_path  = os.path.join(self.out_path,"wx.info")

    def __start_threads__(self):
        for thread_id in range(1,self.threads):
            thread_name = "Thread - " + str(thread_id)
            thread = HtmlToPdfThreads(self.task_queue,thread_id,thread_name)
            thread.start()
            self.thread_list.append(thread)

    def __data__(self,map=None):
        data = {"userlang":"zh_CN","redirect_url":"","login_type":"3","token":"","lang":"","f":"json","ajax":"1"}
        if map:
            for key,value in map.items():
                data[key] = value
        return data

    def __head__(self,heads=None):
        
        head ={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Referer": self.referer
        }

        if self.cookie:
            head["Cookie"] = self.cookie

        if heads:
            for key,value in heads.items():
                head[key] = value
        return head

    def __start_login__(self):
        data = {"sessionid":str(time.time()).replace(".","")}
        session,result = self.__http_request__(url=self.start_login_url,data=self.__data__(data),wait=1)
        
        if result:
            self.getqrcode(session)
                
    def getqrcode(self,session):
        time_str = str(time.time()).replace(".","")
        new_getqrcode_url = self.getqrcode_url.replace("%s",time_str)
        qrcode_path = os.path.join(self.out_qrcode_path,time_str + ".png")
        self.__http_io_request__(url=new_getqrcode_url,session=session,path=qrcode_path)
        log.warn("请使用微信扫描弹出的二维码图片用于登录微信公众号!")
        try:
            image = Image.open(qrcode_path)
            image.show()
        except Exception as e:
            log.error(e)
            raise Exception("获取二维码失败，请重试!")
        
        self.getqrcodeStatus(session)   

    def getqrcodeStatus(self,session,t=6):
        while True:
            session,result = self.__http_request__(method='get',url=self.ask_url,wait=t)
            if not result:
                return
            
            if result.get("status") == "3":
                log.warn("二维码已失效，请重新使用微信进行扫码!")
                self.getqrcode(session)
                return

            if str(result.get("status")) == "1":
                self.login(session)
                return
            if t == 6:
                t = 7
            else:
                t = 6            
            
    def login(self,session):
        data = {"lang":"zh_CN"}
        session,result = self.__http_request__(url=self.login_url,data=self.__data__(data))
        if not result:
            return

        redirect_url = result.get("redirect_url")
        if not redirect_url:
            return
        
        token_compile = re.compile(r'.*token=(.*).*')
        token = token_compile.findall(redirect_url)
        if len(token) < 0:
            return
        token = token[0]
        names = self.name.split(",")
        self.__save_cookie__(session,token)
        for name in names:
            self.search_biz(session,token,name)


    # 搜索公众号
    def search_biz(self,session,token,name,no=1,begin=0,count=5,total=0):

        data = {
            "action":"search_biz",
            "begin":begin,
            "count":count,
            "query":name,
            "token":token,
            "lang":"zh_CN",
            "f":"json",
            "ajax":1
        }
        
        self.referer = ("https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&createType=0&token=%s&lang=zh_CN") % (token)
        session,result = self.__http_request__(method='get',url=self.search_biz_url,data=data)
        if not result:
            return
            
        biz_list = result.get("list") # 公众号列表
        biz_total = result.get("total") # 公众号总数量
        if len(biz_list) == 0:
            return 
            
        for biz in biz_list:
            fakeid = biz.get("fakeid")
            nickname = biz.get("nickname")
            alias = biz.get("alias")
            if nickname != name:
                continue
            wi_id = WechatSql.insert_info(fakeid,alias,nickname)
            out_dir = os.path.join(self.out_path , nickname)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            begin = WechatSql.select_list_num(wi_id)
            app_msg_cnt = self.list_ex(session,fakeid,token,out_dir,wi_id)
            diz_dict ={}
            if app_msg_cnt != 0:
                diz_dict["wi_id"] = wi_id
                diz_dict["name"] = name
                diz_dict["total"] = app_msg_cnt
                diz_dict["current"] = str(app_msg_cnt - begin)
                diz_dict["html"] = os.path.join(out_dir,"html")
                diz_dict["pdf"] = os.path.join(out_dir,"pdf")
                self.diz_list.append(diz_dict)
            return

        begin = count + begin
        if no <= biz_total:
            self.search_biz(session,token,name,no,begin,count,biz_total)

    
    def list_ex(self,session,fakeid,token,out_dir,wi_id,no=0,begin=0,count=5,app_msg_cnt=0):
        data ={
            "action":"list_ex",
            "begin":str(begin),
            "count":str(count),
            "fakeid":str(fakeid),
            "type":"9",
            "query":"",
            "token":str(token),
            "lang":"zh_CN",
            "f":"json",
            "ajax":"1"
        }
        if begin < 0: # 防止出现负数的情况
            return app_msg_cnt

        if app_msg_cnt == 0: # 获取文章总数量
            session,result = self.__http_request__(method='get',url=self.appmsg_url,data=data,session=session)
            if not result:
                return app_msg_cnt
            app_msg_cnt = result.get("app_msg_cnt")

            nums = str(app_msg_cnt/10).split(".")
            if int(nums[1]) >= 5:
                start = app_msg_cnt - int(nums[1]) + 5
            else:
                start = app_msg_cnt - int(nums[1]) 
            self.list_ex(session,fakeid,token,out_dir,wi_id,begin=start, app_msg_cnt = app_msg_cnt) # 设置文章起始编号和文章总数量
            return app_msg_cnt
        
        session,result = self.__http_request__(method='get',url=self.appmsg_url,data=data,session=session)
        if not result:
            return app_msg_cnt
        app_msg_cnt = result.get("app_msg_cnt")
        app_msg_list = result.get("app_msg_list")
        if len(app_msg_list) == 0:
            return app_msg_cnt
        
        for app in list(reversed(app_msg_list)): 
            link = app.get("link")
            title = app.get("title")
            digest = app.get("digest")
            title_list = WechatSql.select_list_title(wi_id,begin)
            if title in title_list:
                continue
            i_date = str(time.time).replace(".","")
            WechatSql.insert_list(wi_id,no,title,link,digest,i_date)
            self.__get_article_details__(no,title,link,out_dir)
            no = no + 1
        begin = begin - count
        self.list_ex(session,fakeid,token,out_dir,wi_id,no,begin,count,app_msg_cnt) 
        
    def __get_article_details__(self,no,title,link,out_dir):
        filters = {'/','\\','?','*',':','"','<','>','|',' ','？','（','）','！','，','“',"”"}
        for filter in filters:
            title = title.replace(filter,"")

        html_path = os.path.join(out_dir,"html")
        pdf_path = os.path.join(out_dir,"pdf")
        image_path = os.path.join(html_path,"image") 
        if not os.path.exists(image_path):       
            os.makedirs(image_path)

        if not os.path.exists(pdf_path):
            os.makedirs(pdf_path)

        html_file = os.path.join(html_path,str(no)+ "-" +title+".html")
        pdf_file = os.path.join(pdf_path,str(no)+ "-" +title+".pdf")
        if os.path.exists(pdf_file): # PDF文件存在则不生成对应的PDF文件，否则继续
            return

        if not os.path.exists(html_file):
            content = self.__get_content__(link,image_path)
            with open(html_file,"w") as f:
                f.write(content)
                f.flush()
                f.close()
        
        task_info = {"html":html_file,"pdf":pdf_file}
        self.task_queue.put(task_info)  

    def __get_content__(self,link,image_path):
        self.referer = link
        session,content = self.__http_request__(method="get",url=link,flag=True)
        if not content:
            return

        src_compile = re.compile(r'data-src=\"(.*?)\"')
        src_urls = src_compile.findall(content)
        if len(src_urls) < 0:
            return
        for img_url in src_urls:
            if not (img_url.startswith("http://") or img_url.startswith("https://")):
                continue

            img_url_compile = re.compile("wx_fmt=(.*)?")
            img = img_url_compile.findall(img_url)
            suffix = ".png"
            if len(img)>0:
                suffix = "."+ str(img[0])
            img_name = str(time.time()).replace(".","") + suffix
            img_file = os.path.join(image_path,img_name)
            self.__http_io_request__(url=img_url,path=img_file)
            self.img_path_dict[img_url] = "./image/"+img_name

        content = content.replace("data-src","src")
        for key,value in  self.img_path_dict.items():
            content = content.replace(key,value)
        return content

    def __http_io_request__(self,method='get',url=None,data=None,headers=None,session=requests.session(),stream=True,path=None):
        if method =='get':
            resp = session.get(url=url,params=data,headers=self.__head__(headers),stream=stream)
        else:
            resp = session.post(url=url,data=data,headers=self.__head__(headers),stream=stream)

        if resp.status_code == 200:
            with open(path, 'wb+') as f:  
                for chunk in resp.iter_content(chunk_size=1024):  
                    if chunk:
                        f.write(chunk)  
                        f.flush()  
                f.close() 
            return session,True
        time.sleep(1)
        return session,False

    def __http_request__(self,method='post',url=None,data=None,headers=None,session=requests.session(),wait=5,flag=False):
        time.sleep(wait)
        if method == "get":
            resp = session.get(url = url, params = data, headers = self.__head__(headers))
        else:
            resp = session.post(url = url, data = data, headers = self.__head__(headers))
    
        if resp.status_code != 200:
            log.error("网络异常或者错误:"+str(resp.status_code))
            return session,None
        if flag:
            content = resp.text
            if not content:
                return session,None
            return session,content
    
        resp_json = resp.json()
        if not resp_json:
            return session,None
        log.debug(resp_json)
        base_resp = resp_json.get("base_resp")
        if base_resp:
            ret = base_resp.get("ret") 
            err_msg = base_resp.get("err_msg")
            if ret == 0:
                return session,resp_json
            elif err_msg == "default" or err_msg == "invalid csrf token" or err_msg=="invalid session" :
                UserSql.delete_user_info(0)
                self.__start_login__()
                return
            else:
                return session,None
        

    def __print__(self):
        change = 0
        current = 0
        for diz in self.diz_list:
            titles = WechatSql.select_list_to_diz(diz['wi_id'],self.__start_data__)
            for title in titles:
                if os.path.exists(os.path.join(diz["pdf"],title+".pdf")):
                    change = change + 1
                if os.path.exists(os.path.join(diz["html"],title+".html")):
                    current = current + 1 

            print(("公众号: %s ，共计 %s 篇文章" %(diz["name"],diz["total"])))
            print(("==> 本次共计获取 %s 篇文章，成功将 %s 篇文章转换为PDF文件。")%(str(current),str(change)))
            print(("==> PDF文件输出目录为: %s")%(diz["pdf"]))
            print(("==> HTML文件输出目录为: %s")%(diz["html"]))

    def __delete_file__(self):
        if os.path.exists(self.out_qrcode_path):
            shutil.rmtree(self.out_qrcode_path)

    def __save_cookie__(self,session,token):
        cookie = ""
        cookies =  session.cookies.items()
        for key,value in cookies:
            cookie = cookie + '{0}={1};'.format(key,value)
        UserSql.insert_user_info(self.user_name ,self.password,token,cookie,0)
        
    
    def __load_cookies__(self):
        session = requests.session()
        user_info = UserSql.select_user_info(0)
        if user_info:
            token =  user_info[0]
            self.cookie = user_info[1]
            names = self.name.split(",")
            for name in names:
                self.search_biz(session,token,name)
        else:
            self.__start_login__()
