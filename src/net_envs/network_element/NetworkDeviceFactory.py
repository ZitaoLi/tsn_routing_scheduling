import abc

from src.net_envs.network_element.NetworkDevice import NetworkDevice
from src.net_envs.network_element.NetworkDeviceFactoryInterface import NetworkDeviceFactoryInterface
from src.utils.Singleton import SingletonABC


class NetworkDeviceFactory(NetworkDeviceFactoryInterface, metaclass=SingletonABC):
    network_device_no: int

    def __init__(self):
        self.network_device_no = 0

    def product(self, unique_id: int) -> NetworkDevice:
        network_device: NetworkDevice = \
            self.get_instance_from_class_name('NetworkDevice', 'NetworkDevice', unique_id=unique_id)
        return network_device

    def get_instance_from_class_name(self, module_name: str, cls_name: str, **kwargs):
        _M = __import__('src.net_envs.network_element.' + module_name, fromlist=[cls_name])
        _C = getattr(_M, cls_name)
        self.network_device_no += 1
        assert 'unique_id' in kwargs.keys(), "parameter 'unique_id' is required"  # unique_id is required
        if 'prefix_name' in kwargs.keys():
            return _C(self.network_device_no, kwargs['prefix_name'] + str(self.network_device_no))
        else:
            return _C(self.network_device_no, 'NetworkDevice' + str(self.network_device_no))
