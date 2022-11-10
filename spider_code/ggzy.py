from lxml import etree
from common.spider import Spider
import traceback
import execjs

class Ggzy(Spider):
    def __init__(self):
        super().__init__('ggzy')
        self.referer = ''
        self.msg = '天津市公共资源交易平台'

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
            if response.status_code == 200:
                try:
                    messages = []
                    tree = etree.HTML(response.text)
                    a_url_lists = tree.xpath('//li/div[@class="article-list3-t"]/a/@url')
                    times = tree.xpath('//li/div[@class="article-list3-t"]/div[@class="list-times"]/text()')
                    for i in range(len(tree.xpath('//div[@class="article-list3-t"]'))):
                        fucnname = 'get_aes("{}")'.format(a_url_lists[i])
                        js_code = self.run_js('ggzy.js',fucnname)
                        page_dict = {
                            'url':js_code,
                            'referer':url,
                            'title':'',
                            'datetime': times[i].strip(),
                        }
                        page_dict = self.get_text_page(page_dict)
                        messages.append(page_dict)
                except:
                    self.logger.info('解析分页url出错, error is:{}'.format(traceback.format_exc()))
                    self.msg = '解析分页url出错'
                    return messages
            else:
                self.logger.info('URL:{}, 请求失败'.format(url))
                self.msg = '分页url请求失败，请查看日志'
                return None
        return messages
    # 获取文章页面的内容
    def get_text_page(self,page_dict):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': page_dict['referer'],
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
        }
        response = self.get(url=page_dict['url'],headers=headers,verify=False)
        if response.status_code:
            try:
                tree = etree.HTML(response.text)
                # 标题
                title = tree.xpath('//div[@class="content-title"]/text()')[0]
                page_dict['title'] = title.strip()
                # 浏览次数
                views = 0
                if tree.xpath('//span[@id="views"]/text()'):
                    views = tree.xpath('//span[@id="views"]/text()')[0].strip()
                page_dict['views'] = int(views)
                # 信息来源
                origin = tree.xpath('//a[@class="originUrl"]/text()')[0].strip()
                page_dict['origin'] = origin
                # 页面文字
                contents = tree.xpath('//div[@id="content"]/p/span/text()')
                page_text = ''
                for content in contents:
                    page_text += content.replace('\xa0','') + '\r'
                page_dict['page_text'] = page_text
                return page_dict
            except:
                self.logger.info('文章页面解析失败, error is:{}'.format(traceback.format_exc()))
                self.msg = '文章页面解析失败'
                return None
        else:
            self.logger.info('文章页面请求失败')
            self.msg = '文章页面请求失败'
            return None

    # 主函数
    def handel(self):
        self.logger.info('天津市公共资源交易平台开始抓取')
        page_urls = self.get_index()
        message = self.get_page(page_urls)
        if message:
            alldata = {
                'msg': self.msg,
                'message': message
            }
        else:
            alldata = {
                'msg':self.msg,
                'message':[]
            }
        self.logger.info('天津市公共资源交易平台结束抓取')
        return alldata

if __name__ == "__main__":
    ggzy = Ggzy()
    alldata = ggzy.handel()
    print(alldata)