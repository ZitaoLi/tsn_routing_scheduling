import abc
from typing import List, Tuple, Dict, Set

from src import config
from src.graph.Flow import Flow
from src.graph.Graph import Graph
from src.graph.TimeSlotAllocator import TimeSlotAllocator, AllocationBlock
from src.net_envs.network_component.FilteringDatabase import FilteringDatabase
from src.net_envs.network_component.GateControlList import GateControlList, GateControlListItem, \
    EXCLUSIVE_NON_TSN_GATE_STATES, EXCLUSIVE_TSN_GATE_STATES, EnhancementGateControlList, EnhancementGateControlListItem
from src.net_envs.network_component.Mac import MAC_TYPE
from src.net_envs.network_element.NetworkDevice import Port
from src.net_envs.network_element.TSNHost import TSNFlowInfo
from src.type import NodeId, PortNo, MacAddress, FlowId, EdgeId, SimTime, QueueId
import src.utils.MacAddressGenerator as MAG
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

    # def parse(self, node_edge_mac_info: MAG.NodeEdgeMacInfo = None):
    def parse(self, **kwargs):
        # assert node_edge_mac_info is not None
        assert kwargs['node_edge_mac_info'], "parameter 'node_edge_mac_info' is required"
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

    # TODO 这是什么魔鬼代码
    def parse(self, **kwargs):
        assert kwargs['node_edge_mac_info']
        assert kwargs['route_immediate_entity']
        node_edge_mac_info: MAG.NodeEdgeMacInfo = kwargs['node_edge_mac_info']
        route_immediate_entity: RG.RouteImmediateEntity = kwargs['route_immediate_entity']
        port_macs_dict: Dict[PortNo, List[MacAddress]] = {}  # {port1: [mac1, mac2, ...], ...}
        mac_ports_dict: Dict[MacAddress, List[PortNo]] = {}  # {mac1: [port1, port2, ...], ...}
        _flow_routes_dict: Dict[FlowId, RG.FlowRoutes] = route_immediate_entity.flow_routes_dict
        for flow_id, flow_routes in _flow_routes_dict.items():
            _group_mac: MacAddress = _flow_routes_dict[flow_id].group_mac
            _flow_routes: Dict[NodeId, RG.OneToOneRedundantRoutes] = flow_routes.flow_routes
            for dest_node_id, one_to_one_redundant_routes in _flow_routes.items():
                _one_to_one_redundant_routes: List[RG.OneToOneRoute] = one_to_one_redundant_routes.redundant_routes
                for one_to_one_route in _one_to_one_redundant_routes:
                    _dest_mac: MacAddress = one_to_one_route.dest_mac
                    _node_route: List[NodeId] = one_to_one_route.node_route
                    _edge_route: List[EdgeId] = one_to_one_route.edge_route
                    if self.switch_id in _node_route:
                        _edge_mac_dict: Dict[EdgeId, MAG.EdgeMacMapper] = node_edge_mac_info.edge_mac_dict
                        _edge_id_list: List[EdgeId] = list(filter(
                            lambda _eid: self.switch_id == _edge_mac_dict[_eid].node_pair[0], _edge_mac_dict))
                        assert _edge_id_list.__len__() != 0
                        outbound_edge_list: List[EdgeId] = list(set(_edge_route).intersection(set(_edge_id_list)))
                        assert outbound_edge_list.__len__() != 0
                        outbound_edge: EdgeId = outbound_edge_list[0]
                        outbound_mac: MacAddress = _edge_mac_dict[outbound_edge].mac_pair[0]  # outbound mac
                        _node_mac_mapper: MAG.NodeMacMapper = node_edge_mac_info.node_mac_dict[self.switch_id]
                        _port_mac_pair_list: List[Tuple[PortNo, MacAddress]] = _node_mac_mapper.port_mac_pair_list
                        outbound_port: PortNo = [_port_mac_pair[0] for _port_mac_pair in _port_mac_pair_list if
                                                 outbound_mac == _port_mac_pair[1]][0]  # outbound port
                        # add port-macs-dict
                        if outbound_port in port_macs_dict.keys():
                            _mac_list: List[MacAddress] = port_macs_dict[outbound_port]
                            if _dest_mac not in _mac_list:
                                _mac_list.append(_dest_mac)
                        else:
                            port_macs_dict[outbound_port] = [_dest_mac]
                        # add port-macs-dict
                        if outbound_port in port_macs_dict.keys():
                            _mac_list: List[MacAddress] = port_macs_dict[outbound_port]
                            if _group_mac not in _mac_list:
                                _mac_list.append(_group_mac)
                        else:
                            port_macs_dict[outbound_port] = [_group_mac]
                        # add mac-ports-dict
                        if _dest_mac in mac_ports_dict.keys():
                            _port_list: List[PortNo] = mac_ports_dict[_dest_mac]
                            if outbound_port not in _port_list:
                                _port_list.append(outbound_port)
                        else:
                            mac_ports_dict[_dest_mac] = [outbound_port]
                        # add mac-ports-dict
                        if _group_mac in mac_ports_dict.keys():
                            _port_list: List[PortNo] = mac_ports_dict[_group_mac]
                            if outbound_port not in _port_list:
                                _port_list.append(outbound_port)
                        else:
                            mac_ports_dict[_group_mac] = [outbound_port]
        for mac, port_list in mac_ports_dict.items():
            self.filtering_database.product_and_add_item(mac, port_list, MAG.MacAddressGenerator.parse_mac_type(mac))


# gate-control-list-configuration-information
class GateControlListConfigurationInfo(ConfigurationInfo):
    switch_id: NodeId
    port_gate_control_list: Dict[PortNo, GateControlList]
    edge_gate_control_list: Dict[EdgeId, GateControlList]
    edge_port_pair_list: List[Tuple[EdgeId, PortNo]]

    def __init__(self, switch_id: NodeId):
        self.switch_id = switch_id
        self.port_gate_control_list = {}
        self.edge_gate_control_list = {}
        # if self.__class__ == GateControlListConfigurationInfo:
        #     self.port_gate_control_list = []
        #     self.edge_port_pair_list = []
        self.edge_port_pair_list = []

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
        self.edge_port_pair_list = \
            GateControlListConfigurationInfo.generate_edge_port_pair_list(
                self.switch_id, node_edge_mac_info, route_immediate_entity)
        for edge_id, edge in graph.edge_mapper.items():
            _time_slot_allocator: TimeSlotAllocator = edge.time_slot_allocator
            _allocation_blocks_m: List[AllocationBlock] = _time_slot_allocator.allocation_blocks_m
            gate_control_list: GateControlList = GateControlList()
            port_no: PortNo = list(filter(lambda p: p[0] == edge_id, self.edge_port_pair_list))[0]
            self.port_gate_control_list[port_no] = gate_control_list
            self.edge_gate_control_list[edge_id] = gate_control_list
            hyper_period: float = config.GRAPH_CONFIG['hyper-period']
            time: SimTime = SimTime(hyper_period)  # initial time length
            gate_control_list_item: GateControlListItem = GateControlListItem(time, EXCLUSIVE_NON_TSN_GATE_STATES)
            if _allocation_blocks_m.__len__() != 0:  # no block has been allocated
                gate_control_list.add_item(gate_control_list_item)
            else:
                sorted_allocation_blocks_m: List[AllocationBlock] = \
                    sorted(_allocation_blocks_m, key=lambda b: b.send_time_offset)
                # note that the order of following code is very important
                for i, block in enumerate(sorted_allocation_blocks_m):
                    # the first one block
                    if i == 0 and block.send_time_offset > 0:
                        next_block: AllocationBlock = sorted_allocation_blocks_m[1]
                        time = SimTime(next_block.send_time_offset)
                        gate_control_list_item = GateControlListItem(time, EXCLUSIVE_NON_TSN_GATE_STATES)
                        gate_control_list.add_item(gate_control_list_item)
                    # the tsn block
                    if block.flow_id != 0:
                        # the block before tsn block
                        if i >= 1 and sorted_allocation_blocks_m[i - 1].send_time_offset + \
                                sorted_allocation_blocks_m[i - 1].interval < block.send_time_offset:
                            time = block.send_time_offset - (sorted_allocation_blocks_m[i - 1].send_time_offset +
                                                             sorted_allocation_blocks_m[i - 1].interval)
                            gate_control_list_item = GateControlListItem(time, EXCLUSIVE_NON_TSN_GATE_STATES)
                            gate_control_list.add_item(gate_control_list_item)
                        time = block.interval
                        gate_control_list_item = GateControlListItem(time, EXCLUSIVE_TSN_GATE_STATES)
                        gate_control_list.add_item(gate_control_list_item)
                    else:
                        assert block.flow_id != 0
                    # the last one block
                    if i == sorted_allocation_blocks_m.__len__() - 1 and \
                            sorted_allocation_blocks_m[i - 1].send_time_offset + \
                            sorted_allocation_blocks_m[i - 1].interval < hyper_period:
                        time = hyper_period - sorted_allocation_blocks_m[i - 1].send_time_offset + \
                               sorted_allocation_blocks_m[i - 1].interval
                        gate_control_list_item = GateControlListItem(time, EXCLUSIVE_NON_TSN_GATE_STATES)
                        gate_control_list.add_item(gate_control_list_item)

    # TODO fix bugs here ! this is important
    @staticmethod
    def generate_edge_port_pair_list(node_id: NodeId,
                                     node_edge_mac_info: MAG.NodeEdgeMacInfo,
                                     route_immediate_entity: RG.RouteImmediateEntity = None,
                                     ports: List[Port] = None) -> List[Tuple[EdgeId, PortNo]]:
        edge_port_pair_list: List[Tuple[EdgeId, PortNo]] = []

        for port in ports:
            mac: MacAddress = port.mac
            edge_id: EdgeId = list(filter(lambda eid: node_edge_mac_info.edge_mac_dict[eid].mac_pair[0] == mac,
                                          node_edge_mac_info.edge_mac_dict))[0]
            edge_port_pair_list.append((edge_id, port.port_id))

        # edge_port_pair_set: Set[Tuple[EdgeId, PortNo]] = set()
        # _flow_routes_dict: Dict[FlowId, RG.FlowRoutes] = route_immediate_entity.flow_routes_dict
        # for flow_id, flow_routes in _flow_routes_dict.items():
        #     _flow_routes: Dict[NodeId, RG.OneToOneRedundantRoutes] = flow_routes.flow_routes
        #     for dest_node_id, one_to_one_redundant_routes in _flow_routes.items():
        #         _one_to_one_redundant_routes: List[RG.OneToOneRoute] = one_to_one_redundant_routes.redundant_routes
        #         for one_to_one_route in _one_to_one_redundant_routes:
        #             _dest_mac: MacAddress = one_to_one_route.dest_mac
        #             _node_route: List[NodeId] = one_to_one_route.node_route
        #             _edge_route: List[EdgeId] = one_to_one_route.edge_route
        #             if node_id in _node_route:
        #                 _edge_mac_dict: Dict[EdgeId, MAG.EdgeMacMapper] = node_edge_mac_info.edge_mac_dict
        #                 _edge_id_list: List[EdgeId] = list(filter(
        #                     lambda _eid: node_id == _edge_mac_dict[_eid].node_pair[0], _edge_mac_dict))
        #                 assert _edge_id_list.__len__() != 0
        #                 for _edge_id in _edge_id_list:
        #                     # edge_id: EdgeId = _edge_id_list[0]
        #                     outbound_mac: MacAddress = _edge_mac_dict[_edge_id].mac_pair[0]  # outbound mac
        #                     _node_mac_mapper: MAG.NodeMacMapper = node_edge_mac_info.node_mac_dict[node_id]
        #                     _port_mac_pair_list: List[Tuple[PortNo, MacAddress]] = _node_mac_mapper.port_mac_pair_list
        #                     outbound_port: PortNo = [_port_mac_pair[0] for _port_mac_pair in _port_mac_pair_list if
        #                                              outbound_mac == _port_mac_pair[1]][0]  # outbound port
        #                     # add edge-port-mapper
        #                     # if edge_port_pair_list.__len__() == 0:
        #                     #     edge_port_pair_list.append((edge_id, outbound_port))
        #                     # else:
        #                     #     for edge_port_pair in edge_port_pair_list:
        #                     #         if edge_id == edge_port_pair[0]:
        #                     #             edge_port_pair_list.append((edge_id, outbound_port))
        #                     edge_port_pair_set.add((_edge_id, outbound_port))
        # edge_port_pair_list = list(edge_port_pair_set)
        return edge_port_pair_list


# enhancement-gate-control-list-configuration-information, used to configure tsn switch
class EnhancementGateControlListConfigurationInfo(GateControlListConfigurationInfo):
    # port_enhancement_gate_control_list: Dict[PortNo, EnhancementGateControlList]
    # edge_enhancement_gate_control_list: Dict[EdgeId, EnhancementGateControlList]

    def __init__(self, switch_id: NodeId):
        super().__init__(switch_id)
        # if self.__class__ == EnhancementGateControlListConfigurationInfo:
        #     self.port_enhancement_gate_control_list = []
        #     self.edge_enhancement_gate_control_list = []

    # TODO 这又又是什么魔鬼代码
    def parse(self, **kwargs):
        assert kwargs['graph']
        assert kwargs['node_edge_mac_info']
        assert kwargs['route_immediate_entity']
        assert kwargs['ports']
        graph: Graph = kwargs['graph']
        node_edge_mac_info: MAG.NodeEdgeMacInfo = kwargs['node_edge_mac_info']
        route_immediate_entity: RG.RouteImmediateEntity = kwargs['route_immediate_entity']
        ports: List[Port] = kwargs['ports']
        _port_mac_pair_list: List[Tuple[PortNo, MacAddress]] = \
            node_edge_mac_info.node_mac_dict[self.switch_id].port_mac_pair_list
        _edge_mac_dict: Dict[EdgeId, MAG.EdgeMacMapper] = node_edge_mac_info.edge_mac_dict
        self.edge_port_pair_list = GateControlListConfigurationInfo.generate_edge_port_pair_list(
            self.switch_id, node_edge_mac_info, route_immediate_entity, ports=ports)
        for edge_id, edge in graph.edge_mapper.items():
            if edge.in_node.node_id != self.switch_id:
                continue
            _time_slot_allocator: TimeSlotAllocator = edge.time_slot_allocator
            _allocation_blocks_m: List[AllocationBlock] = _time_slot_allocator.allocation_blocks_m
            enhancement_gate_control_list: EnhancementGateControlList = EnhancementGateControlList()
            port_no: PortNo = None
            try:
                port_no: PortNo = list(filter(lambda p: p[0] == edge_id, self.edge_port_pair_list))[0][1]# find port no
            except:
                print(edge_id)
            self.port_gate_control_list[port_no] = enhancement_gate_control_list
            self.edge_gate_control_list[edge_id] = enhancement_gate_control_list
            hyper_period: float = config.GRAPH_CONFIG['hyper-period']
            time: SimTime = SimTime(hyper_period)  # initial time length
            enhancement_gate_control_list_item: EnhancementGateControlListItem = EnhancementGateControlListItem(
                time, EXCLUSIVE_NON_TSN_GATE_STATES, FlowId(0), 0)
            # if _allocation_blocks_m.__len__() != 0:  # no block has been allocated
            if _allocation_blocks_m.__len__() == 0:  # no block has been allocated
                enhancement_gate_control_list.add_item(enhancement_gate_control_list_item)
            else:
                # sort the block list based on send time offset
                # sorted_allocation_blocks_m: List[AllocationBlock] = \
                #     sorted(_allocation_blocks_m, key=lambda b: b.send_time_offset)
                # sorted_allocation_blocks_m: List[AllocationBlock] = \
                #     sorted(_allocation_blocks_m, key=lambda b: b.interval.lower)
                sorted_allocation_blocks_m: List[AllocationBlock] = \
                    _time_slot_allocator.sort_allocation_blocks(_allocation_blocks_m)
                # note that the order of following code is very important
                for i, block in enumerate(sorted_allocation_blocks_m):
                    # the first one block
                    # if i == 0 and block.send_time_offset > 0:
                    if i == 0 and block.interval.lower > 0:
                        next_block: AllocationBlock = sorted_allocation_blocks_m[0]
                        # time = SimTime(next_block.send_time_offset)
                        time = SimTime(next_block.interval.lower * _time_slot_allocator.time_slot_len)
                        enhancement_gate_control_list_item = \
                            EnhancementGateControlListItem(time, EXCLUSIVE_NON_TSN_GATE_STATES, FlowId(0), 0)
                        enhancement_gate_control_list.add_item(enhancement_gate_control_list_item)
                    # the tsn block
                    if block.flow_id != 0:
                        # the block before tsn block
                        if i >= 1 and sorted_allocation_blocks_m[i - 1].interval.upper + 1 < block.interval.lower:
                            time = \
                                (block.interval.lower - (sorted_allocation_blocks_m[i - 1]).interval.upper - 1) * \
                                _time_slot_allocator.time_slot_len
                            enhancement_gate_control_list_item = \
                                EnhancementGateControlListItem(time, EXCLUSIVE_NON_TSN_GATE_STATES, FlowId(0), 0)
                            enhancement_gate_control_list.add_item(enhancement_gate_control_list_item)
                        time = (block.interval.upper + 1 - block.interval.lower) * _time_slot_allocator.time_slot_len
                        enhancement_gate_control_list_item = \
                            EnhancementGateControlListItem(time, EXCLUSIVE_TSN_GATE_STATES, block.flow_id, block.phase)
                        enhancement_gate_control_list.add_item(enhancement_gate_control_list_item)
                    else:
                        assert block.flow_id != 0
                    # the last one block
                    if i == sorted_allocation_blocks_m.__len__() - 1 \
                            and (sorted_allocation_blocks_m[i].interval.upper + 1) * \
                            _time_slot_allocator.time_slot_len < hyper_period:
                        time = hyper_period - (sorted_allocation_blocks_m[i].interval.upper + 1) * \
                               _time_slot_allocator.time_slot_len
                        enhancement_gate_control_list_item = \
                            EnhancementGateControlListItem(time, EXCLUSIVE_NON_TSN_GATE_STATES, FlowId(0), 0)
                        enhancement_gate_control_list.add_item(enhancement_gate_control_list_item)
                        # TODO 处理首尾相连的情况


# used to configure tsn host
class TSNHostConfigurationInfo(ConfigurationInfo):
    tsn_host_id: NodeId
    tsn_flow_info_list: List[TSNFlowInfo]

    def __init__(self, tsn_host_id: NodeId):
        self.tsn_host_id = tsn_host_id
        self.tsn_flow_info_list = []

    def parse(self, **kwargs):
        assert kwargs['graph']
        assert kwargs['flows']
        assert kwargs['node_edge_mac_info']
        assert kwargs['route_immediate_entity']
        assert kwargs['port_gate_control_list']
        graph: Graph = kwargs['graph']
        flows: List[Flow] = kwargs['flows']
        node_edge_mac_info: MAG.NodeEdgeMacInfo = kwargs['node_edge_mac_info']
        route_immediate_entity: RG.RouteImmediateEntity = kwargs['route_immediate_entity']
        port_gate_control_list: Dict[PortNo, GateControlList] = kwargs['port_gate_control_list']
        # TODO
        flows_strart_time: Dict[FlowId, SimTime] = {}
        strat_time: SimTime = SimTime(0)
        for e_gcl in port_gate_control_list.values():
            for e_gcl_item in e_gcl.items:
                if e_gcl_item.flow_id not in flows_strart_time and e_gcl_item.phase == 0:
                    flows_strart_time[e_gcl_item.flow_id] = strat_time
                strat_time += e_gcl_item.time
        m_flows: List[Flow] = list(filter(lambda f: f.source == self.tsn_host_id, flows))
        for m_flow in m_flows:
            cycle_time: SimTime = m_flow.period
            size: int = m_flow.size
            flow_id: FlowId = m_flow.flow_id
            start_time: SimTime = flows_strart_time[flow_id]  # TODO
            queue: QueueId = QueueId(7)
            dest_mac: MacAddress = ''  # TODO
            group_mac: MacAddress = node_edge_mac_info.flow_mac_dict[flow_id].group_mac
            tsn_flow_info: TSNFlowInfo = TSNFlowInfo(
                flow_id=flow_id, start_time=start_time, queue=queue, dest_mac=dest_mac, group_mac=group_mac,
                size=size, cycle_time=cycle_time)
            self.tsn_flow_info_list.append(tsn_flow_info)
