import functools
import os
import sys


def process_output(success_code=0, fail_code=-1, exceptions=(BaseException,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cmd = ' '.join(sys.argv[1:])
            stdout = ""
            stderr = ""
            try:
                func(*args, **kwargs)
                return_code = success_code
                stdout = f"run cmd: {cmd} successfully.{os.linesep}"
            except KeyboardInterrupt:  # handle KeyboardInterrupt
                return_code = fail_code
                stderr = f"User interrupted the program by Keyboard.{os.linesep}"
            except SystemExit as e:
                if e.code == 0:
                    return_code = success_code
                    stdout = f"run cmd: {cmd} successfully.{os.linesep}"
                else:
                    return_code = fail_code
                    stderr = f"run cmd: {cmd} failed, reason: {str(e)}.{os.linesep}"
            except exceptions as e:
                return_code = fail_code
                stderr = f"run cmd: {cmd} failed, reason: {str(e)}.{os.linesep}"
            return return_code, stdout, stderr

        return wrapper

    return decorator
