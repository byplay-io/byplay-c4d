from __future__ import absolute_import
import os


def join(*args):
    return os.path.join(*args).replace(u"\\", u"/")
