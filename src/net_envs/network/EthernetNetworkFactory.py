import abc
from typing import List

from src.net_envs.network.EthernetNetwork import EthernetNetwork
from src.net_envs.network.Network import Network
from src.net_envs.network.NetworkFactory import NetworkFactory
from src.net_envs.network_configurator.HostConfigurator import HostConfigurator
from src.net_envs.network_configurator.SwitchConfigurator import SwitchConfigurator
from src.net_envs.network_element.Host import Host
from src.net_envs.network_element.HostFactory import HostFactory
from src.net_envs.network_element.Switch import Switch
from src.net_envs.network_element.SwitchFactory import SwitchFactory
from src.type import NodeId
import src.utils.RoutesGenerator as RG


class EthernetNetworkFactory(NetworkFactory):
    route_immediate_entity: RG.RouteImmediateEntity

    def product(self, *args, **kwargs) -> EthernetNetwork:
        # initialize empty network
        network: Network = super().product(*args, **kwargs)
        network.__class__ = EthernetNetwork  # force into EthernetNetwork
        ethernet_network: EthernetNetwork = network

        # the network device which only has one NIC is host, otherwise switch
        host_id_list: List[NodeId] = [node_id for node_id, node_mac_mapper in
                                      self.node_edge_mac_info.node_mac_dict.items()
                                      if node_mac_mapper.port_list.__len__() == 1]
        switch_id_list: List[NodeId] = [node_id for node_id in self.node_edge_mac_info.node_mac_dict.keys()
                                        if node_id not in host_id_list]

        # set route immediate entity
        self.route_immediate_entity = \
            RG.RoutesGenerator.generate_routes_immediate_entity(
                self.solution.graph, self.solution.flows,
                self.node_edge_mac_info.edge_mac_dict, self.node_edge_mac_info.flow_mac_dict)

        # product hosts and add them into network
        host_list: List[Host] = []
        host_factory: HostFactory = HostFactory()  # factory singleton
        for host_id in host_id_list:
            host: Host = host_factory.product(host_id)
            host_list.append(host)
        ethernet_network.add_hosts(host_list)

        # product switches and add them into network
        switch_list: List[Switch] = []
        switch_factory: SwitchFactory = SwitchFactory()  # factory singleton
        for switch_id in switch_id_list:
            switch: Switch = switch_factory.product(switch_id)
            switch_list.append(switch)
        ethernet_network.add_switches(switch_list)

        # configure hosts
        host_configurator: HostConfigurator = HostConfigurator(self.node_edge_mac_info)
        for host in host_list:
            host.accept_configurator(host_configurator)

        # configure switches
        switch_configurator: SwitchConfigurator = \
            SwitchConfigurator(self.node_edge_mac_info, self.route_immediate_entity)
        for switch in switch_list:
            switch.accept_configurator(switch_configurator)

        return ethernet_network
