"""
setuid

Utility for changing uid of scripts run as root
"""

import os
import pwd

__all__ = ["setuid"]


def setuid(user):
    """switches uid to a particular user if we are running as root

    Args:
        user (str): designated user

    Raises:
        Exception: Unable to set UID/GID for user
    """
    target_uid = None
    target_gid = None
    target_home = None

    if isinstance(user, int):
        _, _, target_uid, target_gid, _, target_home, *_ = pwd.getpwuid(user)
    else:
        _, _, target_uid, target_gid, _, target_home, *_ = pwd.getpwnam(user)

    if os.getuid() == 0:
        os.setgid(target_gid)
        os.setuid(target_uid)
        os.environ["HOME"] = target_home

    if (os.getuid(), os.getgid()) != (target_uid, target_gid):
        raise Exception(f"Unable to set UID/GID for {user}")
