

class SingletonV3(type):
    """
    https://stackoverflow.com/questions/51896862/how-to-create-singleton-class-with-arguments-in-python
    """
    _instances = {}  # type: ignore

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonV3, cls).__call__(*args, **kwargs)

        return cls._instances[cls]
