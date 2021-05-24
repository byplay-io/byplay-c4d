from __future__ import absolute_import
import logging

import json
import sys
import threading


def _sync_post(url, params):
    logging.info(u"Doing async request to {}".format(url))
    request = _request_module()
    headers = {}
    data = None
    if u'data' in params:
        data = urlencode(params[u'data']).encode(u'utf8')
    if u'json' in params:
        headers[u'content-type'] = u'application/json'
        data = json.dumps(params[u'json']).encode(u'utf8')
    if u'headers' in params:
        for k, v in params[u'headers'].items():
            headers[k] = v
    req = request.Request(url, data=data, headers=headers)
    res = request.urlopen(req).read().decode(u'utf8')
    logging.info(u"Async response: {}".format(res))


def async_post(url, **params):
    logging.info(u"Starting async request to {}".format(url))
    thread = threading.Thread(target=_sync_post, args=(url, params))
    thread.setDaemon(True)
    thread.start()


def _request_module():
    if sys.version_info[0] == 2:
        import urllib2
        return urllib2
    else:
        import urllib2, urllib
        return urllib.request


def urlencode(data):
    if sys.version_info[0] == 2:
        import urllib
        return urllib.urlencode(data)
    else:
        import urllib2, urllib, urlparse
        print data
        return urllib.urlencode(data)