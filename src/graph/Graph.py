from typing import List, Dict, Set

from src.graph.TimeSlotAllocator import TimeSlotAllocator
from src.graph.FlowScheduler import FlowScheduler
from .Node import Node
from .Edge import Edge
from .Flow import Flow
from .FlowRouter import FlowRouter
from src.utils.Visualizer import Visualizer, GanttEntry, GanttBlock
import logging

logger = logging.getLogger(__name__)


# maybe a single instance
class Graph:
    nodes: List[int]
    edges: List[int]
    flows: List[int]
    node_mapper: Dict[int, Node]
    edge_mapper: Dict[int, Edge]
    flow_mapper: Dict[int, Flow]
    hyper_period: int
    flow_router: FlowRouter
    flow_scheduler: FlowScheduler
    failure_queue: Set[int]

    def __init__(self, nodes: List[int] = None, edges: List[int] = None, hp: int = 0):
        self.nodes = nodes
        self.edges = edges
        self.flows = []
        self.failure_queue = set()
        self.node_mapper = {}
        self.edge_mapper = {}
        self.flow_mapper = {}
        self.hyper_period = hp
        self.flow_router = \
            FlowRouter(self.nodes, self.edges, self.flows, self.node_mapper, self.edge_mapper, self.flow_mapper)
        self.flow_scheduler = \
            FlowScheduler(self.nodes, self.edges, self.flows, self.node_mapper, self.edge_mapper, self.flow_mapper)
        self.init_nodes()
        self.init_edges()
        # self.print_nodes()

    def get_node_num(self):
        return self.nodes.__len__()

    def get_edge_num(self):
        return self.edges.__len__()

    def print_nodes(self):
        for _nid in self.nodes:
            self.node_mapper[_nid].to_string()

    def init_nodes(self) -> bool:
        if self.nodes is None or self.nodes == []:
            logging.info('there is no nodes')
            return False
        for node_id in self.nodes:
            logger.info('initialize node [' + str(node_id) + ']')
            node: Node = Node(node_id)
            self.node_mapper[node_id] = node
        return True

    def init_edges(self) -> bool:
        if self.edges is None or self.edges == []:
            logging.info('there is no edges')
            return False
        edge_id = 1  # start from 1
        for edge_tuple in self.edges:
            logger.info(
                'initialize edge [' + str(edge_id) + '] <' + str(edge_tuple[0]) + '->' + str(edge_tuple[1]) + '>')
            in_node: int = edge_tuple[0]
            out_node: int = edge_tuple[1]
            _e: Edge = Edge(
                edge_id, in_node=self.node_mapper[in_node], out_node=self.node_mapper[out_node], hp=self.hyper_period)
            self.edge_mapper[edge_id] = _e
            self.node_mapper[in_node].append_out_edge(_e)
            self.node_mapper[out_node].append_in_edge(_e)
            edge_id += 1
        return True

    def set_edges_bandwidth(self, b: int):
        # TODO set edge bandwidth
        pass

    def set_all_edges_bandwidth(self, b: int):
        for edge in self.edge_mapper.values():
            edge.set_bandwidth(b)

    def set_end2switch_edges_bandwidth(self, b: int):
        # TODO set all host-to-switch edges delay
        pass

    def set_switch2switch_edges_bandwidth(self, b: int):
        # TODO set all switch-to-switch edges daley
        pass

    def set_all_edges_propagation_delay(self, prop_d: int):
        # TODO set all edges propagation delay
        pass

    def set_all_edges_process_delay(self, proc_d: int):
        # TODO set all edges propagation delay
        pass

    def add_flows(self, flows: List[Flow]):
        # add flows to flow list and flow mapper
        for _f in flows:
            self.flows.append(_f.flow_id)
            self.flow_mapper[_f.flow_id] = _f

    def route_all_flows(self, flows: List[Flow]):
        self.add_flows(flows)
        self.flow_router.route_all_flows()

    def route_flows_incrementally(self, flows: List[Flow]):
        self.add_flows(flows)
        _flows: List[int] = []
        for _f in flows:
            _flows.append(_f.flow_id)
        self.flow_router.route_flows_incrementally(_flows)

    def schedule_all_flows(self):
        pass

    def schedule_flows_incrementally(self):
        pass

    def combine_failure_queue(self):
        '''
        combine failure queue
        :return:
        '''
        self.failure_queue = self.flow_router.failure_queue.union(self.flow_scheduler.failure_queue)
        logger.info('WHOLE FAILURE QUEUE:' + str(self.failure_queue))

    # draw gantt chart for merged time slots allocation blocks
    # def draw_gantt(self):
    #     gantt_entries: List[GanttEntry] = []
    #     for _i, _e in enumerate(self.edges):
    #         _e: Edge = self.edge_mapper[_i + 1]
    #         _allocator: TimeSlotAllocator = _e.time_slot_allocator
    #         _time_slot_len: int = _allocator.time_slot_len
    #         _gantt_blocks: List[GanttBlock] = []
    #         for _j, _block in enumerate(_allocator.allocation_blocks_m):
    #             _caption = 'fid=' + str(_block.flow_id)
    #             _gantt_block: GanttBlock = GanttBlock(_block.interval.lower * _time_slot_len,
    #                                                   (_block.interval.upper + 1) * _time_slot_len, _caption)
    #             _gantt_blocks.append(_gantt_block)
    #         _gantt_entry: GanttEntry = GanttEntry(10 * _i, 'edge ' + str(_e.edge_id), 5, _gantt_blocks)
    #         gantt_entries.append(_gantt_entry)
    #     Visualizer.draw_gantt([0, self.hyper_period], [0, 10 * len(self.edges)], gantt_entries)

    # draw gantt chart for raw time slots allocation blocks

    def draw_gantt(self):
        '''
        gant chart without merging operation
        :return:
        '''
        # random color for flow
        _colors: Dict[int, str] = dict()
        for _fid in self.flows:
            # _colors[_fid] = Visualizer.random_color()
            _colors[_fid] = self.flow_mapper[_fid].color
        gantt_entries: List[GanttEntry] = []
        for _i, _e in enumerate(self.edges):
            _e: Edge = self.edge_mapper[_i + 1]
            _allocator: TimeSlotAllocator = _e.time_slot_allocator
            _time_slot_len: int = _allocator.time_slot_len
            _gantt_blocks: List[GanttBlock] = []
            for _j, _block in enumerate(_allocator.allocation_blocks):
                _caption: str = 'f=' + str(_block.flow_id) + '\n' + 'p=' + str(_block.phase)
                # _caption: str = ''
                _gantt_block: GanttBlock = GanttBlock(
                    _block.interval.lower * _time_slot_len,
                    (_block.interval.upper + 1 - _block.interval.lower) * _time_slot_len,
                    _caption, color=_colors[_block.flow_id])
                _gantt_blocks.append(_gantt_block)
            _gantt_entry: GanttEntry = GanttEntry(10 * _i, 'edge ' + str(_e.edge_id), 5, _gantt_blocks)
            gantt_entries.append(_gantt_entry)
        Visualizer.draw_gantt([0, self.hyper_period], [0, 10 * len(self.edges)], gantt_entries)
