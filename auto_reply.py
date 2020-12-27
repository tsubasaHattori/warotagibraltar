# -*- coding: utf-8 -*-

import json
import time
import random

from credential import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
from requests_oauthlib import OAuth1Session, OAuth1
from datetime import datetime
from datetime import timedelta
from threading import Thread


def post_reply(twitter, status_id, reply_status="auto reply"):
    url = "https://api.twitter.com/1.1/statuses/update.json"

    in_reply_to_status_id = status_id

    res = twitter.post(url, params={"status": reply_status, "in_reply_to_status_id": in_reply_to_status_id, "auto_populate_reply_metadata":True})
    print(res)

def auto_reply(twitter):
    while True:
        url = "https://api.twitter.com/1.1/search/tweets.json"
        screen_name = "@tinpostar75"
        since = datetime.now() + timedelta(minutes=-15)
        query = screen_name + " exclude:retweets"
        query += " since:" + since.strftime("%Y-%m-%d_%H:%M:%S") + "_JST"
        params = {"q": query, "count": 50}
        res = twitter.get(url, params=params)
        try:
            tweets = json.loads(res.text)["statuses"]
            if len(tweets) == 0: 
                url = "https://api.twitter.com/1.1/search/tweets.json"
                screen_name = "@tinpostar75"
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

                if 'わろた' in tweet['text'] or 'ワロタ' in tweet['text']:
                    if datetime.now().microsecond % 3 == 0:
                        status = 'ワロタSMGを発見。'
                    elif datetime.now().microsecond % 3 == 1 :
                        status = 'ワロタネーターを発見。'
                    else:
                        status = 'ワロタスタビライザーを発見。レベル' + str(random.randint(1,4)) + 'だ。'

                # elif 'ワロタ' in tweet['text']:
                #     status = 'おっはよ！'
                # elif 'こんにちは' in tweet['text']:
                #     status += 'こんにちは！'
                # elif 'こんばんは' in tweet['text']:
                #     status += 'こんばんは！'
                # elif 'テスト' in tweet['text'] or 'てすと' in tweet['text'] or 'test' in tweet['text']:
                #     status = 'テストお疲れ様です'
                else:
                    if datetime.now().microsecond % 2:
                        status = 'リロード中だ。'
                    else:
                        status = 'いいニュースだ。部隊全員次のリングに入ってる。'
                post_reply(twitter, tweet['id'], status)


def auto_follow(twitter):
    while True:
        print("following!")

        url = "https://api.twitter.com/1.1/followers/ids.json"
        params = {'screen_name': 'tinpostar75'}
        res = twitter.get(url, params=params)
        follower_ids = json.loads(res.text)['ids']

        url = "https://api.twitter.com/1.1/friends/ids.json"
        params = {'screen_name': 'tinpostar75'}
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