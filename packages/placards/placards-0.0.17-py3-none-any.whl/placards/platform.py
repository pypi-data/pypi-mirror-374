import re
import os
import shlex
import shutil
import socket
import logging
import random
import subprocess


VNC_TIMEOUT = 30
PORT_PATTERN = re.compile(b'PORT=(\\d+)')
REBOOT = 'shutdown -r +%s'

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def file_path(s):
    if os.path.isfile(s):
        return s
    else:
        raise FileNotFoundError(s)


def dir_path(s):
    if os.path.isdir(s):
        return s
    else:
        raise NotADirectoryError(s)


def bin_path(s):
    file_path(s)
    if os.access(s, os.X_OK):
        return s
    else:
        raise PermissionError(s)


def get_addr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 1))

    except Exception:
        pass

    return s.getsockname()[0]


def run_command(command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **kwargs):
    cmd = shlex.split(command)
    bin = shutil.which(cmd[0])
    if not bin:
        LOGGER.warning('Could not find program %s', cmd[0])
        return
    return subprocess.Popen(
        [bin, *cmd[1:]],
        stdout=stdout,
        stderr=stderr,
        **kwargs,
    )


def run_x11vnc():
    'Run x11vnc and retrieve port'
    p = run_command(
        f'x11vnc -q -timeout {VNC_TIMEOUT}', stdout=subprocess.PIPE)

    if not p or p.poll():
        raise subprocess.CalledProcessError('Process died')

    try:
        line = p.stdout.readline()
        LOGGER.error('Process out: %s', line)
        m = PORT_PATTERN.match(line)
        LOGGER.error('Match: %s', m)
        return int(m.groups()[0])

    except (AttributeError, IndexError) as e:
        raise ValueError('Could not determine x11vnc port: %s', e.args[0])


def get_hostname():
    return socket.gethostname()


def reboot():
    # NOTE: Use a random delay to avoid a dogpile.
    delay = random.randint(1, 10)
    command = REBOOT % delay
    p = run_command(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    LOGGER.debug('Reboot out: %s, err: %s', out, err)
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, command, err)
