import abc


class NetworkFactoryInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def product(self, *args, **kwargs):
        pass
