"""
local_env

Environment detection routine
"""

import os
import re

detected_env = None

__all__ = ["local_env"]


def local_env():
    """returns detected environment name

    Returns:
        str: dev or test or prod
    """
    global detected_env
    if detected_env is None:
        if "LOCAL_ENV" in os.environ:
            detected_env = os.environ["LOCAL_ENV"]
        else:
            shn = os.uname().nodename
            shn = re.sub(r"\..*", "", shn)
            if re.search(r"-d\d+$", shn):
                detected_env = "dev"
            elif re.search(r"-t\d+$", shn):
                detected_env = "test"
            else:
                detected_env = "prod"
    return detected_env


def is_prod_env():
    """
    Returns boolean indicating whether local_env is "prod"
    """
    return local_env() == "prod"


def is_test_env():
    """
    Returns boolean indicating whether local_env is "test"
    """
    return local_env() == "test"


def is_dev_env():
    """
    Returns boolean indicating whether local_env is "dev"
    """
    return local_env() == "dev"


def apps_url(hostname: str = None) -> str:
    """Returns environment aware apps url

    Args:
        hostname (str, optional): If provided, adds `{hostname}.` to the base url. Defaults to None.

    Returns:
        str: The enviornment aware apps url such as `apps-test.mst.edu` or `https://{hostname}.apps-test.mst.edu`
    """
    env = local_env()
    prefix = f"https://{hostname}." if hostname else ""
    return f"{prefix}apps-{env}.mst.edu" if env in ["dev", "test"] else f"{prefix}apps.mst.edu"
