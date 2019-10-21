from src.net_elem.NetworkDeviceFactory import NetworkDeviceFactory


class HostFactory(NetworkDeviceFactory):
    def product(self):
        super().product()
