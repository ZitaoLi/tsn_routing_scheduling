# use function decorator
def singleton_decorator(cls):
    from functools import wraps
    _instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    return get_instance


# use decorator class
# TODO this decorator cannot be inherited
class SingletonDecorator(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self, *args, **kwargs):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls(*args, **kwargs)
        return self._instance[self._cls]


# use __new()__
class SingletonNewMethod(object):
    _instance = None

    # __new()__ is the real constructor function
    # __init()__ only use to initialize variables
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(SingletonNewMethod, cls).__new__(cls, *args, **kw)
        return cls._instance


# using metaclass
class SingletonMetaclass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMetaclass, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
