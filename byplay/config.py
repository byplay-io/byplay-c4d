import json
import os
import logging
from byplay.version import VERSION
from distutils.dir_util import mkpath

class Config:
    _recordings_dir = None
    _user_id = None

    @staticmethod
    def mute_amplitude() -> bool:
        return False

    @staticmethod
    def is_dev() -> bool:
        return False

    @staticmethod
    def build() -> str:
        return VERSION

    @staticmethod
    def user_id() -> str:
        if Config._user_id is None:
            Config.read()
        return Config._user_id

    @staticmethod
    def recordings_dir() -> str:
        return Config._recordings_dir

    @staticmethod
    def user_config_path():
        return os.environ["BYPLAY_SYSTEM_DATA_PATH"]

    @staticmethod
    def log_file_path():
        return os.environ["BYPLAY_PLUGIN_LOG_PATH"]

    @staticmethod
    def _read_config_file():
        config_path = Config.user_config_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, encoding="utf-8") as f:
                    logging.debug("Successfully read config file")
                    return json.loads(f.read())
            else:
                raise ValueError("User config doesn't exist at {}".format(config_path))
        except Exception as e:
            logging.error("exception while reading config {}".format(config_path))
            logging.exception(e)
            return {'error': str(e)}

    @staticmethod
    def read():
        data = Config._read_config_file()
        logging.debug("Successfully read config file, {}".format(data))
        Config._user_id = data.get("userId")
        Config._recordings_dir = data.get("recordingsDir")
        if Config._recordings_dir is None:
            raise ValueError("Recordings dir is empty in config {}".format(data))

    @staticmethod
    def setup_logger():
        path = Config.log_file_path()
        mkpath(os.path.dirname(path))
        logging.basicConfig(filename=path, format='%(asctime)s - [%(levelname)s]: %(message)s', level=logging.DEBUG)
