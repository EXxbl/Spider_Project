from lxml import etree
from common.spider import Spider
import execjs


class Ggzy(Spider):
    def __init__(self):
        super().__init__()
        self.referer = ''
        self.msg = '天津市公共资源交易平台抓取'

    # 获取首页及所有翻页的页面连接
    def get_index(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
        }

        response = self.get('http://ggzy.zwfwb.tj.gov.cn/jyxx/index.jhtml', headers=headers,verify=False)
        if response.status_code == 200:
            self.referer = response.url
            tree = etree.HTML(response.text)
            maxlenth = int(tree.xpath('//li/input[@id="pageSelect"]/@maxlength')[0])
            page_urls = []
            if maxlenth > 5:
                maxlenth = 5
            for url_index in range(maxlenth):
                page_urls.append('http://ggzy.zwfwb.tj.gov.cn/jyxx/index_{}.jhtml'.format(str(url_index+1)))
            return page_urls
        else:
            self.msg = '首页获取失败'
            return []

    # 获取所有子页面的数据
    def get_page(self,page_urls):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'Referer':self.referer
        }
        # 获取分页url
        for url in page_urls:
            response = self.get(url=url,headers=headers)
            tree = etree.HTML(response.text)
            a_url_lists = tree.xpath('//li/div[@class="article-list3-t"]/a/@url')
            times = tree.xpath('//li/div[@class="article-list3-t"]/div[@class="list-times"]/text()')
            for i in range(len(tree.xpath('//div[@class="article-list3-t"]'))):
                fucnname = 'get_aes("{}")'.format(a_url_lists[i])
                js_code = self.run_js('ggzy.js',fucnname)
                page_dict = {
                    'url':js_code,
                    'referer':a_url_lists[i],
                    'title':'',
                    'datetime': times[i].strip()
                }


    def handel(self):
        page_urls = self.get_index()
        message = self.get_page(page_urls)
        print(self.msg)

if __name__ == "__main__":
    ggzy = Ggzy()
    outpute = ggzy.handel()
    print(outpute)