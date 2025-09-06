
from re import sub as regExSub

from deprecated import deprecated

#
# https://www.codetable.net/hex/a
#
XML_END_OF_LINE_MARKER: str = '&#xA;'

@deprecated(version='1.15.0', reason='Use the class method in Basic')
def cmp(left, right) -> int:
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


@deprecated(version='1.15.0', reason='Use the class method in Basic')
def apply(callback, args=None, kwargs=None):
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


@deprecated(version='1.15.0', reason='Use the class method in Basic')
def fixURL(oldURL: str) -> str:
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
