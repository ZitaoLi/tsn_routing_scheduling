import abc
from typing import List

from src.net_envs.network.EthernetNetwork import EthernetNetwork
from src.net_envs.network.EthernetNetworkFactory import EthernetNetworkFactory
from src.net_envs.network.TSNNetwork import TSNNetwork
from src.net_envs.network_configurator.TSNHostConfigurator import TSNHostConfigurator
from src.net_envs.network_configurator.TSNSwitchConfigurator import TSNSwitchConfigurator
from src.net_envs.network_element.Host import Host
from src.net_envs.network_element.HostFactory import HostFactory
from src.net_envs.network_element.Switch import Switch
from src.net_envs.network_element.SwitchFactory import SwitchFactory
from src.net_envs.network_element.TSNHost import TSNHost
from src.net_envs.network_element.TSNSwitch import TSNSwitch
from src.type import NodeId


class TSNNetworkFactory(EthernetNetworkFactory):

    def product(self, *args, **kwargs) -> TSNNetwork:
        assert kwargs['enhancement_enable'], "parameter 'enhancement_enable' is required"
        enhancement_enable: bool = kwargs['enhancement_enable']

        # initialize empty network
        ethernet_network: EthernetNetwork = super().product()
        ethernet_network.__class__ = TSNNetwork  # force into EthernetNetwork
        tsn_network: TSNNetwork = ethernet_network

        # the network device which only has one NIC is host, otherwise switch
        tsn_host_id_list: List[NodeId] = [node_id for node_id, node_mac_mapper in
                                          self.node_edge_mac_info.node_mac_dict.items() if
                                          node_mac_mapper.port_list.__len__() == 1]
        tsn_switch_id_list: List[NodeId] = [node_id for node_id in self.node_edge_mac_info.node_mac_dict.keys()
                                            if node_id not in tsn_host_id_list]

        # product hosts and add them into network
        tsn_host_list: List[TSNHost] = []
        host_factory: HostFactory = HostFactory()  # factory singleton
        for tsn_host_id in tsn_host_id_list:
            host: Host = host_factory.product(tsn_host_id)
            host.__class__ = TSNHost
            tsn_host: TSNHost = host
            tsn_host_list.append(tsn_host)
        tsn_network.add_tsn_hosts(tsn_host_list)

        # product switches and add them into network
        tsn_switch_list: List[TSNSwitch] = []
        switch_factory: SwitchFactory = SwitchFactory()  # factory singleton
        for switch_id in tsn_switch_id_list:
            switch: Switch = switch_factory.product(switch_id)
            switch.__class__ = TSNSwitch
            tsn_switch: TSNSwitch = switch
            tsn_switch_list.append(tsn_switch)
        tsn_network.add_tsn_switches(tsn_switch_list)

        # configure tsn host
        tsn_host_configurator: TSNHostConfigurator = TSNHostConfigurator(
            self.node_edge_mac_info,
            self.route_immediate_entity,
            self.solution.graph,
            self.solution.flows,
            enhancement_enable=enhancement_enable)
        for tsn_host in tsn_host_list:
            tsn_host.accept_configurator(tsn_host_configurator)

        #  configure tsn switch
        tsn_switch_configurator: TSNSwitchConfigurator = TSNSwitchConfigurator(
            self.node_edge_mac_info,
            self.route_immediate_entity,
            self.solution.graph,
            enhancement_enable=enhancement_enable)
        for tsn_switch in tsn_switch_list:
            tsn_switch.accept_configurator(tsn_switch_configurator)

        return tsn_network
