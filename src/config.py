import os
from enum import Enum

from src.type import ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY

TIME_GRANULARITY = Enum('TIME_GRANULARITY', ('NS, US, MS, S'))

src_dir: str = os.path.dirname(os.path.abspath(__file__))
pro_dir: str = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))


GRAPH_CONFIG = {
    'min-flow-size': 64 * 8,  # minimum frame size = 64B, [unit: Byte]
    'hyper-period': int(3e5),  # 300us = 3e5ns, [unit: ns],
    'all-bandwidth': int(1e0),  # 1Gbps = 1bit/ns, [unit: bpns]
    'max-bandwidth': int(1e0),  # maximum bandwidth of all edges
    'overlapped-routing': True,  # whether routing with overlapping or not
    'time-granularity': TIME_GRANULARITY.NS,  # time granularity, default is ns
    'routing-strategy': ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY,
    'scheduling-strategy': SCHEDULING_STRATEGY.LRF_RRDUNDANT_SCHEDULING_STRATEGY,
    'allocating-strategy': ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY,
    'max-try-times': 50,  # max retry times if the graph is not connected
}

FLOW_CONFIG = {
    'flow-num': 0,  # number of flow
    'dest-num-set': [1, 2, 3],  # set of the number of destination nodes
    'period-set': [int(1e5), int(2e5), int(5e5), int(1e6)],  # set of period, 周期能被最大周期整除
    'size-set': [int(2e4), int(1e5), int(5e4)],
    'reliability-set': [0.97, 0.98, 0.99],
    'deadline-set': [int(1e8), int(5e7), int(2e7)]
}

OPTIMIZATION = {
    'flows-generator': False,  # whether generate new flows or not
    'max_iterations': 5,  # maximum iteration times
    'max_no_improve': 5,  # maximum local search width
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
