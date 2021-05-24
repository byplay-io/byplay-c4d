import logging

import json
import sys
import threading


def _sync_post(url, params):
    logging.info("Doing async request to {}".format(url))
    request = _request_module()
    headers = {}
    data = None
    if 'data' in params:
        data = urlencode(params['data']).encode('utf8')
    if 'json' in params:
        headers['content-type'] = 'application/json'
        data = json.dumps(params['json']).encode('utf8')
    if 'headers' in params:
        for k, v in params['headers'].items():
            headers[k] = v
    req = request.Request(url, data=data, headers=headers)
    res = request.urlopen(req).read().decode('utf8')
    logging.info("Async response: {}".format(res))


def async_post(url, **params):
    logging.info("Starting async request to {}".format(url))
    thread = threading.Thread(target=_sync_post, args=(url, params))
    thread.setDaemon(True)
    thread.start()


def _request_module():
    if sys.version_info[0] == 2:
        import urllib2
        return urllib2
    else:
        import urllib.request
        return urllib.request


def urlencode(data):
    if sys.version_info[0] == 2:
        import urllib
        return urllib.urlencode(data)
    else:
        import urllib.parse
        print(data)
        return urllib.parse.urlencode(data)