
from logging import Logger
from logging import getLogger

from importlib.resources.abc import Traversable
from importlib.resources import files

from pathlib import Path


class ResourceManager:
    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    @classmethod
    def retrieveResourcePath(cls, bareFileName: str, resourcePath: str, packageName: str) -> str:
        """
        Assume we are in an app;  If not, then we are in development
        Args:
            bareFileName:  Simple filename
            resourcePath:  OS Path that matches the package name
            packageName:   The package from which to retrieve the resource

        Returns:  The fully qualified filename
        """
        fqPath: Path = cls.computeResourcePath(resourcePath=resourcePath, packageName=packageName) / Path(bareFileName)
        return str(fqPath)

    @classmethod
    def computeResourcePath(cls, resourcePath: str, packageName: str) -> Path:
        """
        Computes just the bare resource path
        Assume we are in an app;  If not, then we are in development
        Args:
            resourcePath:  OS Path that matches the package name
            packageName:   The package from which to retrieve the resource

        Returns:  The fully qualified path
        """
        try:
            from os import environ
            pathToResources: str  = environ[f'{ResourceManager.RESOURCE_ENV_VAR}']
            fqPath:      Path = Path(f'{pathToResources}/{resourcePath}/')
        except KeyError:
            traversable: Traversable = files(packageName)
            fqPath = Path(str(traversable))

        return fqPath
