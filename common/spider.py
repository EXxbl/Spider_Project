import os
import time
import requests
from common import useragent
from common import connect
import traceback
import execjs
import logging
import datetime

class Spider(object):
    def __init__(self,spider_name):
        self.session = requests.Session()
        self.user_agent = useragent.get_user_agent()
        self.logger = self.save_logger(spider_name)

    def connent(self):
        return connect

    # get请求
    def get(self,url = None,headers = None,params = None,verify = True,timeout = 10,retry_times = 3,proxies=None,**kwargs):
        response = None
        # 定义重试次数
        for i in range(retry_times):
            try:
                response = self.session.get(url=url,headers=headers,params=params,verify=verify,timeout=timeout,
                                             **kwargs)
                if response.status_code == 500:
                    self.logger.info('服务器遇到错误, 无法完成请求, status_code:{}'.format(response.status_code))
                    break
                if response.status_code == 503:
                    self.logger.info('服务器不可用, 服务器超载或已停止使用, status_code:{}'.format(response.status_code))
                    break
                if response.status_code == 504:
                    self.logger.info('服务器网关或代理超时, status_code:{}'.format(response.status_code))
                    continue
                if response.status_code == 404:
                    self.logger.info('服务器找不到该网页, status_code:{}, url:{}'.format(response.status_code,url))
                    break
                if response.status_code == 200:
                    self.logger.info(url + ' : ' + str(response.status_code))
                    return response
            except:
                self.logger.info('请求失败, url:{}, error is:{}'.format(url,traceback.format_exc()))
                continue
        return None

    # post请求
    def post(self,url = None,headers = None,params = None,verify = True,timeout = 5,retry_times = 3,proxies=None,**kwargs):
        response = None
        for i in range(retry_times):
            try:
                response = self.session.post(url=url, headers=headers, params=params, verify=verify, timeout=timeout,
                                             **kwargs)
                if response.status_code == 500:
                    self.logger.info('服务器遇到错误, 无法完成请求, status_code:{}'.format(response.status_code))
                    break
                if response.status_code == 503:
                    self.logger.info('服务器不可用, 服务器超载或已停止使用, status_code:{}'.format(response.status_code))
                    break
                if response.status_code == 504:
                    self.logger.info('服务器网关或代理超时, status_code:{}'.format(response.status_code))
                    continue
                if response.status_code == 404:
                    self.logger.info('服务器找不到该网页, status_code:{}, url:{}'.format(response.status_code, url))
                    break
                if response.status_code == 200:
                    self.logger.info(url + ' : ' + str(response.status_code))
                    return response
            except:
                self.logger.info('请求失败, url:{}, error is:{}'.format(url, traceback.format_exc()))
                continue
        return None

    # 调用js函数
    def run_js(self,js_name,func_name):
        try:
            node = execjs.get()
            with open('../javascript/{}'.format(js_name),'r',encoding='utf-8') as js:
                ctx = node.compile(js.read(),cwd =r'../javascript/node_modules')
                js_code = ctx.eval(func_name)
            return js_code
        except:
            print(traceback.format_exc())
            return None

    # 保存日志
    def save_logger(self,spider_name):
        logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # 创建logger对象
        logger = logging.getLogger('')
        logger.handlers.clear()
        # 现在的时间
        now = datetime.date.today()
        # 日志地址
        log_path = '../logs/{}'.format(now)
        # 创建文件
        if not os.path.exists('../logs'):
            os.mkdir('../logs')
        if not os.path.exists(log_path):
            os.mkdir(log_path)

        handler = logging.FileHandler(
            "../logs/{}/spider_{}_{}.log".format(now, spider_name, now),encoding='utf-8')
        logger.addHandler(handler)
        # 定义日志输出格式
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(module)s - %(lineno)d/  %(message)s'))
        return logger
