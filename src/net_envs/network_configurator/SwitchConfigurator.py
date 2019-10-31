from src.net_envs.network_configurator.ConfigurationInfo import PortConfigurationInfo, \
    FilteringDatabaseConfigurationInfo
from src.net_envs.network_configurator.NetworkDeviceConfigurator import NetworkDeviceConfigurator
import src.utils.MacAddressGenerator as MAG
import src.utils.RoutesGenerator as RG
from src.net_envs.network_element.Switch import Switch


class SwitchConfigurator(NetworkDeviceConfigurator):
    route_immediate_entity: RG.RouteImmediateEntity

    def __init__(self, node_edge_mac_info: MAG.NodeEdgeMacInfo, route_immediate_entity: RG.RouteImmediateEntity):
        super().__init__(node_edge_mac_info)
        self.route_immediate_entity = route_immediate_entity

    def configure(self, switch: Switch):
        # install NIC
        port_configuration_info: PortConfigurationInfo = PortConfigurationInfo(switch.device_id)
        port_configuration_info.parse(node_edge_mac_info=self.node_edge_mac_info)
        switch.add_ports(port_configuration_info.port_list)

        # configure filtering database
        filtering_database_info: FilteringDatabaseConfigurationInfo = \
            FilteringDatabaseConfigurationInfo(switch.device_id)
        filtering_database_info.parse(
            node_edge_mac_info=self.node_edge_mac_info, route_immediate_entity=self.route_immediate_entity)
        switch.set_filtering_database(filtering_database_info.filtering_database)
