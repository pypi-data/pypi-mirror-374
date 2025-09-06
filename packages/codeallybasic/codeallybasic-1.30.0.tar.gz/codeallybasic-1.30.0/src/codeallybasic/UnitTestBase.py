from logging import getLogger
from typing import cast

from logging import Logger
import logging.config

import json

from importlib.resources.abc import Traversable
from importlib.resources import files

from unittest import TestCase

JSON_LOGGING_CONFIG_FILENAME: str = "testLoggingConfiguration.json"
TEST_DIRECTORY:               str = 'tests'


class UnitTestBase(TestCase):
    """
    This is a copy of the one in the export package

    A base unit test class to initialize some logging stuff we need
    Opinionated with respect to
        * the test package name
        * the logging
            * configuration name
            * and format
    """

    RESOURCES_PACKAGE_NAME:  str = 'tests.resources'

    clsLogger: Logger = cast(Logger, None)

    @classmethod
    def setUpClass(cls):
        """
        Hook method for setting up class fixture before running tests in the class.
        """
        cls.setUpLogging()
        cls.clsLogger = getLogger(__name__)

    @classmethod
    def tearDownClass(cls):
        """
        Hook method for deconstructing the class fixture after running all tests in the class.
        """
        pass

    def setUp(self):
        self.logger: Logger = self.clsLogger

    def tearDown(self):
        pass

    @classmethod
    def setUpLogging(cls):
        """
        """
        loggingConfigFilename: str = cls.getLoggingConfigurationFileName()

        with open(loggingConfigFilename, 'r') as loggingConfigurationFile:
            configurationDictionary = json.load(loggingConfigurationFile)

        logging.config.dictConfig(configurationDictionary)
        logging.logProcesses = False
        logging.logThreads = False

    @classmethod
    def getLoggingConfigurationFileName(cls) -> str:

        fqFileName: str = cls.getFullyQualifiedResourceFileName(cls.RESOURCES_PACKAGE_NAME, fileName=JSON_LOGGING_CONFIG_FILENAME)
        return fqFileName

    @classmethod
    def getFullyQualifiedResourceFileName(cls, package: str, fileName: str) -> str:
        """
        Use this method to get other unit test resources
        Args:
            package: The fully qualified package name (dot notation)
            fileName: The resource's file name

        Returns: A fully qualified path name
        """

        traversable: Traversable = files(package) / fileName

        return str(traversable)
