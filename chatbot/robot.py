from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.models import (TemplateSendMessage, ButtonsTemplate,
                            PostbackTemplateAction, CarouselTemplate,
                            CarouselColumn)
from .cluster_recommend import ClusterRecommend
import re
from pymongo import MongoClient

line_bot_api = LineBotApi('b8c+EloUjPhs/nCv2PGkyI905gbBaZ+VYwb'
                          'MkjN9Zuw8av/+tLZxprXNcaB7F8qNN4qrq08'
                          'NYMSAHJszAlSFt5hhkmZyEp2o07onwaKaQW4'
                          'XuHoEmQkINe+z4f587gqJkHAwWOh80K13dFA'
                          'HhZxwjgdB04t89/1O/w1cDnyilFU=')

recommender = ClusterRecommend()
domain = 'https://5a42a59d.ngrok.io'
welcome_carousel_title = '歡迎使用電影推薦系統'
welcome_carousel_des = "請選擇一種推薦方式"
title = 'Movie Subway'
cluster_carousel_des = '共五欄15個分類,請選擇感興趣的分類後,按下確認'
client = MongoClient('mongodb://localhost:27017/')

class Adam:
    sees = None
    user_select_tag = None
    choose = None

    def __init__(self):
        self.sees = 'nothing'
        self.user_select_tags = ''
        self.choose = ''

    def eyes(self, event):
        message_type = event.type
        if message_type == "postback":
            if event.postback.data == 'movieSubway':  # user click movie subway button
                self.sees = 'movieSubway'
            elif re.findall(r'^c\d+', event.postback.data):  # user click cluster button
                self.sees = 'clusterId'
            elif re.findall(r'^\d+', event.postback.data):  # user click tag
                self.sees = 'tagid'
            elif event.postback.data == '-1':  # user click submit
                self.sees = 'submit'
            elif event.postback.data == '-2':  # user click reset
                self.sees = 'reset'
            elif event.postback.data == "movieClassic":
                self.sees = 'movieClassic'
                self.choose = 'way A'
            elif event.postback.data == "movieAngle":
                self.sees = 'movieAngle'
                self.choose = 'way B'
        elif message_type == "message":
            if self.choose != "":
                try:
                    self.getMovie(event.message.text, self.choose)
                    self.sees = 'movie name'
                except TypeError:
                    pass
            hello_list = ['hi', 'Hi', 'Hello', "hello", '你好', '安', '嗨']
            for w in hello_list:
                if re.findall(w, event.message.text):  # user say hi
                    self.sees = 'user_say_hi'
        elif message_type == 'follow':
            self.sees = 'user is here'

    def getMovie(self, movie_like, choose):
        db = client['bb104t1']
        collection = db['multiRecommend']
        recommend = collection.find_one({'chname': movie_like})
        if choose == 'way A':
            str_1 = 'Association:\n'
            if recommend['result_Association'][0] == 'no movie to recommend':
                str_2 = 'no movie to recommend'
            else:
                ll = []
                for two in recommend['result_Association']:
                    for one in two:
                        ll.append(one)
                str_2 = '\n'.join(ll)
            result = '\n'.join([str_1, str_2])
            return result
        str_3 = 'Collaborative:\n\n'
        if choose == 'way B':
            ll = []
            for two in recommend['result_Collaborative']:
                for one in two:
                    ll.append(one)
            str_4 = '\n'.join(ll)
            result = ''.join([str_3, str_4])
            return result

    def response(self, event):
        if (self.sees == 'user_say_hi') or (self.sees == 'user is here'):
            self.__init__()
            welcome_button = TemplateSendMessage(
                alt_text='Welcome Button Template',
                template=ButtonsTemplate(
                    thumbnail_image_url='{}/static/hello.jpg'.format(domain),
                    title=welcome_carousel_title,
                    text=welcome_carousel_des,
                    actions=[PostbackTemplateAction(label='Movie Subway', data="movieSubway"),
                             PostbackTemplateAction(label='Movie Classic', data="movieClassic"),
                             PostbackTemplateAction(label='Movie Angle', data="movieAngle")]))
            line_bot_api.reply_message(event.reply_token, messages=welcome_button)
        if self.sees == 'movieSubway':
            self.__init__()
            button_label_list = []
            for cid in recommender.info.keys():
                button_label_list.append(recommender.info[cid]['name'])
            button_list = []
            for button_label in button_label_list:
                button = PostbackTemplateAction(
                    label=button_label,
                    data='c{}'.format(button_label_list.index(button_label)))
                button_list.append(button)
            carousel_column_list = []
            button_add_list = []
            c = 1
            for button in button_list:
                button_add_list.append(button)
                if len(button_add_list) == 3:
                    carousel_column = CarouselColumn(
                                      thumbnail_image_url='{}/static/cc{}.jpg'.format(domain, c),
                                      title=title,
                                      text=cluster_carousel_des,
                                        actions=button_add_list)
                    carousel_column_list.append(carousel_column)
                    button_add_list = []
                    c += 1
                else:
                    pass
            cluster_carousel = TemplateSendMessage(
                alt_text='Cname Carousel', template=CarouselTemplate(columns=carousel_column_list))
            line_bot_api.reply_message(event.reply_token, messages=cluster_carousel)
        if self.sees == 'clusterId':
            self.__init__()
            cid = event.postback.data.replace('c', '')
            recommender.setCluster(cid)
            template_num = int((len(recommender.getTags(recommender.user_select['cluster']))+3)/3)
            tag_name_list = recommender.getTags(recommender.user_select['cluster'])
            tag_name_list.extend(["確認", '重選'])
            button_list = []
            for tag in tag_name_list:
                if tag == "確認":
                    button = PostbackTemplateAction(label=tag, data='-1')
                elif tag == "重選":
                    button = PostbackTemplateAction(label=tag, data='-2')
                else:
                    tag_id = re.findall(r'^(\d+)', tag)[0]
                    button = PostbackTemplateAction(label=tag, data=tag_id)
                button_list.append(button)
            while True:
                if len(button_list) % 3 == 0:
                    break
                else:
                    button = PostbackTemplateAction(label=" ", data='-1')
                    button_list.append(button)
            carousel_column_list = []
            c = 1
            addbutton = []
            for button in button_list:
                if c % 3 == 0:
                    addbutton.append(button)
                    car = CarouselColumn(thumbnail_image_url='{}/static/{}.jpg'.format(domain, cid),
                                         title=recommender.info[recommender.user_select['cluster']]['name'],
                                         text='共{}欄{}個標籤,請選擇感興趣的標籤後,按下確認鍵（可複選）'.format(template_num, (len(tag_name_list) - 2)),
                                         actions=addbutton)
                    carousel_column_list.append(car)
                    addbutton = []
                else:
                    addbutton.append(button)
                c += 1
            tag_carousel = TemplateSendMessage(
                alt_text='Tag Carousel',
                template=CarouselTemplate(columns=carousel_column_list))
            line_bot_api.reply_message(event.reply_token, messages=tag_carousel)
        if self.sees == 'tagid':
            self.user_select_tags += "{} ".format(event.postback.data)
        if self.sees == 'submit':
            result = "已選擇： {}\n---------------------\n推薦您以下電影：\n".format(self.user_select_tags)
            text = self.user_select_tags.strip()
            recommender.setTags(text)
            recommender.setRel()
            movie_list = recommender.getMovies()
            for t in movie_list:
                result += "{}\n{}\n".format(t[1], t[2])
                result += '---------------------\n'
            line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=result))
            self.__init__()
        if self.sees == 'reset':
            self.__init__()
            line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text='清除已選標籤'))
        if self.sees == 'nothing':
            line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text="constructing"))
        if (self.sees == "movieClassic") or (self.sees == "movieAngle"):
            result = "請輸入一部您喜歡的電影片名"
            line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=result))
        if self.sees == 'movie name':
            result = self.getMovie(event.message.text, self.choose)
            line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=result))
