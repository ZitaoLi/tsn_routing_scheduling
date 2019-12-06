import os
from enum import Enum

from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.type import ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY, TOPO_STRATEGY, TIME_GRANULARITY

src_dir: str = os.path.dirname(os.path.abspath(__file__))
pro_dir: str = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
res_dir: str = os.path.join(pro_dir, 'res')
flow_size_res_dir: str = os.path.join(res_dir, 'flow_size')
graph_size_res_dir: str = os.path.join(res_dir, 'graph_size')
redundancy_res_dir: str = os.path.join(res_dir, 'redundancy')
solutions_res_dir: str = os.path.join(res_dir, 'solutions')
json_dir: str = os.path.join(src_dir, 'json')
flows_filename: str = os.path.join(json_dir, 'flows.json')

GRAPH_CONFIG = {
    'min-flow-size': 64 * 8,  # minimum frame size = 64B, [unit: Byte]
    'hyper-period': int(3e5),  # 300us = 3e5ns, [unit: ns],
    'all-bandwidth': int(1e0),  # 1Gbps = 1bit/ns, [unit: bpns]
    'max-bandwidth': int(1e0),  # maximum bandwidth of all edges
    'overlapped-routing': True,  # whether routing with overlapping or not
    'time-granularity': TIME_GRANULARITY.NS,  # time granularity, default is ns
    'edge-nodes-distribution-degree': 6,  # distribution degree of edge nodes
    'core-node-num': 10,  # [2, 4, 6, ..., 20]
    'edge-node-num': 10,
    'topo-strategy': [
        {
            'strategy': TOPO_STRATEGY.ER_STRATEGY,
            'type': ErdosRenyiStrategy.ER_TYPE.GNP,
            'n': 10,
            'm': 14,
            'p': 0.2,
        },
        {
            'strategy': TOPO_STRATEGY.BA_STRATEGY,
            'n': 10,
            'm': 2,
        },
        {
            'strategy': TOPO_STRATEGY.RRG_STRATEGY,
            'd': 3,
            'n': 10,
        },
        {
            'strategy': TOPO_STRATEGY.WS_STRATEGY,
            'n': 10,
            'k': 2,
            'p': 1.0,
        },
    ],
    'routing-strategy': ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY,
    'scheduling-strategy': SCHEDULING_STRATEGY.LRF_RRDUNDANT_SCHEDULING_STRATEGY,
    'allocating-strategy': ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY,
    'max-try-times': 50,  # max retry times if the graph is not connected,
    'visible': False,  # whether visualizing or not
}

FLOW_CONFIG = {
    'flow-num': 100,  # number of flow
    'dest-num-set': [1, 2, 3],  # set of the number of destination nodes
    'period-set': [int(1e5), int(1.5e5), int(3e5)],  # set of period, 周期能被最大周期整除
    'hyper-period': int(3e5),  # 300us = 3e5ns, [unit: ns],
    'size-set': [int(1.5e3), int(5e3), int(1e3)],  # 1500bit, [unit: bit],
    'reliability-set': [0.97, 0.98, 0.99],
    'deadline-set': [int(1e8), int(5e7), int(2e7)]
}

OPTIMIZATION = {
    'enable': False,  # whether enable optimization or not
    'flows-generator': False,  # whether generate new flows or not
    'max_iterations': 50,  # maximum iteration times
    'max_no_improve': 1,  # maximum local search width
    'k': 0.3,  # ratio of removed flows
    'results-root-path': '/src/json/'  # root path of results
}

XML_CONFIG = {
    'tsn_host_pre_name': 'Host',  # prefix of tsn termination host
    'tsn_switch_pre_name': 'Switch',  # prefix of tsn
    'one-flow-one-host': False,  # whether one flow corresponds one host or not
    'multicast-model': True,  # whether all flow follow multicast transmission mode or not
    'static': True,  # whether static forwarding or not
    'enhancement-tsn-switch-enable': True,  # whether enable enhancement function of tsn switch or not
}

TESTING = {
    'round': 5,  # test rounds
    'x-axis-gap': 5,
    'prefix': 1,
    'flow-size': [10, 100],  # the least number of flows
    'draw-gantt-chart': False,
    'save-solution': False,
    'graph-core-size': [10, 20],
    'graph-edge-size': [],
    'generate-flows': False
}
