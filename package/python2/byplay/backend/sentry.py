from __future__ import absolute_import
import logging
import sys
import time
import traceback
from datetime import datetime

import random

from byplay.backend.async_post import async_post
from byplay.backend.sys_info import sys_info
from byplay.config import Config
from itertools import imap


def generate_random_key(length):
    return u''.join(random.choice(u'0123456789abcdef') for _ in xrange(length))


STORE_URL = u"https://o244219.ingest.sentry.io/api/5780350/store/"
AUTH = u"""Sentry sentry_version=7,
sentry_timestamp={timestamp},
sentry_key=37c797dbf371420381b9f862843ea1b3,
sentry_client=byplay-c4d-python/1.0""".replace(u"\n", u"")


def capture_exception():
    send_exception(*sys.exc_info())


def send_exception(exc_type, exc_value, exc_traceback):
    logging.error(exc_value)
    try:
        value = exc_value
        payload = {
            u'event_id': generate_random_key(32),
            u'platform': u'python',
            u'culpit': u'-',
            u'timestamp': unicode(datetime.utcnow()),
            u'dist': Config.build(),
            u'tags': sys_info(),
            u'user': {
                u'id': Config.user_id(),
            },
            u"exception": {
                u"values": [{
                    u"type": exc_type.__name__,
                    u"value": unicode(value),
                    u"stacktrace": {
                        u"frames": list(
                            imap(
                                lambda f: {
                                    u'filename': f[0],
                                    u'lineno': f[1] + 1,
                                    u'function': f[2]
                                },
                                traceback.extract_tb(exc_traceback)
                            )
                        )
                    }
                }]
            }
        }
        async_post(
            STORE_URL,
            headers={u"X-Sentry-Auth": AUTH.format(timestamp=int(time.time()))},
            json=payload
        )
    except Exception, sending_exception:
        # raise sending_exception
        print u"Could not send:("
        print sending_exception
        logging.error(sending_exception)


class ExceptionCatcher(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return
        send_exception(exc_type, exc_val, exc_tb)
