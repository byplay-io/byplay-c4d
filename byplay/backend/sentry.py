import logging
import sys
import time
import traceback
from datetime import datetime

import random

from byplay.backend.async_post import async_post
from byplay.backend.sys_info import sys_info
from byplay.config import Config


def generate_random_key(length):
    return ''.join(random.choice('0123456789abcdef') for _ in range(length))


STORE_URL = "https://o244219.ingest.sentry.io/api/5780350/store/"
AUTH = """Sentry sentry_version=7,
sentry_timestamp={timestamp},
sentry_key=37c797dbf371420381b9f862843ea1b3,
sentry_client=byplay-c4d-python/1.0""".replace("\n", "")


def capture_exception():
    send_exception(*sys.exc_info())


def send_exception(exc_type, exc_value, exc_traceback):
    logging.error(exc_value)
    try:
        value = exc_value
        payload = {
            'event_id': generate_random_key(32),
            'platform': 'python',
            'culpit': '-',
            'timestamp': str(datetime.utcnow()),
            'dist': Config.build(),
            'tags': sys_info(),
            'user': {
                'id': Config.user_id(),
            },
            "exception": {
                "values": [{
                    "type": exc_type.__name__,
                    "value": str(value),
                    "stacktrace": {
                        "frames": list(
                            map(
                                lambda f: {
                                    'filename': f[0],
                                    'lineno': f[1] + 1,
                                    'function': f[2]
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
            headers={"X-Sentry-Auth": AUTH.format(timestamp=int(time.time()))},
            json=payload
        )
    except Exception as sending_exception:
        # raise sending_exception
        print("Could not send:(")
        print(sending_exception)
        logging.error(sending_exception)


class ExceptionCatcher:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return
        send_exception(exc_type, exc_val, exc_tb)
