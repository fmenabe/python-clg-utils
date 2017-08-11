# coding: utf-8

import re
import sys
import time
import inspect
import clg.logger as logger

class Print:
    @staticmethod
    def log(msg, loglevel, **kwargs):
        """Log ``msg`` message with ``loglevel`` verbosity.

        `**kwargs` can contains:

            * *quit*: force exit of the program,
            * *return_code*: return_code to use in case of exit,
            * *confidential*: don't log on the file logger (allows to log password
              on console)
        """
        quit = kwargs.get('quit', False)
        return_code = kwargs.get('return_code', 0)
        confidential = kwargs.get('confidential', False)
        print(msg)
        if quit:
            sys.exit(return_code)

    @staticmethod
    def verbose(msg, **kwargs):
        """Verbose messages."""
        Print.log(
            msg, 'verbose',
            quit=kwargs.get('quit', False),
            return_code=kwargs.get('return_code', 0),
            confidential=kwargs.get('confidential', False))

    @staticmethod
    def debug(msg, **kwargs):
        """Debug messages."""
        Print.log(
            msg, 'debug',
            quit=kwargs.get('quit', False),
            return_code=kwargs.get('return_code', 0),
            confidential=kwargs.get('confidential', False))

    @staticmethod
    def info(msg, **kwargs):
        """Info messages."""
        Print.log(
            msg, 'info',
            quit=kwargs.get('quit', False),
            return_code=kwargs.get('return_code', 0),
            confidential=kwargs.get('confidential', False))

    @staticmethod
    def warn(msg, **kwargs):
        """Warning messages."""
        Print.log(
            msg, 'warn',
            quit=kwargs.get('quit', False),
            return_code=kwargs.get('return_code', 0),
            confidential=kwargs.get('confidential', False))

    @staticmethod
    def error(msg, **kwargs):
        """Error message."""
        Print.log(
            msg, 'error',
            quit=kwargs.get('quit', False),
            return_code=kwargs.get('return_code', 1),
            confidential=kwargs.get('confidential', False))


def ask(message='Continue?',
        negative_answer='command aborted',
        warning=None, force=False, timeout=3, event_hdl=Print):
    if warning is not None:
        event_hdl.warn(warning)

    if not force:
        response = ' '
        while response.lower() not in ('', 'y', 'n'):
            response = input('{:s} [y/N]'.format(message))
            if response.lower() in ('', 'n'):
                event_hdl.info(negative_answer, quit=True)
    else:
        try:
            event_hdl.info("You have {:d} seconds to abort ('Ctrl+c')".format(timeout))
            time.sleep(timeout)
        except KeyboardInterrupt:
            event_hdl.info(negative_answer, quit=True)

def catch(msg, cmd, exceptions, event_hdl=logger, loglevel='info', feedback=False, **kwargs):
    """Utility function that execute the command `cmd` by preceding it by the
    informational message `msg` printed using the event handler `event_hdl`
    (of type clg.logger, clg.spinner, ...) with the `loglevel` log level.

    If an error occur, the event handler log a message with the *error* loglevel
    and `**kwargs` values for the event handler parameters (``quit=True`` for example
    for leaving the program).

    The `feedback` parameter define whether a confirmation is logged or not.
    """
    getattr(event_hdl, loglevel)(msg)
    try:
        result = cmd()
        if feedback:
            getattr(event_hdl, loglevel)('{:s} done'.format(msg))
        return result
    except exceptions as err:
        event_hdl.error('{:s} failed: {:s}'.format(msg, str(err)), **kwargs)


def execute(msg, cmd, quit=True, show_warnings=True, event_hdl=logger):
    logger.info(msg)
    func_code = re.sub('\n\s*', ' ', inspect.getsource(cmd).strip())
    logger.debug(func_code)
    status, stdout, stderr = cmd()
    logger.verbose('\nstatus: {:b}\nstdout: {:s}\nstderr: {:s}'
                    .format(status, stdout.strip(), stderr.strip()))
    if not status:
        event_hdl.error('{:s} failed: {:s}'.format(msg, stdout + stderr), quit=quit)
    elif show_warnings and stderr:
        event_hdl.warn(stderr)
    return stdout

