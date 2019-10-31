from src.graph.Graph import Graph
from src.net_envs.network_configurator.ConfigurationInfo import GateControlListConfigurationInfo, \
    EnhancementGateControlListConfigurationInfo
from src.net_envs.network_configurator.HostConfigurator import HostConfigurator
from src.net_envs.network_element.TSNHost import TSNHost
import src.utils.MacAddressGenerator as MAG
import src.utils.RoutesGenerator as RG


class TSNHostConfigurator(HostConfigurator):

    def __init__(self, node_edge_mac_info: MAG.NodeEdgeMacInfo, route_immediate_entity: RG.RouteImmediateEntity,
                 graph: Graph, enhancement_enable: bool = False):
        super().__init__(node_edge_mac_info)
        self.route_immediate_entity = route_immediate_entity
        self.enhancement_enable = enhancement_enable
        self.graph = graph

    def configure(self, tsn_host: TSNHost):
        assert self.graph, "instance variable 'graph' must be set"
        assert self.enhancement_enable, "instance variable 'enhancement_enable' must be set"
        super().configure(tsn_host)  # call base class method
        if self.enhancement_enable is False:
            gate_control_list_configuration_info: GateControlListConfigurationInfo = \
                GateControlListConfigurationInfo(tsn_host.device_id)
            gate_control_list_configuration_info.parse(
                graph=self.graph,
                node_edge_mac_info=self.node_edge_mac_info,
                route_immediate_entity=self.route_immediate_entity)
            tsn_host.port_gate_control_list = gate_control_list_configuration_info.port_gate_control_list
            # for port in tsn_host.ports:
            #     port_no: PortNo = port.port_id
            #     if port_no in gate_control_list_configuration_info.port_gate_control_list.keys():
            #         gate_control_list: GateControlList = \
            #             gate_control_list_configuration_info.port_gate_control_list[port_no]
            #         tsn_host.set_gate_control_list(gate_control_list)
        else:
            enhancement_gate_control_list_configuration_info: EnhancementGateControlListConfigurationInfo = \
                EnhancementGateControlListConfigurationInfo(tsn_host.device_id)
            enhancement_gate_control_list_configuration_info.parse(
                graph=self.graph,
                node_edge_mac_info=self.node_edge_mac_info,
                route_immediate_entity=self.route_immediate_entity)
            tsn_host.port_gate_control_list = enhancement_gate_control_list_configuration_info.port_gate_control_list
            # for port in tsn_host.ports:
            #     port_no: PortNo = port.port_id
            #     if port_no in enhancement_gate_control_list_configuration_info.port_gate_control_list.keys():
            #         gate_control_list: GateControlList = \
            #             enhancement_gate_control_list_configuration_info.port_gate_control_list[port_no]
            #         tsn_host.set_gate_control_list(gate_control_list)
