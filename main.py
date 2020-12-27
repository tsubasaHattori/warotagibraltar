from twitter import *
from config import *
oauth_dance(app_name, consumer_key, consumer_secret, token_filename="./config.txt", open_browser=False)