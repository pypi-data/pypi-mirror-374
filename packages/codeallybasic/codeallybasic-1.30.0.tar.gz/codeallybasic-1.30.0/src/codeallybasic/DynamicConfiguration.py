
from typing import Optional
from typing import Callable
from typing import Dict
from typing import List
from typing import cast
from typing import NewType
from typing import Any

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from configparser import ConfigParser
from configparser import Interpolation

from pathlib import Path

from codeallybasic.ConfigurationLocator import ConfigurationLocator

PROTECTED_PROPERTY_INDICATOR: str = '_'
PRIVATE_PROPERTY_INDICATOR:   str = '__'

KeyName      = NewType('KeyName', str)
SectionName  = NewType('SectionName', str)


Deserializer = Callable[[str], Any]
StringList   = NewType('StringList', List[str])


@dataclass
class ValueDescription:
    """
    When specifying an enumeration only one of enumUseValue or enumUseName can be True
    """

    defaultValue: Any          = None
    deserializer: Deserializer = cast(Deserializer, None)
    enumUseValue: bool         = False      # Set to True if you want to use the enum value; Use constructor to deserialize
    enumUseName:  bool         = False      # Set to True if you want to use the enum name;  Create deserialize method
    isStringList: bool         = False      # Set to True to get free serialization and deserialization


ValueDescriptions = NewType('ValueDescriptions', Dict[KeyName,     ValueDescription])
Sections          = NewType('Sections',          Dict[SectionName, ValueDescriptions])


@dataclass
class LookupResult:
    sectionName:    SectionName      = cast(SectionName, None)
    keyDescription: ValueDescription = cast(ValueDescription, None)


class UnDefinedValueDescription(Exception):
    pass


class DynamicConfiguration:
    """
    This class allows developers to create configuration/preference class w/o
    all the boiler plate code of property getter/setter for each configuration
    value

    It uses Python's ConfigParser as the backing for the values

    """
    def __init__(self, moduleName: str, baseFileName: str, sections: Sections, interpolation: Optional[Interpolation] = None):
        """

        Args:
            moduleName:     The component's module name
            baseFileName:   The base filename including the file extension
            sections:       The property descriptions mapped to their appropriate section
        """

        self._logger:   Logger   = getLogger(__name__)
        self._sections: Sections = sections

        locator: ConfigurationLocator = ConfigurationLocator()

        self._fqFileName:   Path         = locator.applicationPath(f'{moduleName}') / baseFileName
        if interpolation is None:
            self._configParser: ConfigParser = ConfigParser()
        else:
            self._configParser = ConfigParser(interpolation=interpolation)

        self._configParser.optionxform = self._toStr    # type: ignore
        self._loadConfiguration()

    def __getattr__(self, attrName: str) -> Any:
        """
        Does the work of retrieving the named attribute from the configuration parser

        Args:
            attrName:

        Returns:  The correctly typed value
        """

        self._logger.debug(f'{attrName}')

        configParser:     ConfigParser     = self._configParser
        result:           LookupResult     = self._lookupKey(searchKeyName=KeyName(attrName))
        valueDescription: ValueDescription = result.keyDescription

        valueStr: str = configParser.get(result.sectionName, attrName)

        if valueDescription.deserializer is not None:
            value: Any = valueDescription.deserializer(valueStr)
        else:
            if valueDescription.isStringList is True:
                value = DynamicConfiguration.stringToStringList(valueStr)
            else:
                value = valueStr

        return value

    def __setattr__(self, key: str, value: Any):
        """
        Do the work of writing this back to the configuration/settings/preferences file
        Ignores protected and private variables uses by this class

        Does a "write through" to the backing configuration file (.ini)

        Args:
            key:    The property name
            value:  Its new value
        """

        if key.startswith(PROTECTED_PROPERTY_INDICATOR) or key.startswith(PRIVATE_PROPERTY_INDICATOR):
            super(DynamicConfiguration, self).__setattr__(key, value)
        else:
            self._logger.debug(f'Writing `{key}` with `{value}` to configuration file')

            configParser:     ConfigParser     = self._configParser
            result:           LookupResult     = self._lookupKey(searchKeyName=KeyName(key))
            valueDescription: ValueDescription = result.keyDescription

            if valueDescription.enumUseValue is True:
                valueStr: str = value.value
                configParser.set(result.sectionName, key, valueStr)
            elif valueDescription.enumUseName is True:
                configParser.set(result.sectionName, key, value.name)
            elif isinstance(value, list) is True:
                configParser.set(result.sectionName, key, DynamicConfiguration.stringListToString(StringList(value)))
            else:
                configParser.set(result.sectionName, key, str(value))

            self.saveConfiguration()

    @classmethod
    def stringToStringList(cls, string: str, delimiter: str = ',') -> StringList:
        """

        Args:
            string:   The value that needs converting
            delimiter:  The delimiter separating the strings

        Returns:  A StringList
        """
        return StringList(string.split(sep=delimiter))

    @classmethod
    def stringListToString(cls, stringList: StringList, delimiter: str = ',') -> str:
        """

        Args:
            stringList:  The string list
            delimiter:   Character to use as delimiter

        Returns:  A string delimited by the delimiter
        """
        return f'{delimiter}'.join(stringList)

    def saveConfiguration(self):
        """
        Save data to the configuration file
        """
        with self._fqFileName.open(mode='w') as fd:
            # fd = cast(SupportsWrite, fd)
            # noinspection PyTypeChecker
            self._configParser.write(fd)

    def _loadConfiguration(self):

        self._ensureConfigurationFileExists()
        # Read data
        self._configParser.read(self._fqFileName)
        self._addMissingSections()
        self._addMissingKeys()

    def _ensureConfigurationFileExists(self):

        fileName: Path = self._fqFileName
        if fileName.exists() is False:
            with fileName.open(mode='w') as fd:
                fd.write('')
            self._logger.warning(f'Empty Configuration file created')

    def _addMissingSections(self):

        for sectionName in self._sections.keys():
            if self._configParser.has_section(sectionName) is False:
                self._configParser.add_section(sectionName)
                self.saveConfiguration()

    def _addMissingKeys(self):

        for sectionName in self._sections.keys():
            propertyDescriptions: ValueDescriptions = self._sections[sectionName]

            for propName in propertyDescriptions.keys():

                desc: ValueDescription = propertyDescriptions[propName]
                self._logger.debug(f'{desc=}')
                if self._configParser.has_option(sectionName, propName) is False:
                    self._addMissingKey(sectionName=sectionName, preferenceName=propName, value=desc.defaultValue)

    def _addMissingKey(self, sectionName: str, preferenceName: str, value: str | StringList):

        if isinstance(value, list):
            strValue: str = DynamicConfiguration.stringListToString(value)
            self._configParser.set(sectionName, preferenceName, strValue)
        else:
            self._configParser.set(sectionName, preferenceName, value)

        self.saveConfiguration()

    def _lookupKey(self, searchKeyName: KeyName) -> LookupResult:
        """
        Loop through the sections, but uses the searchKeyName to try
        and index into the value description dictionary

        Args:
            searchKeyName:

        Returns:  LookupResult

        Raises: UnDefinedValueDescription if the configuration property is not defined
        """

        lookupResult: LookupResult = LookupResult()

        for sectionName in self._sections.keys():
            keyDescriptions: ValueDescriptions = self._sections[sectionName]
            try:
                lookupResult.keyDescription = keyDescriptions[searchKeyName]
                lookupResult.sectionName    = sectionName
                break
            except KeyError:
                continue        # Go to next Section

        # sectionName is not set if we never found a key (actually neither value set)
        if lookupResult.sectionName is None:
            raise UnDefinedValueDescription()

        return lookupResult

    def _toStr(self, optionString: str) -> str:
        """
        Override base method

        Args:
            optionString:

        Returns: The option string unchanged
        """
        return optionString
