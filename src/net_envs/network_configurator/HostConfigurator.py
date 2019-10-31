# host-configurator
from src.net_envs.network_configurator.ConfigurationInfo import PortConfigurationInfo
from src.net_envs.network_configurator.NetworkDeviceConfigurator import NetworkDeviceConfigurator
from src.net_envs.network_element.Host import Host
import src.utils.MacAddressGenerator as MAG
import src.utils.RoutesGenerator as RG


class HostConfigurator(NetworkDeviceConfigurator):
    route_immediate_entity: RG.RouteImmediateEntity

    def __init__(self, node_edge_mac_info: MAG.NodeEdgeMacInfo):
        super().__init__(node_edge_mac_info)

    def configure(self, host: Host):
        # install NIC
        port_configuration_info: PortConfigurationInfo = PortConfigurationInfo(host.device_id)
        port_configuration_info.parse(node_edge_mac_info=self.node_edge_mac_info)
        host.add_ports(port_configuration_info.port_list)
