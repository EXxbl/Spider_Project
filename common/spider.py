import requests
from common import useragent
from common import connect
import traceback
import execjs

class Spider(object):

    def __init__(self):
        self.session = requests.Session()
        self.post = self.session.post
        self.get = self.session.get
        self.user_agent = useragent.get_user_agent()

    def connent(self):
        return connect

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
