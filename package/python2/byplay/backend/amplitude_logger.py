from __future__ import absolute_import
import logging
import time
import json

from byplay.backend.async_post import async_post
from byplay.backend.sys_info import sys_info
from byplay.config import Config


class AmplitudeLogger(object):
    def __init__(self, api_key, api_uri=u"https://api.amplitude.com/httpapi"):
        self.api_key = api_key
        self.api_uri = api_uri
        self.is_logging = True

    def turn_on_logging(self):
        self.is_logging = True

    def turn_off_logging(self):
        self.is_logging = False

    def _is_None_or_not_str(self, value):
        if value is None or type(value) is not unicode:
            return True

    def create_event(self, **kwargs):
        event = {}
        user_id = kwargs.get(u'user_id', None)
        device_id = kwargs.get(u'device_id', None)
        if self._is_None_or_not_str(user_id) and self._is_None_or_not_str(device_id):
            return None

        if self._is_None_or_not_str(user_id):
            event[u"device_id"] = device_id
        else:
            event[u"user_id"] = user_id

        event_type = kwargs.get(u'event_type', None)
        if self._is_None_or_not_str(event_type):
            return None

        event[u"event_type"] = event_type

        # integer epoch time in milliseconds
        if u"time" in kwargs:
            event[u"time"] = kwargs[u"time"]
        else:
            event[u"time"] = int(time.time() * 1000)

        if u"ip" in kwargs:
            event[u"ip"] = kwargs[u"ip"]

        event_properties = kwargs.get(u'event_properties', None)
        if event_properties is not None and type(event_properties) == dict:
            event[u"event_properties"] = event_properties

        sys = sys_info()
        event[u"platform"] = u"C4D plugin"
        event[u"os_name"] = sys[u"os.name"]
        event[u"os_version"] = sys[u"os.version"]
        event[u"app_version"] = u"c4d-plugin:{}".format(Config.build())
        event[u"device_model"] = u"c4d:{}".format(sys[u"c4d.version"])

        event_package = [
            (u'api_key', self.api_key),
            (u'event', json.dumps([event])),
        ]

        # print(event_package)

        # ++ many other properties
        # details: https://amplitude.zendesk.com/hc/en-us/articles/204771828-HTTP-API
        return event_package

    def log_event(self, event):
        if event is not None and type(event) == list:
            if self.is_logging:
                result = async_post(self.api_uri, data=event, headers={})
                return result


AMPLITUDE = AmplitudeLogger(api_key=u"5e18757a01b9d84a19dfddb7f0835a28")


def log_amplitude(event_type, **props):
    try:
        global AMPLITUDE
        AMPLITUDE.log_event(
            AMPLITUDE.create_event(
                device_id=u"c4d-plugin",
                event_type=event_type,
                user_id=Config.user_id(),
                event_properties=props
            )
        )
    except Exception, e:
        logging.error(e)
