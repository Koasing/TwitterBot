from croniter import croniter
from datetime import datetime

import twitter
from twitter import TwitterError
import logging

from MessageWrapper import BraceMessage as __

class BotTweet(object):
    def __init__(self, config=None, *args, **kwargs):
        d = {'sid'       : '',                  # self id
             'cron'      : '0 * * * *',         # cron schedule
             'tweet'     : '{timestamp} #bot',  # tweet body (status)
             'timestamp' : '%x %X',             # timestamp
             'delete'    : False}               # delete previous bot tweet

        if type(config) is dict:
            d.update(config)

        self.sid       = d['sid']
        self.croniter  = croniter(d['cron'], datetime.now(), datetime)
        self.tweet     = d['tweet']
        self.timestamp = d['timestamp']

        self.logger    = logging.getLogger(type(self).__name__)

        # initialize croniter
        self.schedule = self.croniter.get_next()

        # store previous bot tweet to delete after time
        if d['delete'] is True:
            self.logger.warning(__('\"{sid}\" Deleting previous bot tweet is yet not implemented. SORRY!', sid=self.sid))
            self.previous_tweet = None
        else:
            self.previous_tweet = None

        return

    def __lt__(self, other):
        # comparator "less than"
        if not isinstance(other, type(self)):
            raise TypeError()
        return self.schedule < other.schedule

    def __eq__(self, other):
        # comparator "equals to"
        if not isinstance(other, type(self)):
            raise TypeError()
        # because croniter.get_current() returns floating value, direct comparison is not effective.
        return self.schedule == other.schedule

    def parse(self):
        map = {}
        map['timestamp'] = datetime.now().strftime(self.timestamp)
        # TODO : ADD PARSER
        return self.tweet.format_map(map)

    def post(self, api):
        # trivial check
        if not isinstance(api, twitter.api.Api):
            raise TypeError()

        if datetime.now() < self.schedule:
            self.logger.debug(__('\"{sid}\" Next schedule is {next}... do nothing.', sid=self.sid, next=self.schedule))
            return False

        # update schedule
        self.schedule = self.croniter.get_next()

        # do posting
        status = self.parse()

        try:
            retval = api.PostUpdate(status, trim_user=True)
            self.logger.info(__('\"{sid}\" Tweet successful. Next schedule is {next}', sid=self.sid, next=self.schedule))
            return retval.id

        except TwitterError as e:
            # tweet failed
            self.logger.warning(__('\"{sid}\" Tweet failed ({message})', sid=self.sid, message=e.message))
            return False

        # should not reach here
        assert False
