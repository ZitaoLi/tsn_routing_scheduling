import abc


class NetworkDeviceFactoryInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def product(self, unique_id: int):
        pass
