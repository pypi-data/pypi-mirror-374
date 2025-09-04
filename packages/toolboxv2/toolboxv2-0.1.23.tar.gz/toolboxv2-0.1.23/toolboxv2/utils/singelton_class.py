class Singleton(type):
    """
    Singleton metaclass for ensuring only one instance of a class.
    """

    _instances = {}
    _kwargs = {}
    _args = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
            cls._args[cls] = args
            cls._kwargs[cls] = kwargs
        return cls._instances[cls]
