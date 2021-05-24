from __future__ import absolute_import
import logging
import platform


def sys_info():
    sysname, nodename, release, version, machine, _processor = platform.uname()

    c4d_version = u"unk"
    try:
        import c4d
        c4d_version = unicode(c4d.GetC4DVersion())

    except Exception, e:
        logging.error(e)

    return {
        u"c4d.version": c4d_version,
        u"os.name": sysname,
        u"node.name": nodename,
        u"os.release": release,
        u"os.version": version
    }
