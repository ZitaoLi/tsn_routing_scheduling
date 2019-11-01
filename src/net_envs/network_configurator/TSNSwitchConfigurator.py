# use inheritance to implement tsn-switch-configurator
from src.graph.Graph import Graph
from src.net_envs.network_component.GateControlList import GateControlList, EnhancementGateControlList
from src.net_envs.network_configurator.ConfigurationInfo import GateControlListConfigurationInfo, \
    EnhancementGateControlListConfigurationInfo
from src.net_envs.network_configurator.SwitchConfigurator import SwitchConfigurator
import src.utils.MacAddressGenerator as MAG
import src.utils.RoutesGenerator as RG
from src.net_envs.network_element.TSNSwitch import TSNSwitch
from src.type import PortNo


class TSNSwitchConfigurator(SwitchConfigurator):
    enhancement_enable: bool
    graph: Graph

    def __init__(self, node_edge_mac_info: MAG.NodeEdgeMacInfo, route_immediate_entity: RG.RouteImmediateEntity,
                 graph: Graph, enhancement_enable: bool = False):
        super().__init__(node_edge_mac_info, route_immediate_entity)
        self.enhancement_enable = enhancement_enable
        self.graph = graph

    def configure(self, tsn_switch: TSNSwitch):
        assert self.graph, "instance variable 'graph' must be set"
        assert self.enhancement_enable, "instance variable 'enhancement_enable' must be set"
        super().configure(tsn_switch)  # call base class method

        # configure gate control list
        if self.enhancement_enable is False:
            gate_control_list_configuration_info: GateControlListConfigurationInfo = \
                GateControlListConfigurationInfo(tsn_switch.device_id)
            gate_control_list_configuration_info.parse(
                graph=self.graph,
                node_edge_mac_info=self.node_edge_mac_info,
                route_immediate_entity=self.route_immediate_entity)
            tsn_switch.port_gate_control_list = gate_control_list_configuration_info.port_gate_control_list
        else:
            enhancement_gate_control_list_configuration_info: EnhancementGateControlListConfigurationInfo = \
                EnhancementGateControlListConfigurationInfo(tsn_switch.device_id)
            enhancement_gate_control_list_configuration_info.parse(
                graph=self.graph,
                node_edge_mac_info=self.node_edge_mac_info,
                route_immediate_entity=self.route_immediate_entity)
            tsn_switch.port_gate_control_list = enhancement_gate_control_list_configuration_info.port_gate_control_list


# use decorator model to implement enhancement-tsn-switch-configurator,
# note that decorator model is not equal to python decorator
class EnhancementGateControlListDecorator(object):
    switch_configurator: SwitchConfigurator

    def __init__(self, switch_configurator: SwitchConfigurator):
        self.switch_configurator = switch_configurator

    def configure(self, tsn_switch: TSNSwitch):
        pass

    def add_enhancement_gate_control_list(self):
        # TODO dynamically add variables and methods
        # dynamically add enhancement-gate-control-list
        self.switch_configurator.enhancement_gate_control_list = EnhancementGateControlList()
