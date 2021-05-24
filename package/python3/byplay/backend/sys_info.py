import logging
import platform


def sys_info():
    sysname, nodename, release, version, machine, _processor = platform.uname()

    c4d_version = "unk"
    try:
        import c4d
        c4d_version = str(c4d.GetC4DVersion())

    except Exception as e:
        logging.error(e)

    return {
        "c4d.version": c4d_version,
        "os.name": sysname,
        "node.name": nodename,
        "os.release": release,
        "os.version": version
    }
