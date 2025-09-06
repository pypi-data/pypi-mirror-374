

class SecureConversions:
    """
    Assures that you get a valid expected answer back; During development
    mode with assertions turned on, the code will reject nonsensical values.
    This is as opposed to the original version of these that always returned
    some value even for nonsensical values.

    I hate side effects, They hide bugs
    """
    def __init__(self):
        pass

    @classmethod
    def strFloatToInt(cls, floatValue: str) -> int:
        """
        For nonsensical values will fail during development with assertions turned on

        Args:
            floatValue:

        Returns: An integer value
        """
        assert floatValue is not None, 'Cannot be None'
        assert floatValue != '', 'Cannot be empty string'
        assert floatValue.replace('.', '', 1).isdigit(), 'String must be numeric'

        integerValue: int = int(float(floatValue))

        return integerValue

    @classmethod
    def secureInteger(cls, integerValue: str):
        """
        For nonsensical values will fail during development with assertions turned on

        Args:
            integerValue:

        Returns: The integer value for the input string
        """
        assert integerValue is not None, 'Cannot be None'
        assert integerValue != '', 'Cannot convert an empty string'

        return int(integerValue)

    @classmethod
    def secureBoolean(cls, booleanValue: str):
        """
        For nonsensical values will fail during development with assertions turned on

        Args:
            booleanValue: Input string

        Returns: Either boolean true or false

        """
        assert booleanValue is not None, 'Cannot convert None value to boolean'

        if booleanValue in [True, "True", "true", 1, "1"]:
            return True

        return False

    @classmethod
    def secureFloat(cls, possibleFloatStr: str) -> float:
        """
        For nonsensical values will fail during development with assertions turned on

        Args:
            possibleFloatStr:

        Returns: Float value of string

        """

        assert possibleFloatStr is not None, 'Cannot convert None value to float'

        return float(possibleFloatStr)

    @classmethod
    def secureString(cls, possibleString: str) -> str:
        """

        Args:
            possibleString:  the string to validate

        Returns: the same string, if string = None, return an empty string.
        """

        if possibleString is None:
            possibleString = ''
        return possibleString
