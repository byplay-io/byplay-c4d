from __future__ import absolute_import
import os


def join(*args):
    str_convert = str
    return str_convert(os.path.join(*args).replace(u"\\", u"/"))
