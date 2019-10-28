# design model: Visitor Model
# use to configure network elements
import abc
import os
import pickle
from typing import List, Tuple, Dict

from src import config
from src.graph.Flow import Flow
from src.graph.Graph import Graph
from src.graph.Solver import Solution
from src.graph.TimeSlotAllocator import TimeSlotAllocator, AllocationBlock
from src.net_elem.Channel import Channel
from src.net_elem.FilteringDatabase import FilteringDatabase, FilteringDatabaseItem
from src.net_elem.GateControlList import EnhancementGateControlList, GateControlList, GateControlListItem
from src.net_elem.Host import Host
from src.net_elem.Mac import MAC_TYPE
from src.net_elem.NetworkDevice import NetworkDevice, Port
import src.utils.MacAddressGenerator as MAG
from src.net_elem.Switch import Switch, TSNSwitch
from src.type import NodeId, PortNo, MacAddress, FlowId, EdgeId
import src.utils.RoutesGenerator as RG


class ConfigurationInfo(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def parse(self, **kwargs):
        pass


# port-configuration-information
class PortConfigurationInfo(ConfigurationInfo):
    node_id: NodeId
    port_list: List[Port]

    def __init__(self, node_id: NodeId):
        self.node_id = node_id
        self.port_list = []

    @abc.abstractmethod
    # def parse(self, node_edge_mac_info: MAG.NodeEdgeMacInfo = None):
    def parse(self, **kwargs):
        # assert node_edge_mac_info is not None
        assert kwargs['node_edge_mac_info']
        node_edge_mac_info: MAG.NodeEdgeMacInfo = kwargs['node_edge_mac_info']
        port_mac_pair_list: List[Tuple[PortNo, MacAddress]] = \
            node_edge_mac_info.node_mac_dict[self.node_id].port_mac_pair_list
        for port_mac_pair in port_mac_pair_list:
            port_no: PortNo = port_mac_pair[0]
            mac: MacAddress = port_mac_pair[1]
            mac_type: MAC_TYPE = MAG.MacAddressGenerator.parse_mac_type(mac)
            port: Port = Port(port_no, mac, mac_type)
            self.port_list.append(port)


# filtering-database-configuration-information
class FilteringDatabaseConfigurationInfo(ConfigurationInfo):
    switch_id: NodeId
    filtering_database: FilteringDatabase

    def __init__(self, switch_id: NodeId):
        self.switch_id = switch_id
        self.filtering_database = FilteringDatabase()

    @abc.abstractmethod
    # def parse(self,
    #           node_edge_mac_info: MAG.NodeEdgeMacInfo = None,
    #           route_immediate_entity: RG.RouteImmediateEntity = None):
    # TODO 这是什么魔鬼代码
    def parse(self, **kwargs):
        # assert node_edge_mac_info is not None
        # assert route_immediate_entity is not None
        assert kwargs['node_edge_mac_info']
        assert kwargs['route_immediate_entity']
        node_edge_mac_info: MAG.NodeEdgeMacInfo = kwargs['node_edge_mac_info']
        route_immediate_entity: RG.RouteImmediateEntity = kwargs['route_immediate_entity']
        port_macs_dict: Dict[PortNo, List[MacAddress]] = {}  # {port1: [mac1, mac2, ...], ...}
        mac_ports_dict: Dict[MacAddress, List[PortNo]] = {}  # {mac1: [port1, port2, ...], ...}
        _flow_routes_dict: Dict[FlowId, RG.FlowRoutes] = route_immediate_entity.flow_routes_dict
        for flow_id, flow_routes in _flow_routes_dict.items():
            _flow_routes: Dict[NodeId, RG.OneToOneRedundantRoutes] = flow_routes.flow_routes
            for dest_node_id, one_to_one_redundant_routes in flow_routes.items():
                _one_to_one_redundant_routes: List[RG.OneToOneRoute] = one_to_one_redundant_routes.redundant_routes
                for one_to_one_route in _one_to_one_redundant_routes:
                    _dest_mac: MacAddress = one_to_one_route.dest_mac
                    _node_route: List[NodeId] = one_to_one_route.node_route
                    _edge_route: List[EdgeId] = one_to_one_route.edge_route
                    if self.switch_id in _node_route:
                        _edge_mac_dict: Dict[EdgeId, MAG.EdgeMacMapper] = node_edge_mac_info.edge_mac_dict
                        _edge_id_list: List[EdgeId] = list(filter(
                            lambda _eid: self.switch_id in _edge_mac_dict[_eid].node_pair[0], _edge_mac_dict))
                        if _edge_id_list.__len__() != 0:
                            outbound_mac: MacAddress = _edge_mac_dict[_edge_id_list[0]].mac_pair[0]  # outbound mac
                            _node_mac_mapper: MAG.NodeMacMapper = node_edge_mac_info.node_mac_dict[self.switch_id]
                            _port_mac_pair_list: List[Tuple[PortNo, MacAddress]] = _node_mac_mapper.port_mac_pair_list
                            outbound_port: PortNo = [_port_mac_pair[0] for _port_mac_pair in _port_mac_pair_list if
                                                     outbound_mac == _port_mac_pair[1]]  # outbound port
                            # add port-macs-dict
                            if outbound_port in port_macs_dict.keys():
                                _mac_list: List[MacAddress] = port_macs_dict[outbound_port]
                                if outbound_mac not in _mac_list:
                                    _mac_list.append(outbound_mac)
                            else:
                                port_macs_dict[outbound_port] = [outbound_mac]
                            # add mac-ports-dict
                            if outbound_mac in mac_ports_dict.keys():
                                _port_list: List[PortNo] = mac_ports_dict[outbound_mac]
                                if outbound_port not in _port_list:
                                    _port_list.append(outbound_port)
                            else:
                                mac_ports_dict[outbound_mac] = [outbound_port]
        for mac, port_list in mac_ports_dict.items():
            self.filtering_database.add_item(mac, port_list, MAG.MacAddressGenerator.parse_mac_type(mac))


# gate-control-list-configuration-information
class GateControlListConfigurationInfo(ConfigurationInfo):
    switch_id: NodeId
    port_gate_control_list: Dict[PortNo, GateControlList]
    edge_gate_control_list: Dict[EdgeId, GateControlList]
    edge_port_pair_list: List[Tuple[EdgeId, PortNo]]

    def __init__(self, switch_id: NodeId):
        self.switch_id = switch_id
        self.port_gate_control_list = []
        self.edge_port_pair_list = []
        self.edge_port_pair_list = []

    @abc.abstractmethod
    # TODO 这又是什么魔鬼代码
    def parse(self, **kwargs):
        assert kwargs['graph']
        assert kwargs['node_edge_mac_info']
        assert kwargs['route_immediate_entity']
        graph: Graph = kwargs['graph']
        node_edge_mac_info: MAG.NodeEdgeMacInfo = kwargs['node_edge_mac_info']
        route_immediate_entity: RG.RouteImmediateEntity = kwargs['route_immediate_entity']

        _port_mac_pair_list: List[Tuple[PortNo, MacAddress]] = \
            node_edge_mac_info.node_mac_dict[self.switch_id].port_mac_pair_list
        _edge_mac_dict: Dict[EdgeId, MAG.EdgeMacMapper] = node_edge_mac_info.edge_mac_dict
        edge_port_pair_list: List[Tuple[EdgeId, PortNo]] = []
        _flow_routes_dict: Dict[FlowId, RG.FlowRoutes] = route_immediate_entity.flow_routes_dict
        for flow_id, flow_routes in _flow_routes_dict.items():
            _flow_routes: Dict[NodeId, RG.OneToOneRedundantRoutes] = flow_routes.flow_routes
            for dest_node_id, one_to_one_redundant_routes in flow_routes.items():
                _one_to_one_redundant_routes: List[RG.OneToOneRoute] = one_to_one_redundant_routes.redundant_routes
                for one_to_one_route in _one_to_one_redundant_routes:
                    _dest_mac: MacAddress = one_to_one_route.dest_mac
                    _node_route: List[NodeId] = one_to_one_route.node_route
                    _edge_route: List[EdgeId] = one_to_one_route.edge_route
                    if self.switch_id in _node_route:
                        _edge_mac_dict: Dict[EdgeId, MAG.EdgeMacMapper] = node_edge_mac_info.edge_mac_dict
                        _edge_id_list: List[EdgeId] = list(filter(
                            lambda _eid: self.switch_id in _edge_mac_dict[_eid].node_pair[0], _edge_mac_dict))
                        if _edge_id_list.__len__() != 0:
                            edge_id: EdgeId = _edge_id_list[0]
                            outbound_mac: MacAddress = _edge_mac_dict[edge_id].mac_pair[0]  # outbound mac
                            _node_mac_mapper: MAG.NodeMacMapper = node_edge_mac_info.node_mac_dict[self.switch_id]
                            _port_mac_pair_list: List[Tuple[PortNo, MacAddress]] = _node_mac_mapper.port_mac_pair_list
                            outbound_port: PortNo = [_port_mac_pair[0] for _port_mac_pair in _port_mac_pair_list if
                                                     outbound_mac == _port_mac_pair[1]]  # outbound port
                            # add edge-port-mapper
                            for edge_port_pair in edge_port_pair_list:
                                if edge_id in edge_port_pair[0]:
                                    edge_port_pair_list.append((edge_id, outbound_port))
        self.edge_port_pair_list = edge_port_pair_list
        for edge_id, edge in graph.edge_mapper.items():
            _time_slot_allocator: TimeSlotAllocator = edge.time_slot_allocator
            _allocation_blocks_m: List[AllocationBlock] = _time_slot_allocator.allocation_blocks_m
            if _allocation_blocks_m.__len__() == 0:  # no block has been allocated
                pass
            else:
                sorted_allocation_blocks_m: List[AllocationBlock] = \
                    sorted(_allocation_blocks_m, key=lambda b: b.send_time_offset)
                for block in sorted_allocation_blocks_m:
                    if block.send_time_offset > 0:
                        gate_control_list_item: GateControlListItem = GateControlListItem()


# enhancement-gate-control-list-configuration-information
class EnhancementGateControlListConfigurationInfo(GateControlListConfigurationInfo):

    def __init__(self, switch_id: NodeId):
        super().__init__(switch_id)
        pass

    @abc.abstractmethod
    def parse(self, **kwargs):
        pass


# --------------------------------------- necessary configuration information above ------------------------------------


# network-configurator, base class
class NetworkConfigurator(object, metaclass=abc.ABCMeta):
    node_edge_mac_info: MAG.NodeEdgeMacInfoBuilder

    @abc.abstractmethod
    def configure(self, obj: object):
        pass


# network-device-configurator, derived class of network-configurator
class NetworkDeviceConfigurator(NetworkConfigurator):

    @abc.abstractmethod
    def configure(self, network_device: NetworkDevice):
        pass

    def add_node_edge_mac_info(self, node_edge_mac_info: MAG.NodeEdgeMacInfoBuilder):
        self.node_edge_mac_info = node_edge_mac_info


# channel-configurator, derived class of network-configurator
class ChannelConfigurator(NetworkConfigurator):

    @abc.abstractmethod
    def configure(self, channel: Channel):
        pass


# switch-configurator, derived class of network-device-configurator
class SwitchConfigurator(NetworkDeviceConfigurator):
    # port_configuration_info: PortConfigurationInfo
    # filter_database_configuration_info: FilteringDatabaseConfigurationInfo
    graph: Graph
    flows: List[Flow]

    # def __init__(self):
    #     self.port_configuration_info = None
    #     self.filter_database_configuration_info = None

    # def set_port_configuration_info(self, port_configuration_info: PortConfigurationInfo):
    #     self.port_configuration_info = port_configuration_info
    #
    # def set_filter_database_configuration_info(
    #         self, filter_database_configuration_info: FilteringDatabaseConfigurationInfo):
    #     self.filter_database_configuration_info = filter_database_configuration_info

    @abc.abstractmethod
    def configure(self, switch: Switch):
        # get solution which contains graph and flows
        file = os.path.join(os.path.join(os.path.abspath('.'), 'json'), 'solution')  # TODO fix hard code
        with open(file, 'rb') as f:
            solution: Solution = pickle.load(f)
        graph: Graph = solution.graph
        flow_list: List[Flow] = solution.flows

        # get mac-list, edge-mac-dict and node-mac-dict
        mac_list: List[MacAddress] = MAG.MacAddressGenerator.generate_all_multicast_mac_address(graph)
        edge_mac_dict: Dict[EdgeId, MAG.EdgeMacMapper] = \
            MAG.MacAddressGenerator.assign_mac_address_to_edge(mac_list, graph)
        node_mac_dict: Dict[NodeId, MAG.NodeMacMapper] = \
            MAG.MacAddressGenerator.assign_mac_address_to_node(edge_mac_dict)

        # use node-edge-mac-info builder to build node-edge-mac-info
        node_edge_mac_info_builder: MAG.NodeEdgeMacInfoBuilder = MAG.NodeEdgeMacInfoBuilder()
        node_edge_mac_info_builder.add_mac_list(mac_list)
        node_edge_mac_info_builder.add_edge_mac_dict(edge_mac_dict)
        node_edge_mac_info_builder.add_node_mac_dict(node_mac_dict)
        node_edge_mac_info: MAG.NodeEdgeMacInfo = node_edge_mac_info_builder.build()

        # get route immediate entity
        route_immediate_entity: RG.RouteImmediateEntity = \
            RG.RoutesGenerator.generate_routes_immediate_entity(graph, flow_list, edge_mac_dict)

        # install NIC
        port_configuration_info: PortConfigurationInfo = PortConfigurationInfo(switch.device_id)
        port_configuration_info.parse(node_edge_mac_info=node_edge_mac_info)
        # self.set_port_configuration_info(port_configuration_info)
        switch.add_ports(port_configuration_info.port_list)

        # configure filtering database
        filtering_database_info: FilteringDatabaseConfigurationInfo = \
            FilteringDatabaseConfigurationInfo(switch.device_id)
        filtering_database_info.parse(
            ode_edge_mac_info=node_edge_mac_info, route_immediate_entity=route_immediate_entity)
        # self.set_filter_database_configuration_info(filtering_database_info)
        switch.set_filtering_database(filtering_database_info.filtering_database)


# use inheritance to implement tsn-switch-configurator
class TSNSwitchConfigurator(SwitchConfigurator):
    gate_control_list_configuration_info: GateControlListConfigurationInfo

    def __init__(self):
        super().__init__()
        self.gate_control_list_configuration_info = GateControlListConfigurationInfo()

    def set_gate_control_list_configuration_info(
            self, gate_control_list_configuration_info: EnhancementGateControlListConfigurationInfo):
        self.gate_control_list_configuration_info = gate_control_list_configuration_info

    @abc.abstractmethod
    def configure(self, tsn_switch: TSNSwitch):
        super().configure(tsn_switch)
        # TODO identify switch type
        if config.XML_CONFIG['enhancement-tsn-switch-enable'] is False:
            # TODO configure gate control list
            pass
        else:
            # TODO configure enhancement control list
            pass


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


# host-configurator
class HostConfigurator(NetworkDeviceConfigurator):

    @abc.abstractmethod
    def configure(self, host: Host):
        pass
