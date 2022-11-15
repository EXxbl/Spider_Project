import traceback
from lxml import etree
from common.spider import Spider

class Fangtx(Spider):
    def __init__(self):
        super().__init__('ggzy')
        self.referer = 'https://passport.fang.com/'
        self.msg = '房天下'

    # 进行登录操作
    # 实测不需要cookies
    def login(self,username,password):
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://passport.fang.com',
            'Referer': self.referer,
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        fucnname = 'get_RSA(password="{}")'.format(password)
        pwd = self.run_js('fangtx.js',fucnname)
        data = {
            'uid': username,
            'pwd': pwd,
            'Service': 'soufun-passport-web',
            'AutoLogin': '0',
        }
        response = self.post(url="https://passport.fang.com/login.api",headers=headers,data=data)
        if response:
            self.referer = response.url
            self.logger.info('房天下登录成功')
            self.msg = '房天下登录成功'

    # 获取到二手房源
    def get_page_text(self):
        headers = {
            'authority': 'esf.fang.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': self.referer,
            'upgrade-insecure-requests': '1',
            'user-agent': self.user_agent,
        }
        response = self.get('https://esf.fang.com/', headers=headers)
        if response:
            self.referer = response.url
            return response.text

    # 解析页面
    def parse_page_text(self,page_text):
        tree = etree.HTML(page_text)
        rooms = tree.xpath('//dl[@dataflag="bg"]')
        messages = []
        for room in rooms:
            title = room.xpath('.//span[@class="tit_shop"]/text()')[0].strip()      # 标题
            link = self.referer + room.xpath('.//h4/a/@href')[0][1:]                           # 链接
            bed_room = room.xpath('.//p[@class="tel_shop"]/text()')[0].strip()      # 几房几厅
            area = room.xpath('.//p[@class="tel_shop"]/text()')[1].strip()          # 面积
            if room.xpath('.//p[@class="tel_shop"]/a[@class="link_rk"]/text()'):
                floor = room.xpath('.//p[@class="tel_shop"]/a[@class="link_rk"]/text()')[0] + room.xpath('.//p[@class="tel_shop"]/text()')[3].strip()         # 楼层
            else:
                floor = room.xpath('.//p[@class="tel_shop"]/text()')[3].strip()
            orientation = room.xpath('.//p[@class="tel_shop"]/text()')[4].strip()   # 朝向
            build_time = room.xpath('.//p[@class="tel_shop"]/text()')[5].strip()    # 修建时间
            adderss = room.xpath('.//p[@class="add_shop"]/span/text()')[0].strip()  # 地址
            allprice = room.xpath('.//span[@class="red"]/b/text()')[0].strip()      # 总价
            price = room.xpath('.//dd[@class="price_right"]/text()')[0].strip()     # 价格
            people_name = room.xpath('.//span[@class="people_name"]/a/text()')[0].strip() # 联系人

            messages.append({
                'title':title,
                'link':link,
                'bed_room':bed_room,
                'area':area,
                'floor':floor,
                'orientation':orientation,
                'build_time':build_time,
                'adderss':adderss,
                'allprice':allprice,
                'price':price,
                'people_name':people_name,
            })
        return messages

    # 主函数
    def handel(self):
        self.logger.info('房天下开始抓取')
        username = '18173028067'
        password = 'songjinLONG66'
        self.login(username=username,password=password)
        page_text = self.get_page_text()
        messages = self.parse_page_text(page_text)
        alldata = {
            'msg':self.msg,
            'referer':self.referer,
            'message':messages
        }
        self.logger.info('房天下结束抓取')
        return alldata

if __name__ == "__main__":
    fangtx = Fangtx()
    alldata = fangtx.handel()
    print(alldata)