import abc


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


# use __new__()
class SingletonNewMethod(object):
    _instance = None

    # __new()__ is the real constructor function
    # __init()__ only use to initialize variables
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(SingletonNewMethod, cls).__new__(cls, *args, **kw)
        return cls._instance


# use __new__() improved
class SingletonNewMethodImproved(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance'):
            print('in new')
            cls.__instance = object.__new__(cls, *args, **kwargs)
            cls.__instance.__Singleton_Init__(*args, **kwargs)
        return cls.__instance

    def __Singleton_Init__(self):
        print("__Singleton_Init__")


# using metaclass
class SingletonMetaclass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMetaclass, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# use metaclass inheriting abc.ABCMeta
class SingletonMetaclassABC(type, abc.ABC):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMetaclassABC, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonABC(abc.ABCMeta, SingletonMetaclass):
    pass
