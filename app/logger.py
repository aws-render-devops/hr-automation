import logging
from functools import wraps
from types import MethodType


class Logged:
    """
    Decorator that should log when method starts, ends and in case it fails.
    Can be used with functions, methods and coros.
    If you need to change log message, please inherit from it.
    """

    _logger = logging.getLogger("default")
    _level = logging.INFO

    def __init__(self, func):
        wraps(func)(self)

    async def wrapper(self, *args, **kwargs):
        self.log(self.get_msg("Started"))
        try:
            res = await self.__wrapped__(*args, **kwargs)
        except Exception as e:
            self._logger.exception(e)
            raise
        self.log(self.get_msg("Finished"))
        return res

    def __await__(self, *args, **kwargs):
        return self.wrapper(*args, **kwargs).__await__()

    def __call__(self, *args, **kwargs):
        self.log(self.get_msg("Started"))
        try:
            res = self.__wrapped__(*args, **kwargs)
        except Exception as e:
            self._logger.exception(e)
            raise
        self.log(self.get_msg("Finished"))
        return res

    def __get__(self, instance, cls):
        if not instance:
            return self
        else:
            return MethodType(self, instance)

    def log(self, level=None, msg=None):
        level, msg = (level, msg) if msg else (self._level, level)
        self._logger.log(level, msg)

    def get_msg(self, msg=""):
        msg = f"{self.__qualname__}: {msg}"
        return msg
