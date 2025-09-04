import subprocess
from loguru import logger as log
import os


import subprocess

from loguru import logger as log


def run_command(args, env=None, name=None):
    """Run the command defined by args and return its output and return code.

    :param args: List of arguments for the command to be run.
    :param env: Dict defining the environment variables. Pass None to use
        the current environment.
    :param name: User-friendly name for the command being run. A value of
        None will cause args[0] to be used.
    :param logger: Logger object for logging errors. If None, the default logger is used.
    :return: Tuple containing the command's output and return code.
    """

    if name is None:
        name = args[0]

    try:
        output = subprocess.check_output(args, stderr=subprocess.STDOUT, env=env)
        return_code = 0
        if isinstance(output, bytes):
            output = output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        output = e.output.decode("utf-8") if isinstance(e.output, bytes) else e.output
        return_code = e.returncode
        message = "%s failed with return code %d: %s" % (name, return_code, output)
        log.error(message)
        raise RuntimeError(message)

    return output, return_code


def create_dir(path: str):
    """
    Create directory if not exists
    """
    if not os.path.exists(path):
        run_command(["sudo", "mkdir", "-p", path])


def print_run_command(args):
    """debug testing of run_command"""

    print(args)
    print(run_command(args))
