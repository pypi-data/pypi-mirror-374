
from typing import List

from logging import Logger
from logging import getLogger


from configparser import BasicInterpolation


class PassThroughInterpolation(BasicInterpolation):
    """
    This class allows the developer to provide a list of options
    to ignore.  Then the developer passes this to the DynamicConfiguration
    constructor

    This one just passes through values for specific options
    """
    def __init__(self, passThroughOptions: List[str]):

        self.logger: Logger = getLogger(__name__)

        self._passThroughOptions: List[str] = passThroughOptions

    def before_get(self, parser, section, option, value, defaults):

        if option in  self._passThroughOptions:
            return value
        return super().before_get(parser, section, option, value, defaults)

    def before_set(self, parser, section, option, value):
        if option in  self._passThroughOptions:
            return value

        return super().before_set(parser, section, option, value)

    def before_read(self, parser, section, option, value):
        return super().before_read(parser, section, option, value)

    def before_write(self, parser, section, option, value):
        return super().before_write(parser, section, option, value)
