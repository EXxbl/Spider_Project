import base64
import os
import time
import tkinter
import traceback
from PIL import Image
from lxml import etree
import tkinter.messagebox
from common.spider import Spider
from common.parse_slider import get_distance

class Jijian(Spider):
    def __init__(self):
        super().__init__('jijian')
        self.page_code = 0
        self.referer = ''
        self.msg = '极简壁纸'

    # 保存图片
    def save_image(self,img_data,img_name):
        if not os.path.exists('../media/image/jijian'):
            os.mkdir('../media/image/jijian')
        webpPath = '../media/image/jijian/' + img_name.replace('.jpg','').replace('.png','')
        with open(webpPath + '.webp', 'wb') as e:
            e.write(img_data)
        # 打开图片并赋值一份新的图片
        img = Image.open(webpPath + ".webp")
        img.load()
        # 将赋值的图片修改后缀保存在原路径
        img.save('../media/image/jijian/' + img_name)
        # 删除原webp图
        os.remove(webpPath + ".webp")

    # 请求getData
    def request_getData(self,page_code):
        headers = {
            'authority': 'api.zzzmh.cn',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://bz.zzzmh.cn',
            'pragma': 'no-cache',
            'referer': 'https://bz.zzzmh.cn/',
            'user-agent': self.user_agent,
        }

        json_data = {
            'size': 24,
            'current': page_code,
            'sort': 0,
            'category': 0,
            'resolution': 0,
            'color': 0,
            'categoryId': 0,
            'ratio': 0,
        }

        response = self.post('https://api.zzzmh.cn/bz/v3/getData', headers=headers, json=json_data)
        if response.json()['msg'] == 'success':
            return response.json()['result']
        else:
            self.logger.info('getData返回出错 msg:{}'.format(response.json()['msg']))
            self.msg = 'getData返回出错'
            return None
    # 进行滑块验证请求发送
    def check(self,distance,secretKey,token):
        headers = {
            'authority': 'api.zzzmh.cn',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json; charset=UTF-8',
            'origin': 'https://bz.zzzmh.cn',
            'pragma': 'no-cache',
            'referer': 'https://bz.zzzmh.cn/',
            'user-agent': self.user_agent,
            'x-requested-with': 'XMLHttpRequest',
        }
        pointJson = self.run_js('jijian.js','''get_pointJson('{"x":{'''+str(310*distance/420)+'''},"y":5}',"'''+secretKey+'''")''')
        json_data = {
            'captchaType': 'blockPuzzle',
            'pointJson': pointJson,
            'token': token,
        }
        response = self.post('https://api.zzzmh.cn/captcha/check', headers=headers, json=json_data)
        if response.json()['repCode'] == "0000":
            return True
        return False

    # 请求get包
    def request_get(self):
        headers = {
            'authority': 'api.zzzmh.cn',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json; charset=UTF-8',
            'origin': 'https://bz.zzzmh.cn',
            'pragma': 'no-cache',
            'referer': 'https://bz.zzzmh.cn/',
            'user-agent': self.user_agent,
            'x-requested-with': 'XMLHttpRequest',
        }

        json_data = {
            'captchaType': 'blockPuzzle',
            'clientUid': None,
            'ts': int(time.time()*1000),
        }

        response = self.post('https://api.zzzmh.cn/captcha/get', headers=headers, json=json_data)
        if response:
            originalImageBase64 = response.json()['repData']['originalImageBase64']
            jigsawImageBase64 = response.json()['repData']['jigsawImageBase64']
            secretKey = response.json()['repData']['secretKey']
            token = response.json()['repData']['token']
            img_data = base64.b64decode(originalImageBase64)
            with open('../media/image/jijian/001.png', 'wb') as f:
                f.write(img_data)
            img_data = base64.b64decode(jigsawImageBase64)
            with open('../media/image/jijian/002.png', 'wb') as f:
                f.write(img_data)
            distance = get_distance(bg='../media/image/jijian/001.png',tp='../media/image/jijian/002.png')
            check_bool = self.check(distance,secretKey,token)
            if not check_bool:
                self.logger.info('滑动验证码匹配失败')
                self.msg = '滑动验证码匹配失败'
        else:
            self.logger.info('请求滑动验证码滑块图失败')
            self.msg = '请求滑动验证码失败'
            return None

    # 获取请求图片的auth_key，并且请求图片
    def get_img(self,result):
        img_list = self.run_js(js_name='jijian.js',func_name='get_image("{}")'.format(result))
        for auth_key in img_list:
            headers = {
                'authority': 'cdn2.zzzmh.cn',
                'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'referer': 'https://bz.zzzmh.cn/',
                'user-agent': self.user_agent,
            }
            params = {
                'auth_key': auth_key[1],
            }
            url = 'https://cdn2.zzzmh.cn/wallpaper/origin/{}/thumbs'.format(auth_key[0])
            response = self.get(url=url,params=params,headers=headers)
            if response:
                self.save_image(response.content,auth_key[0])
            else:
                self.logger.info('获取图片失败，page_code={}'.format(self.page_code))
                return None

    def get_message(self):
        for self.page_code in range(1,200):
            cont = tkinter.messagebox.askokcancel('提示','马上要抓取极简壁纸第{}页, 是否继续?'.format(self.page_code))
            if cont:
                if self.page_code > 1:
                    self.request_get()
                result = self.request_getData(self.page_code)
                self.get_img(result)
                if not result:
                    return None
            else:
                return None
    # 主函数
    def handel(self):
        self.logger.info('极简壁纸开始抓取')
        message = self.get_message()
        if message != None:
            alldata = {
                'msg': self.msg,
                'message': message
            }
        else:
            alldata = {
                'msg':self.msg,
                'message':[]
            }
        self.logger.info('极简壁纸结束抓取')
        return alldata

if __name__ == "__main__":
    jijian = Jijian()
    alldata = jijian.handel()
    print(alldata)