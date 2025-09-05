"""
usage_logger

track usage of apis and scripts in mstpylib/python portfolio

"""

import sys
import socket
import os
import inspect
import re
import getpass
import urllib.parse
import ttl_cache

IGNORE = False
DEFAULT_TTL = 5
skip_decorators = [("ttl_cache.py", "fn_wrapped")]
server = None
usage_logger_script = None
usage_logger_owner = None
usage_logger_type = None
usage_socket = None
last_socket_pid = None
server_ip = None
server_port = 2407


def LogAPIUsage(msg=None):
    """Collects execution data and sends udp packet to apiusage-feed.srv.mst.edu

    Args:
        msg (str): message for logging. Defaults to None.
    """
    global server, usage_logger_script, usage_logger_owner, usage_logger_type
    # allow application request that we not log anything
    if IGNORE:
        return

    stack = inspect.stack()[1:]
    _, func_file, _, func_name, *_ = stack[0]

    # drill down the stack trace and skip any marked decorators
    for frame in stack[1:]:
        _, caller_file, _, caller_name, *_ = frame
        if (os.path.basename(caller_file), caller_name) not in skip_decorators:
            break

    if server is None:
        server = socket.gethostname()

    authuser = None
    cwd = os.getcwd()

    if "flask" in sys.modules:
        try:
            request = sys.modules["flask"].request
            if getattr(sys.modules["flask"].g, "user", None):
                authuser = sys.modules["flask"].g.user["username"]
            server = request.host
        except RuntimeError:
            # not within a flask request, nothing to do here
            authuser = None

    if usage_logger_script is None:
        usage_logger_script = sys.argv[0]

    if usage_logger_owner is None:
        if m := re.search(r"^/local/(.*?)/", usage_logger_script):
            usage_logger_owner = m[1]

    if usage_logger_type is None:
        if "VSCODE_IPC_HOOK_CLI" in os.environ:
            usage_logger_type = "vscode"
        elif "flask" in sys.modules:
            usage_logger_type = "flask"
        elif "PS1" in os.environ:
            usage_logger_type = "shell"
        else:
            usage_logger_type = "unknown"

    _SendUsagePacket(
        msg=msg,
        user=getpass.getuser(),
        script=usage_logger_script,
        scriptowner=usage_logger_owner,
        cwd=cwd,
        authuser=authuser,
        server=server,
        function=func_name,
        function_file=func_file,
        caller=caller_name,
        caller_file=caller_file,
        language="python",
        type=usage_logger_type,
    )


@ttl_cache(DEFAULT_TTL)
def _SendUsagePacket(**kwargs):
    """urlencodes delivery packet and sends data over udp to apiusage-feed.srv.mst.edu"""
    global usage_socket, last_socket_pid, server_ip, server_port

    parts = []
    for key, value in kwargs.items():
        k = urllib.parse.quote(key, safe="")
        if value is not None:
            v = urllib.parse.quote(value, safe="")
            parts.append(f"{k}={v}")
    data = "&".join(parts).encode("utf-8")

    if last_socket_pid != os.getpid():
        usage_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM | socket.SOCK_NONBLOCK)

    if server_ip is None:
        server_ip = socket.gethostbyname("apiusage-feed.srv.mst.edu")

    usage_socket.sendto(data, (server_ip, server_port))
