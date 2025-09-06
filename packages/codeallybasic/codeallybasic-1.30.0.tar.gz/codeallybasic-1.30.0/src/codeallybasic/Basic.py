from dataclasses import dataclass
from logging import Logger
from logging import getLogger

from pathlib import Path

from re import sub as regExSub
from subprocess import CompletedProcess
from subprocess import run as subProcessRun

@dataclass
class RunResult:
    returnCode: int = 0
    stdout:     str = ''
    stderr:     str = ''

class Basic:
    """
    Basic methods.  All are class methods
    """
    #
    # https://www.codetable.net/hex/a
    #
    XML_END_OF_LINE_MARKER: str = '&#xA;'

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    @classmethod
    def cmp(cls, left, right):
        """
        Python 2 stand in

        Args:
            left:
            right:

        Returns:
            -1 if left < right

            0 if left = right

            1 if left > right
        """
        return (left > right) - (left < right)

    @classmethod
    def apply(cls, callback, args=None, kwargs=None):
        """
        Python 2 stand in

        Stolen from:  https://github.com/stefanholek/apply

        Call a callable object with positional arguments taken from the
        tuple args, and keyword arguments taken from the optional dictionary
        kwargs; return its results.
        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        return callback(*args, **kwargs)

    @classmethod
    def fixURL(cls, oldURL: str) -> str:
        """
        Makes the URLs returned by the GitHub API actually user linkable when I
        generate the markdown file.

        e.g.

        https://api.github.com/repos/hasii2011/code-ally-advanced

        gets turned into

        https://github.com//hasii2011/code-ally-advanced

        Args:
            oldURL:  The URL we have to fix

        Returns:  A linkable URL
        """

        apiStrip:  str = regExSub(pattern=r'api.',   repl='', string=oldURL)
        repoStrip: str = regExSub(pattern=r'repos/', repl='', string=apiStrip)

        return repoStrip

    @classmethod
    def deleteDirectory(cls, path: Path):
        """
        Danger, Danger;  Make sure you want to delete everything in
        every subdirectory

        Args:
            path:  The top of the directory tree to delete
        """
        for item in path.iterdir():
            if item.is_dir():
                cls.deleteDirectory(item)
            else:
                item.unlink()
        path.rmdir()  # Remove the directory itself

    @classmethod
    def runCommand(cls, programToRun: str) -> RunResult:
        """
        Will always
            * capture the output
            * runs shell=True
            * text=True
            * check=False; So no exception generated on failure
        Args:
            programToRun:  What must be executed

        Returns:  The command run results
        """
        completedProcess: CompletedProcess = subProcessRun([programToRun], shell=True, capture_output=True, text=True, check=False)
        return RunResult(
            returnCode=completedProcess.returncode,
            stderr=completedProcess.stderr,
            stdout=completedProcess.stdout
        )
