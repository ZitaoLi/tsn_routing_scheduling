from typing import List

from src.graph.Flow import Flow
from src.graph.Graph import Graph
from src.net_envs.network_configurator.ConfigurationInfo import GateControlListConfigurationInfo, \
    EnhancementGateControlListConfigurationInfo, TSNHostConfigurationInfo
from src.net_envs.network_configurator.HostConfigurator import HostConfigurator
from src.net_envs.network_element.TSNHost import TSNHost
import src.utils.MacAddressGenerator as MAG
import src.utils.RoutesGenerator as RG


class TSNHostConfigurator(HostConfigurator):
    graph: Graph
    flows: List[Flow]

    def __init__(self, node_edge_mac_info: MAG.NodeEdgeMacInfo, route_immediate_entity: RG.RouteImmediateEntity,
                 graph: Graph, flows: List[Flow], enhancement_enable: bool = False):
        super().__init__(node_edge_mac_info)
        self.route_immediate_entity = route_immediate_entity
        self.enhancement_enable = enhancement_enable
        self.graph = graph
        self.flows = flows

    def configure(self, tsn_host: TSNHost):
        assert self.graph, "instance variable 'graph' must be set"
        assert self.enhancement_enable, "instance variable 'enhancement_enable' must be set"
        super().configure(tsn_host)  # call base class method

        # configure gate control list
        if self.enhancement_enable is False:
            gate_control_list_configuration_info: GateControlListConfigurationInfo = \
                GateControlListConfigurationInfo(tsn_host.device_id)
            gate_control_list_configuration_info.parse(
                graph=self.graph,
                node_edge_mac_info=self.node_edge_mac_info,
                route_immediate_entity=self.route_immediate_entity)
            tsn_host.port_gate_control_list = gate_control_list_configuration_info.port_gate_control_list
        else:
            enhancement_gate_control_list_configuration_info: EnhancementGateControlListConfigurationInfo = \
                EnhancementGateControlListConfigurationInfo(tsn_host.device_id)
            enhancement_gate_control_list_configuration_info.parse(
                graph=self.graph,
                node_edge_mac_info=self.node_edge_mac_info,
                route_immediate_entity=self.route_immediate_entity,
                ports=tsn_host.ports)
            tsn_host.port_gate_control_list = enhancement_gate_control_list_configuration_info.port_gate_control_list

        # configure tsn flow information
        tsn_host_configuration_info: TSNHostConfigurationInfo = TSNHostConfigurationInfo(tsn_host.device_id)
        tsn_host_configuration_info.parse(
            graph=self.graph,
            node_edge_mac_info=self.node_edge_mac_info,
            route_immediate_entity=self.route_immediate_entity,
            flows=self.flows,
            port_gate_control_list=tsn_host.port_gate_control_list)
        tsn_host.tsn_flow_info_list = tsn_host_configuration_info.tsn_flow_info_list
