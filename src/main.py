import sys
import logging
import os
import copy
from typing import List, Tuple, Dict

from src.graph.Graph import Graph
from src.graph.Flow import Flow
from src.type import MacAddress, EdgeId
from src.utils.SaveHelper import SaveHelper
from src.utils.Visualizer import Visualizer
from src.utils.FlowGenerator import FlowGenerator
from src.graph.Solver import Solver, Solution
from src.utils import MacAddressGenerator as mag
from src.utils import RoutesGenerator as rg
from src import config

logger = logging.getLogger(__name__)

'''
time unit: s/ms/us/ns, 1s = 1e3ms = 1e6us = 1e9ns
length unit: Gb/Mb/Kb/b, 1Gb = 1e3Mb = 1e6Kb = 1e9b
'''
HYPER_PERIOD = int(3e5)  # 300us = 3e5ns, [unit: ns]
IDEAL_BANDWIDTH = int(1e0)  # 1Gbps = 1bit/ns, [unit: bpns]


def main():
    # test()  # fixed flows
    # test_2()  # random flows
    # test_v()  # visualizer
    test_mac_address_generator()
    # test_import_module()


def test():
    nodes: List[int] = [1, 2, 3, 4, 5, 6, 7]
    edges: List[Tuple[int]] = [(1, 2), (2, 1), (2, 3), (3, 2), (2, 4), (4, 2), (3, 4), (4, 3), (3, 5), (5, 3), (4, 5),
                               (5, 4), (5, 6), (6, 5), (5, 7), (7, 5)]
    g: Graph = Graph(nodes=nodes, edges=edges, hp=config.GRAPH_CONFIG['hyper-period'])
    g.set_all_edges_bandwidth(config.GRAPH_CONFIG['all-bandwidth'])
    gc: Graph = copy.deepcopy(g)

    # fid = 1, size = 8Kb, period = 300us, source = 1, destinations = [6, 7], reliability = 0.0, deadline = 300us
    f1: Flow = Flow(1, int(8e3), int(3e5), 1, [6, 7], 0.0, int(1e6))
    # fid = 1, size = 20Kb, period = 150us, source = 1, destinations = [6], reliability = 0.0, deadline = 150us
    f2: Flow = Flow(2, int(2e4), int(1.5e5), 1, [6], 0.0, int(1e6))
    # fid = 1, size = 30Kb, period = 150us, source = 1, destinations = [6, 7], reliability = 0.0, deadline = 300us
    f3: Flow = Flow(3, int(3e4), int(3e5), 1, [6, 7], 0.0, int(1e6))
    # fid = 1, size = 2Kb, period = 150us, source = 1, destinations = [7], reliability = 0.0, deadline = 300us
    f4: Flow = Flow(4, int(2e3), int(3e5), 1, [7], 0.0, int(1e6))

    fs: List[Flow] = list()
    fs.append(f1)
    fs.append(f2)
    fs.append(f3)
    fs.append(f4)

    Solver.generate_init_solution(nodes, edges, fs)
    Solver.optimize(config.OPTIMIZATION['max_iterations'], config.OPTIMIZATION['max_no_improve'],
                    config.OPTIMIZATION['k'])

    f_json = FlowGenerator.flows2json(fs)
    path = os.path.join(os.path.abspath('.'), 'json')
    path = os.path.join(path, 'flows.json')
    with open(path, "w") as f:
        f.write(f_json)
    with open(path, "r") as f:
        f_json = f.read()
        _fs = FlowGenerator.json2flows(f_json)
        for _f in _fs:
            _f.to_string()


def test_2():
    nodes: List[int] = [1, 2, 3, 4, 5, 6, 7]
    edges: List[Tuple[int]] = [(1, 2), (2, 1), (2, 3), (3, 2), (2, 4), (4, 2), (3, 4), (4, 3), (3, 5), (5, 3), (4, 5),
                               (5, 4), (5, 6), (6, 5), (5, 7), (7, 5)]

    path = os.path.join(os.path.abspath('.'), 'json')
    path = os.path.join(path, 'flows.json')

    if config.OPTIMIZATION['flows-generator'] is True:
        _F: List[Flow] = FlowGenerator.generate_r(
            n=20, hn=[1, 6, 7], s=[int(1e4), int(2e4)], p=[int(1e5), int(6e5)], dn=[1, 2], rl=[0.0, 0.0], dl=[0, 0])
        for _f in _F:
            _f.to_string()

        _json = FlowGenerator.flows2json(_F)

        with open(path, "w") as f:
            f.write(_json)

    with open(path, "r") as f:
        _json = f.read()
        _fs = FlowGenerator.json2flows(_json)

    Solver.generate_init_solution(nodes, edges, _fs)
    Solver.optimize(config.OPTIMIZATION['max_iterations'], config.OPTIMIZATION['max_no_improve'],
                    config.OPTIMIZATION['k'])


def test_v():
    Visualizer.test_2()


def test_mac_address_generator():
    nodes: List[int] = [1, 2, 3, 4, 5, 6, 7]
    edges: List[Tuple[int]] = [(1, 2), (2, 1), (2, 3), (3, 2), (2, 4), (4, 2), (3, 4), (4, 3), (3, 5), (5, 3), (4, 5),
                               (5, 4), (5, 6), (6, 5), (5, 7), (7, 5)]
    f1: Flow = Flow(1, int(8e3), int(3e5), 1, [6, 7], 0.0, int(1e6))
    f2: Flow = Flow(2, int(2e4), int(1.5e5), 1, [6], 0.0, int(1e6))
    f3: Flow = Flow(3, int(3e4), int(3e5), 1, [6, 7], 0.0, int(1e6))
    f4: Flow = Flow(4, int(2e3), int(3e5), 1, [7], 0.0, int(1e6))
    flow_list: List[Flow] = list()
    flow_list.append(f1)
    flow_list.append(f2)
    flow_list.append(f3)
    flow_list.append(f4)

    s: Solution = Solver.generate_init_solution(nodes, edges, flow_list, visual=False)
    # Solver.optimize(config.OPTIMIZATION['max_iterations'], config.OPTIMIZATION['max_no_improve'],
    #                 config.OPTIMIZATION['k'], visual=False)

    mac_list: List[MacAddress] = mag.MacAddressGenerator.generate_all_multicast_mac_address(s.graph)
    [print(mac) for mac in mac_list]
    logger.info('Mac List:' + str(mac_list))
    edge_mac_dict: Dict[EdgeId, mag.EdgeMacMapper] = \
        mag.MacAddressGenerator.assign_mac_address_to_edge(mac_list, s.graph)
    [print(str(edge_mac.edge_id) + ': ' + edge_mac.mac_pair[0] + ',' + edge_mac.mac_pair[1]) for edge_mac in
     edge_mac_dict.values()]
    logger.info('Edge Mac Dict: ' + str(edge_mac_dict))
    route_immediate_entity: rg.RouteImmediateEntity = \
        rg.RoutesGenerator.generate_routes_immediate_entity(s.graph, flow_list, edge_mac_dict)
    json_str: str = rg.RoutesGenerator.serialize_to_json(route_immediate_entity)
    logger.info('Routes Json: ' + str(json_str))
    node_mac_dict: Dict[int, mag.NodeMacMapper] = mag.MacAddressGenerator.assign_mac_address_to_node(edge_mac_dict)
    logger.info('Node Mac Dict: ' + str(node_mac_dict))


def test_import_module():
    m = __import__('src.net_elem.NetworkDevice', fromlist=['NetworkDevice'])
    _C = getattr(m, 'NetworkDevice')
    print(_C)
    _C(1, '')


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    main()
