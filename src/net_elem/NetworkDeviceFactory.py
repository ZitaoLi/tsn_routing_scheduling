import abc

from src.net_elem.NetworkDevice import NetworkDevice
from src.utils.Singleton import SingletonDecorator


@SingletonDecorator
class NetworkDeviceFactory(object):
    __metaclass__ = abc.ABCMeta  # use abstract class metaclass to control the creation behaviour of class

    network_device_no: int

    def __init__(self):
        self.network_device_no = 0

    @abc.abstractmethod
    def product(self, unique_id: int) -> NetworkDevice:
        network_device: NetworkDevice = self.get_instance_from_class_name(
            'NetworkDevice',
            unique_id=unique_id)
        return network_device

    def get_instance_from_class_name(self, cls_name: str, **kwargs):
        _M = __import__('src.net_elem.' + cls_name, fromlist=[cls_name])
        _C = getattr(_M, cls_name)
        self.network_device_no += 1
        assert 'unique_id' in kwargs.keys()  # unique_id is required
        if 'prefix_name' in kwargs.keys():
            return _C(self.network_device_id, kwargs['prefix_name'] + str(self.network_device_no))
        else:
            return _C(self.network_device_id, 'NetworkDevice' + str(self.network_device_no))
