from __future__ import with_statement
from __future__ import absolute_import
import json
import os
import logging
# from byplay.version import VERSION
from distutils.dir_util import mkpath
from io import open
VERSION = u'1.0.1'

class Config(object):
    _recordings_dir = None
    _user_id = None

    @staticmethod
    def mute_amplitude():
        return False

    @staticmethod
    def is_dev():
        return False

    @staticmethod
    def build():
        return VERSION

    @staticmethod
    def user_id():
        if Config._user_id is None:
            Config.read()
        return Config._user_id

    @staticmethod
    def recordings_dir():
        return Config._recordings_dir

    @staticmethod
    def user_config_path():
        return os.environ[u"BYPLAY_SYSTEM_DATA_PATH"]

    @staticmethod
    def log_file_path():
        return os.environ[u"BYPLAY_PLUGIN_LOG_PATH"]

    @staticmethod
    def _read_config_file():
        config_path = Config.user_config_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, encoding=u"utf-8") as f:
                    logging.debug(u"Successfully read config file")
                    return json.loads(f.read())
            else:
                raise ValueError(u"User config doesn't exist at {}".format(config_path))
        except Exception, e:
            logging.error(u"exception while reading config {}".format(config_path))
            logging.exception(e)
            return {u'error': unicode(e)}

    @staticmethod
    def read():
        data = Config._read_config_file()
        logging.debug(u"Successfully read config file, {}".format(data))
        Config._user_id = data.get(u"userId")
        Config._recordings_dir = data.get(u"recordingsDir")
        if Config._recordings_dir is None:
            raise ValueError(u"Recordings dir is empty in config {}".format(data))

    @staticmethod
    def setup_logger():
        path = Config.log_file_path()
        mkpath(os.path.dirname(path))
        logging.basicConfig(filename=path, format=u'%(asctime)s - [%(levelname)s]: %(message)s', level=logging.DEBUG)
