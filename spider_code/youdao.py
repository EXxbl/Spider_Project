import time
import execjs
from common.spider import Spider

class Youdao(Spider):
    def __init__(self):
        super().__init__()

    # 读取js文件并且获取md5加密的值
    def get_md5(self,e):
        self.time_code = str(int(time.time()*10000))
        # 获取js运行结果
        funcname = 'get_md5("{}","{}")'.format(e,self.time_code)
        sign = self.run_js('youdao.js',funcname)
        return sign


    # 请求翻译接口返回翻译的内容
    def get_translate(self,sign,e):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://fanyi.youdao.com',
            'Referer': 'https://fanyi.youdao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        cookies = {
            'OUTFOX_SEARCH_USER_ID': '-1329751019@10.112.57.87',
            'OUTFOX_SEARCH_USER_ID_NCOO': '1266717750.0494585',
            '___rl__test__cookies': self.time_code[:-1],
        }
        params = {
            'smartresult': [
                'dict',
                'rule',
            ],
        }
        salt = self.time_code
        lts = self.time_code[:-1]
        data = {
            'i': e,
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': salt,
            'sign': sign,
            'lts': lts,
            'bv': '9edd1e630b7d8f13679a536d504f3d9f',
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME',
        }

        self.session.cookies.update(cookies)
        response = self.post(url='https://fanyi.youdao.com/translate_o', params=params, headers=headers, data=data)
        return response.json()

    def handel(self,e):
        sign = self.get_md5(e)
        world_translate = self.get_translate(sign,e)
        if world_translate['errorCode'] == 0:
            output = []
            for world in world_translate['smartResult']['entries']:
                if world:
                    output.append(world.strip())
            return output
        else:
            return '有道未搜索到该单词释义或未搜索到该语种'

if __name__ == "__main__":
    youdao = Youdao()
    output = youdao.handel('car')
    print(output)