import abc

from src.net_elem.NetworkDevice import NetworkDevice
from src.utils.Singleton import SingletonDecorator


@SingletonDecorator
class NetworkDeviceFactory(object):
    __metaclass__ = abc.ABCMeta  # use abstract class metaclass to control the creation behaviour of class

    network_device_id: int

    def __init__(self):
        self.network_device_id = 0

    @abc.abstractmethod
    def product(self, prefix_name: str) -> NetworkDevice:
        self.network_device_id += 1
        network_device: NetworkDevice = NetworkDevice(self.network_device_id, prefix_name + str(self.network_device_id))
        return network_device
