import os
import traceback
from common.spider import Spider

class Wangyiyun(Spider):
    def __init__(self):
        super().__init__('wangyiyun')
        self.referer = 'https://music.163.com/'
        self.msg = '网易云音乐'

    # 搜索歌曲
    def search_song(self,song):
        headers = {
            'authority': 'music.163.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'nm-gcore-status': '1',
            'origin': self.referer ,
            'referer': self.referer ,
            'user-agent': self.user_agent,
        }
        params = {
            'csrf_token': '',
        }
        d = '{"s":"{'+ song +'}","limit":"8","csrf_token":""}'
        enc = self.run_js('wangyiyun.js',"get_data('{}')".format(d))
        data = {
            'params': enc['encText'],
            'encSecKey': enc['encSecKey'],
        }
        response = self.post('https://music.163.com/weapi/search/suggest/web', params=params, headers=headers, data=data)
        if response.json()['code'] == 200:
            try:
                message = []
                for song_data in response.json()['result']['songs']:
                    # 把所有带有歌曲关键词的歌都存进来
                    if song in song_data['name']:
                        message.append({
                            'name':song_data['name'],
                            'id':song_data['id'],
                        })
                if message == []:
                    self.logger.info('未搜索到指定歌曲')
                    self.msg = '未搜索到指定歌曲'
                    return None
                else:
                    self.logger.info('搜索歌曲成功, message_len = {}'.format(str(len(message))))
                    return message
            except:
                self.logger.info('搜索解析过程出错, error is:{}'.format(traceback.format_exc()))
                self.msg = '搜索解析过程出错'
                return None
        elif response['code'] == 400:
            self.logger.info('歌曲搜索接口请求失败')
            self.msg = '歌曲搜索接口请求失败'
            return None

    # 把转换m4a为mp3
    def m4a_to_mp3(self,message,search_song):
        # 创建music文件夹
        if not os.path.exists('../media/music/{}/'.format(search_song)):
            os.mkdir('../media/music/{}/'.format(search_song))
        for song in message:
            try:
                content = self.get(url=song['url']).content
                # 打开文件，并在文件里写入二进制数据
                with open('../media/music/{search_song}/{name}_{id}.mp3'.format(search_song=search_song,name=song['name'], id=song['id']), 'wb') as f:
                    f.write(content)
                    f.close()
                self.logger.info('{}m4a转mp3成功'.format(song['name']))
            except:
                self.logger.info('m4a转mp3失败, song_name:{}, error is:{}'.format(song['name'],traceback.format_exc()))
                continue


    # 搜索歌曲
    def get_song(self,message):
        headers = {
            'authority': 'music.163.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'origin': 'https://music.163.com',
            'referer': 'https://music.163.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        }

        params = {
            'csrf_token': '',
        }
        # 记录抓取成功的次数
        get_success = 0
        # 把每个相关的歌都搜索一次
        for song in message:
            d = '{"ids":"['+ str(song['id']) +']","level":"standard","encodeType":"aac","csrf_token":""}'
            enc = self.run_js('wangyiyun.js', "get_data('{}')".format(d))
            data = {
                'params': enc['encText'],
                'encSecKey': enc['encSecKey'],
            }
            response = self.post('https://music.163.com/weapi/song/enhance/player/url/v1', params=params,headers=headers, data=data)
            if response.json()['code'] == 200:
                try:
                    song['url'] = response.json()['data'][0]['url']
                    get_success += 1
                    self.logger.info('{}获取成功, get_success:{}'.format(song['name'],str(get_success)))
                except:
                    self.logger.info('歌曲解析失败, error is:{}'.format(traceback.format_exc()))
                    self.msg = '歌曲解析失败'
                    continue
            elif response.json()['code'] == 400:
                self.logger.info('搜索歌曲失败, song_name:{}, song_id:{}'.format(song['name'],song['id']))
                self.msg = '搜素歌曲失败'
                continue
        return message


    def handel(self):
        self.logger.info('网易云音乐开始抓取')
        search_song = '孤勇者'
        # 先进行搜索
        message = self.search_song(search_song)
        if not message:
            return [{
                'msg':self.msg,
                'referer':self.referer,
                'message':message
            }]
        # 如果搜索到了歌就获取歌的m4a地址
        message = self.get_song(message)
        # 然后将m4a的地址转为mp3并且存在本地
        self.m4a_to_mp3(message,search_song)
        alldata = {
            'msg':self.msg,
            'referer':self.referer,
            'message': message
        }
        self.logger.info('网易云音乐结束抓取')
        return alldata

if __name__ == '__main__':
    wangyiyun = Wangyiyun()
    alldata = wangyiyun.handel()
    print(alldata)