from src import config
from src.net_elem.Host import Host
from src.net_elem.NetworkDeviceFactory import NetworkDeviceFactory


class HostFactory(NetworkDeviceFactory):
    def product(self, unique_id: int) -> Host:
        host: Host = self.get_instance_from_class_name(
            'Host',
            prefix_name=config.XML_CONFIG['tsn_host_pre_name'],
            unique_id=unique_id)
        return host
