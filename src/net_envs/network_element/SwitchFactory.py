from src import config
from src.net_envs.network_element.NetworkDeviceFactory import NetworkDeviceFactory
from src.net_envs.network_element.Switch import Switch


class SwitchFactory(NetworkDeviceFactory):
    def product(self, unique_id: int) -> Switch:
        switch: Switch = \
            self.get_instance_from_class_name(
                'Switch', 'Switch', prefix_name=config.XML_CONFIG['tsn_switch_pre_name'], unique_id=unique_id)
        return switch
