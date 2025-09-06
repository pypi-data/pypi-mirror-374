
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from functools import wraps

from configparser import ConfigParser

from pathlib import Path

from deprecated import deprecated

from codeallybasic.ConfigurationLocator import ConfigurationLocator


def configurationSetter(sectionName: str, isEnum: bool = False, enumUseName: bool = False):

    def decoratorConfigurationSetter(func):
        @wraps(func)
        def setWrapper(*args, **kwargs):
            """
            Wrapper function
            """
            baseConfiguration: ConfigurationProperties = args[0]
            configParser: ConfigParser = baseConfiguration.configurationParser

            if isEnum is True:
                configParser.set(sectionName, f'{func.__name__}', args[1].value)
            elif enumUseName is True:
                configParser.set(sectionName, f'{func.__name__}', args[1].name)
            else:
                configParser.set(sectionName, f'{func.__name__}', str(args[1]))
            baseConfiguration.saveConfiguration()

            value = func(*args, **kwargs)
            # print(f'Do something after')
            return value

        return setWrapper
    return decoratorConfigurationSetter


DeSerializeFunction = Callable[[str], Any]
"""
Function that takes a string and does a custom deserialization
"""

NO_DESERIALIZE_FUNCTION: DeSerializeFunction = cast(DeSerializeFunction, None)


def configurationGetter(sectionName: str, deserializeFunction: DeSerializeFunction = NO_DESERIALIZE_FUNCTION):
    """

    Args:
        sectionName:            Section to get our value from
        deserializeFunction:    If this value is `None`, we  use str();
                                If you supply this method,
                                it is imperative that the underlying object implement a .__repr__()
                                that is consumable by the de-Serialize function

    Returns:  Nothing we return our own value
    """

    def decoratorConfigurationGetter(func):

        # noinspection PyUnusedLocal
        @wraps(func)
        def getWrapper(*args, **kwargs):
            """
            Wrapper function
            """
            baseConfiguration: ConfigurationProperties = args[0]
            configParser:      ConfigParser            = baseConfiguration.configurationParser

            value = configParser.get(sectionName, f'{func.__name__}')

            if deserializeFunction is not None:
                value = deserializeFunction(value)
            #  value = func(*args, **kwargs)   do not bother calling original

            return value
        return getWrapper
    return decoratorConfigurationGetter


@dataclass
class ConfigurationNameValue:

    name:                str = ''
    defaultValue:        Any = None


PropertyName = NewType('PropertyName', str)
SectionName  = NewType('SectionName', str)

Section  = NewType('Section',  List[ConfigurationNameValue])
Sections = NewType('Sections', Dict[SectionName, Section])


@deprecated(reason='Use DynamicConfiguration')
class ConfigurationProperties:
    """
    This is the base class for component configuration.
    """
    def __init__(self, moduleName: str, baseFileName, sections: Sections):
        """
        The subclassing component is responsible for calling self._loadConfiguration();
        This is, so it can potentially modify the ConfigParser behavior

        Args:
            moduleName:     The component's module name
            baseFileName:   The base filename including the file extension
            sections:       A dictionary sections that divide the various component configuration properties
        """

        self.logger: Logger = getLogger(__name__)

        locator: ConfigurationLocator = ConfigurationLocator()

        self._fqFileName:   Path         = locator.applicationPath(f'{moduleName}') / baseFileName
        self._configParser: ConfigParser = ConfigParser()

        self._sections: Sections = sections

    @property
    def configurationParser(self) -> ConfigParser:
        return self._configParser

    @property
    def fileName(self) -> Path:
        return self._fqFileName

    def saveConfiguration(self):
        """
        Save data to the configuration file
        """
        with self._fqFileName.open(mode='w') as fd:
            # noinspection PyTypeChecker
            self._configParser.write(fd)

    def _loadConfiguration(self):

        self._ensureConfigurationFileExists()
        # Read data
        self._configParser.read(self._fqFileName)
        self._addMissingSections()
        self._addMissingPreferences()

    def _ensureConfigurationFileExists(self):

        fileName: Path = self._fqFileName
        if fileName.exists() is False:
            with fileName.open(mode='w') as fd:
                fd.write('')
            self.logger.warning(f'Empty Configuration file created')

    def _addMissingSections(self):

        for sectionName in self._sections:
            if self._configParser.has_section(sectionName) is False:
                self._configParser.add_section(sectionName)
                self.saveConfiguration()

    def _addMissingPreferences(self):

        for sectionName in self._sections:
            section: Section = self._sections[sectionName]
            for c in section:
                cfgNameValue: ConfigurationNameValue = cast(ConfigurationNameValue, c)
                self.logger.debug(f'{cfgNameValue=}')
                if self._configParser.has_option(sectionName, cfgNameValue.name) is False:
                    self._addMissingPreference(sectionName=sectionName, preferenceName=cfgNameValue.name, value=cfgNameValue.defaultValue)

    def _addMissingPreference(self, sectionName: str, preferenceName: str, value: str):
        self._configParser.set(sectionName, preferenceName, value)
        self.saveConfiguration()
