
from typing import Callable

from logging import Logger
from logging import getLogger

# from subprocess import CompletedProcess
# from subprocess import run as subProcessRun

from os import chdir

from os import environ as osEnvironment
from os import sep as osSep


PrintCallback  = Callable[[str], None]


class Environment:
    """

    """
    ENV_PROJECTS_BASE: str = 'PROJECTS_BASE'
    ENV_PROJECT:       str = 'PROJECT'

    def __init__(self, printCallback: PrintCallback):

        self.ebLogger: Logger = getLogger(__name__)

        self._projectsBase:     str = ''
        self._projectDirectory: str = ''

        try:
            self._projectsBase = osEnvironment[Environment.ENV_PROJECTS_BASE]
        except KeyError:
            self.ebLogger.info(f'Project Base not set')
        try:
            self._projectDirectory = osEnvironment[Environment.ENV_PROJECT]
        except KeyError:
            self.ebLogger.info(f'Project Directory not set')

        printCallback(f'projects_base={self._projectsBase}')
        printCallback(f'project={self._projectDirectory}')
        printCallback('')

    @property
    def projectsBase(self) -> str:
        return self._projectsBase

    @property
    def projectDirectory(self) -> str:
        return self._projectDirectory

    @property
    def validProjectsBase(self) -> bool:
        if self._projectsBase == '':
            return False
        else:
            return True

    def validProjectDirectory(self) -> bool:
        if self._projectDirectory == '':
            return False
        else:
            return True

    # def _runCommand(self,  command: str) -> int:
    #
    #     cp: CompletedProcess = subProcessRun([command], shell=True, capture_output=False, text=True, check=False)
    #
    #     return cp.returncode

    def _changeToProjectRoot(self):

        fullPath: str = f'{self._projectsBase}{osSep}{self._projectDirectory}'
        chdir(fullPath)
