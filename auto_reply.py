# -*- coding: utf-8 -*-

from reply_words import REPLY_WORDS

import json
import time
import sys
import math
import re
import urllib
import io
import requests

from trend_train import repeat_trend
# from trend_train import mk_sentence_char
# from trend_train import mk_sentence_word
from user_train import user_copy

from regular_post import regular_post


from credential import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
from requests_oauthlib import OAuth1Session, OAuth1
from datetime import datetime
from datetime import timedelta
from operator import xor
from scipy.stats import norm
from threading import Thread


def post_reply(twitter, status_id, reply_status="auto reply"):
    url = "https://api.twitter.com/1.1/statuses/update.json"

    in_reply_to_status_id = status_id

    res = twitter.post(url, params={"status": reply_status, "in_reply_to_status_id": in_reply_to_status_id, "auto_populate_reply_metadata":True})
    print(res)

def auto_reply(twitter):
    while True:
        url = "https://api.twitter.com/1.1/search/tweets.json"
        screen_name = "@farmer_API"
        since = datetime.now() + timedelta(minutes=-15)
        query = screen_name + " exclude:retweets"
        query += " since:" + since.strftime("%Y-%m-%d_%H:%M:%S") + "_JST"
        params = {"q": query, "count": 50}
        res = twitter.get(url, params=params)
        try:
            tweets = json.loads(res.text)["statuses"]
            if len(tweets) == 0: 
                url = "https://api.twitter.com/1.1/search/tweets.json"
                screen_name = "@farmer_API"
                query = screen_name + " exclude:retweets"
                params = {"q": query, "count": 10}
                res = twitter.get(url, params=params)
                try:
                    tweets_tmp = json.loads(res.text)["statuses"]
                    since_id = tweets_tmp[0]['id']
                    break
                except KeyError: # リクエスト回数が上限に達した場合のデータのエラー処理
                    print('上限まで検索しました: auto_reply else')
                    time.sleep(900)
                    continue
            else:
                since_id = tweets[0]['id']
                break
        except KeyError: # リクエスト回数が上限に達した場合のデータのエラー処理
            print('上限まで検索しました: auto_reply init')
            time.sleep(900)
            continue

    while True:
        time.sleep(20)
        print("searching...")
        url = "https://api.twitter.com/1.1/statuses/mentions_timeline.json"
        params = {"count": 50, "since_id": since_id}
        res = twitter.get(url, params=params)
        tweets = json.loads(res.text)

        if len(tweets) > 0:
            since_id = tweets[0]['id']

            for tweet in tweets:
                print('({id}) [{username}]:{text}'.format(id=tweet['id'], username=tweet['user']['name'], text=tweet['text']))
                status = tweet['user']['name'] + 'さん、'

                if 'cm' in tweet['text'] and xor('男' in tweet['text'], '女' in tweet['text']):
                    status = height_reply(tweet['text'])

                elif 'train:' in tweet['text']:
                    screen_name = re.search('train:(.*)', tweet['text']).group(1) or tweet['user']['screen_name']
                    status = user_copy(twitter, screen_name)

                elif tweet["text"] in REPLY_WORDS:
                    status = REPLY_WORDS[tweet["text"]]

                elif 'おはよう' in tweet['text']:
                    status += 'おはようございます！'
                elif 'おっはよ' in tweet['text']:
                    status = 'おっはよ！'
                elif 'こんにちは' in tweet['text']:
                    status += 'こんにちは！'
                elif 'こんばんは' in tweet['text']:
                    status += 'こんばんは！'
                elif 'テスト' in tweet['text'] or 'てすと' in tweet['text'] or 'test' in tweet['text']:
                    status = 'テストお疲れ様です'
                else:
                    if datetime.now().microsecond % 2:
                        status = '私はベイマックス。あなたの健康を守ります。'
                    else:
                        status = tweet['user']['name'] + "というのかい？贅沢な名だねぇ。今からお前の名前は" + tweet['user']['name'][:math.ceil(len(tweet['user']['name'])/2)] + "だ！いいかい！"
                post_reply(twitter, tweet['id'], status)


def height_reply(text):
    if '男' in text:
        sex = 0
        sex_name = '男性'
    elif '女' in text:
        sex = 1
        sex_name = '女性'
    height = re.search('(\d+)(cm)', text)
    height = int(height.group(1))

    age = re.search('(\d+)(歳)', text) or re.search('(\d+)(才)', text)
    if age and int(age.group(1)) > 20 and int(age.group(1)) < 100:
        age = int(age.group(1)) 
    else:
        age = 20

    prob_per = height_rate(sex, height, age)

    rank = '下位' if prob_per > 0 else '上位'
    prob_per = abs(prob_per)

    if prob_per >= 0.000001:
        if prob_per >= 1:
            prob_str = '{:.2f}'.format(abs(prob_per))
        else:
            prob_str = '{:.6f}'.format(abs(prob_per))

        rank += prob_str + '%'
    else:
        rank += '0.000001%未満'
    status = str(height) + 'cmの' + str(age) + '歳' + sex_name + 'は、' + str(math.floor(age / 10) * 10) + '代日本人' + sex_name + 'の' + rank + 'です。\n\n(各分布は政府統計 国民健康・栄養調査[2017年次]による)'

    return status

def height_rate(sex, height, age): # 男:0 女:1 2017年次統計
    if age >= 20 and age < 30:
        mean = 157.5 if sex else 171.4
        sd = 5.4 if sex else 5.8
    if age >= 30 and age < 40:
        mean = 158.6 if sex else 171.2
        sd = 6.0 if sex else 5.5
    if age >= 40 and age < 50:
        mean = 158.2 if sex else 171.2
        sd = 5.4 if sex else 6.0
    if age >= 50 and age < 60:
        mean = 156.7 if sex else 170.2
        sd = 5.2 if sex else 6.0
    if age >= 60 and age < 70:
        mean = 153.9 if sex else 167.3
        sd = 5.3 if sex else 5.8
    if age >= 70:
        mean = 148.9 if sex else 162.5
        sd = 6.2 if sex else 6.3

    n = 6 # 小数点以下桁数
    prob = norm.cdf(x=height, loc=mean, scale=sd)
    prob = prob if height < mean else prob-1
    prob_per = prob * 100

    return prob_per

def auto_follow(twitter):
    while True:
        print("following!")

        url = "https://api.twitter.com/1.1/followers/ids.json"
        params = {'screen_name': 'farmer_API'}
        res = twitter.get(url, params=params)
        follower_ids = json.loads(res.text)['ids']

        url = "https://api.twitter.com/1.1/friends/ids.json"
        params = {'screen_name': 'farmer_API'}
        res = twitter.get(url, params=params)
        friend_ids = json.loads(res.text)['ids']

        url = "https://api.twitter.com/1.1/friendships/create.json"
        for follower_id in follower_ids:
            if follower_id in friend_ids:
                continue

            print(follower_id)

            params = {'user_id': follower_id}
            res = twitter.post(url, params=params)
            print(res)

        time.sleep(65)


def main():
    twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

    job_reply = Thread(target=auto_reply, args=(twitter,))
    job_reply.start()

    job_follow = Thread(target=auto_follow, args=(twitter,))
    job_follow.start()

    # job_regular = Thread(target=regular_post, args=(twitter,))
    # job_regular.start()

    # job_trend = Thread(target=repeat_trend, args=(twitter,))
    # job_trend.start()


    job_reply.join()
    job_follow.join()
    # job_regular.join()
    # job_trend.join()


    # print(json.dumps(list, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main()