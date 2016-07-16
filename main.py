from BotTweet import BotTweet
from croniter import croniter
from datetime import datetime

import twitter

import json
import logging
import logging.config
import signal
import sys
import time

# Event loop handlr
run_flag = True

# Ctrl-C routine
def interrupt_handler(signal, frame):
    global run_flag
    run_flag = False
    print('Ctrl-C pressed... Event loop will be terminated within 5 seconds...')

signal.signal(signal.SIGINT, interrupt_handler)

cfg = {}
with open('config.json', encoding='utf8') as fp:
    cfg = json.load(fp)
    with open(cfg['log'], encoding='utf8') as fp:
        logcfg = json.load(fp)
        logging.config.dictConfig(logcfg)

credential = cfg['auth']
tweet = []

for t in cfg['tweet']:
    b = BotTweet(t)
    tweet.append(b)

api = twitter.api.Api(**credential)
user = api.VerifyCredentials()

if user is None:
    print('INVALID CREDENTIAL', file=sys.stderr)
    sys.exit()

next = min(tweet)

# TODO: change to logging
print('Working User : @{user}'.format(user = user.screen_name), file=sys.stderr)
print('Next schedule is {next}'.format(next = next.schedule), file=sys.stderr)

while run_flag:
    time_left = (next.schedule - datetime.now()).total_seconds()

    if time_left > 5:
        time.sleep(5)
        continue

    elif time_left > 0:
        time.sleep(1)
        continue

    next.post(api)
    next = min(tweet)
