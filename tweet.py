from credential import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
from requests_oauthlib import OAuth1Session

def post_tweet(twitter, body):
    url = "https://api.twitter.com/1.1/statuses/update.json"
    res = twitter.post(url, params={"status": body})
    print(res)

def main():
    twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

    body = "空爆を要請する！"
    post_tweet(twitter, body)

if __name__ == '__main__':
    main()