GRAPH_CONFIG = {
    'min-flow-size': 64 * 8,  # minimum frame size = 64B, [unit: Byte]
    'hyper-period': int(3e5),  # 300us = 3e5ns, [unit: ns],
    'all-bandwidth': int(1e0),  # 1Gbps = 1bit/ns, [unit: bpns]
    'max-bandwidth': int(1e0),  # maximum bandwidth of all edges
    'overlapped-routing': True,  # whether routing with overlapping or not
}

OPTIMIZATION = {
    'flows-generator': False,  # whether generate new flows or not
    'max_iterations': 5,  # maximum iteration times
    'max_no_improve': 5,  # maximum local search width
    'k': 0.3,  # ratio of removed flows
}
