import copy
import logging
import os
from enum import Enum
from typing import List, Dict, Tuple

import jinja2

from src import config
from src.graph.Flow import Flow
from src.graph.Solver import Solution
from src.net_envs.network.TSNNetwork import TSNNetwork
from lxml import html

from src.net_envs.network_component.FilteringDatabase import FilteringDatabase
from src.net_envs.network_component.GateControlList import EnhancementGateControlList, GateControlList, \
    GateControlListItem, EnhancementGateControlListItem
from src.net_envs.network_component.Mac import MAC_TYPE
from src.net_envs.network_configurator.ConfigurationInfo import ConfigurationInfo, GateControlListConfigurationInfo
from src.net_envs.network_element.NetworkDevice import NetworkDevice
from src.net_envs.network_element.TSNHost import TSNHost, TSNFlowInfo
from src.net_envs.network_element.TSNSwitch import TSNSwitch
from src.type import NodeId, MacAddress, PortNo, SimTime, FlowId, EdgeId
import src.utils.MacAddressGenerator as MAG

etree = html.etree  # ???
logger = logging.getLogger(__name__)


class ConfigFileGenerator:

    @staticmethod
    def generate_routes_xml(tsn_network: TSNNetwork) -> str:
        tsn_switch_list: List[TSNSwitch] = tsn_network.tsn_switch_list
        root: etree.Element = etree.Element('filteringDatabases')
        for tsn_switch in tsn_switch_list:
            tsn_switch_id: NodeId = tsn_switch.device_id
            filtering_database: FilteringDatabase = tsn_switch.filtering_database
            xml_filtering_database: etree.Element = etree.SubElement(root, 'filteringDatabase')
            xml_filtering_database.attrib['id'] = 'switch{}'.format(tsn_switch_id)
            if filtering_database.static is True:
                xml_static: etree.Element = etree.SubElement(xml_filtering_database, 'static')
                xml_forward: etree.Element = etree.SubElement(xml_static, 'forward')
                for filtering_database_item in filtering_database.items:
                    mac: MacAddress = filtering_database_item.mac
                    mac_type: MAC_TYPE = filtering_database_item.mac_type
                    ports: List[PortNo] = filtering_database_item.ports
                    ports_str: str = ''
                    for port_no in ports:
                        ports_str += ' ' + str(port_no - 1)
                    ports_str = ports_str.lstrip()
                    if mac_type == MAC_TYPE.UNICAST:
                        xml_filtering_database_item: etree.Element = etree.SubElement(xml_forward, 'individualAddress')
                        xml_filtering_database_item.attrib['port'] = ports_str
                    elif mac_type == MAC_TYPE.MULTICAST:
                        xml_filtering_database_item: etree.Element = etree.SubElement(xml_forward, 'multicastAddress')
                        xml_filtering_database_item.attrib['ports'] = ports_str
                    elif mac_type == MAC_TYPE.BROADCAST:
                        xml_filtering_database_item: etree.Element = etree.SubElement(xml_forward, 'broadcastAddress')
                        xml_filtering_database_item.attrib['ports'] = ports_str
                    else:
                        raise RuntimeError('unknown mac type')
                    xml_filtering_database_item.attrib['macAddress'] = mac
            else:
                # TODO non-static situation
                pass
        routes_content: str = str(
            etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'), encoding='utf-8')
        logger.info('\n' + routes_content)
        return routes_content

    @staticmethod
    # TODO flat and hierarchical xml
    def generate_switch_schedule_xml(tsn_network: TSNNetwork) -> str:
        tsn_switch_list: List[TSNSwitch] = tsn_network.tsn_switch_list
        # <root></root>
        root: etree.Element = etree.Element('schedule')
        # <!--time-->
        if config.GRAPH_CONFIG['time-granularity'] is config.TIME_GRANULARITY.NS:
            xml_time_comment: etree.Comment = etree.Comment('ns')
        elif config.GRAPH_CONFIG['time-granularity'] is config.TIME_GRANULARITY.US:
            xml_time_comment: etree.Comment = etree.Comment('us')
        elif config.GRAPH_CONFIG['time-granularity'] is config.TIME_GRANULARITY.MS:
            xml_time_comment: etree.Comment = etree.Comment('ms')
        elif config.GRAPH_CONFIG['time-granularity'] is config.TIME_GRANULARITY.S:
            xml_time_comment: etree.Comment = etree.Comment('s')
        else:
            raise RuntimeError('unknown time type')
        root.append(copy.copy(xml_time_comment))
        # <cycle></cycle>
        xml_cycle: etree.Element = etree.Element('cycle')
        xml_cycle.text = str(config.GRAPH_CONFIG['hyper-period'])
        root.append(xml_cycle)
        for tsn_switch in tsn_switch_list:
            # <switch></switch>
            xml_switch: etree.Element = etree.Element('switch')
            xml_switch.attrib['name'] = 'switch{}'.format(tsn_switch.device_id)
            root.append(xml_switch)
            # if tsn_switch.port_gate_control_list.__len__() == 0:  # this port has no gcl
            #     break
            for port_no, gcl in tsn_switch.port_gate_control_list.items():
                assert gcl.items.__len__() != 0, 'incorrect gate control list'
                # <port></port>
                xml_port: etree.Element = etree.Element('port')
                xml_port.attrib['id'] = str(port_no - 1)
                xml_switch.append(xml_port)
                for gcl_item in gcl.items:
                    # <entry></entry>
                    xml_entry: etree.Element = etree.Element('entry')
                    xml_port.append(xml_entry)
                    # <!--time-->
                    xml_entry.append(copy.copy(xml_time_comment))
                    # <length></length>
                    xml_length: etree.Element = etree.Element('length')
                    xml_length.text = str(gcl_item.time)
                    xml_entry.append(xml_length)
                    # <bitvector></bitvector>
                    xml_bitvector: etree.Element = etree.Element('bitvector')
                    xml_bitvector.text = gcl_item.gate_states.to01()
                    xml_entry.append(xml_bitvector)
                    if type(gcl_item) is EnhancementGateControlListItem:  # enhancement extension
                        # <uniqueID></uniqueID>
                        xml_unique_id: etree.Element = etree.Element('uniqueID')
                        xml_unique_id.text = str(gcl_item.flow_id)
                        xml_entry.append(xml_unique_id)
                        # <phase></phase>
                        xml_phase: etree.Element = etree.Element('phase')
                        xml_phase.text = str(gcl_item.phase)
                        xml_entry.append(xml_phase)
        schedule_switch_content: str = str(
            etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'), encoding='utf-8')
        logger.info('\n' + schedule_switch_content)
        return schedule_switch_content

    @staticmethod
    def generate_host_schedule_xml(tsn_network: TSNNetwork) -> Dict[NodeId, Dict[FlowId, str]]:
        tsn_host_list: List[TSNHost] = tsn_network.tsn_host_list
        hosts_content: Dict[NodeId, Dict[FlowId, str]] = {}
        for tsn_host in tsn_host_list:
            # if tsn_host.port_gate_control_list.__len__() == 0:  # this port has no gcl
            #     break
            flows_content: Dict[FlowId, str] = {}
            for tsn_flow_info in tsn_host.tsn_flow_info_list:
                # <root></root>
                root: etree.Element = etree.Element('schedule')
                # <!--time-->
                if config.GRAPH_CONFIG['time-granularity'] is config.TIME_GRANULARITY.NS:
                    xml_time_comment: etree.Comment = etree.Comment('ns')
                elif config.GRAPH_CONFIG['time-granularity'] is config.TIME_GRANULARITY.US:
                    xml_time_comment: etree.Comment = etree.Comment('us')
                elif config.GRAPH_CONFIG['time-granularity'] is config.TIME_GRANULARITY.MS:
                    xml_time_comment: etree.Comment = etree.Comment('ms')
                elif config.GRAPH_CONFIG['time-granularity'] is config.TIME_GRANULARITY.S:
                    xml_time_comment: etree.Comment = etree.Comment('s')
                else:
                    raise RuntimeError('unknown time type')
                root.append(copy.copy(xml_time_comment))
                # <cycle></cycle>
                xml_cycle: etree.Element = etree.Element('cycle')
                xml_cycle.text = str(tsn_flow_info.cycle_time)
                root.append(xml_cycle)
                # <!-- flow-id=fid -->
                xml_flow_id_comment: etree.Comment = etree.Comment('flow-id={}'.format(tsn_flow_info.flow_id))
                root.append(xml_flow_id_comment)
                # <host></host>
                xml_host: etree.Element = etree.Element('host')
                xml_host.attrib['name'] = 'host{}'.format(tsn_host.device_id)
                root.append(xml_host)
                xml_entry: etree.Element = etree.Element('entry')
                xml_host.append(xml_entry)
                # <start></start>
                xml_start: etree.Element = etree.Element('start')
                xml_start.text = str(tsn_flow_info.start_time)
                xml_entry.append(xml_start)
                # <queue></queue>
                xml_queue: etree.Element = etree.Element('queue')
                xml_queue.text = str(tsn_flow_info.queue)
                xml_entry.append(xml_queue)
                # <dest></dest>
                xml_dest: etree.Element = etree.Element('dest')
                xml_dest.text = str(tsn_flow_info.dest_mac)
                xml_entry.append(xml_dest)
                # <size></size>
                xml_size: etree.Element = etree.Element('size')
                xml_size.text = str(int(tsn_flow_info.size / 8) - 50)  # TODO bit to byte and reduce overhead
                xml_entry.append(xml_size)
                # enhancement part
                # <group></group>
                xml_group: etree.Element = etree.Element('group')
                xml_group.text = str(tsn_flow_info.group_mac)  # TODO get group mac
                xml_entry.append(xml_group)
                # <uniqueID></uniqueID>
                xml_uniqueID: etree.Element = etree.Element('uniqueID')
                xml_uniqueID.text = str(tsn_flow_info.flow_id)
                xml_entry.append(xml_uniqueID)
                # <phase></phase>
                xml_phase: etree.Element = etree.Element('phase')
                xml_phase.text = str(0)
                xml_entry.append(xml_phase)
                #
                flow_content: str = str(
                    etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'), encoding='utf-8')
                flows_content[tsn_flow_info.flow_id] = flow_content
                logger.info('\n' + flow_content)
            hosts_content[tsn_host.device_id] = flows_content
        return hosts_content

    @staticmethod
    def generate_flows_xml(flows: List[Flow]) -> str:
        # <flows></flows>
        root_xml: etree.Element = etree.Element('flows')
        for flow in flows:
            flow_xml: etree.Element = etree.Element('flow')
            flow_xml.attrib['id'] = str(flow.flow_id)
            flow_xml.attrib['source'] = str(flow.source)
            _D: str = ''
            for d in flow.destinations:
                _D += str(d) + ' '
            _D = _D.rstrip()
            flow_xml.attrib['destination'] = _D
            flow_xml.attrib['size'] = str(int(flow.size / 8) - 50)  # bit to byte
            flow_xml.attrib['cycle'] = str(flow.period)
            flow_xml.attrib['deadline'] = str(flow.deadline)
            flow_xml.attrib['reliability'] = str(flow.reliability)
            root_xml.append(flow_xml)
        # TODO save to file

        flows_xml_str: str = str(
            etree.tostring(root_xml, pretty_print=True, xml_declaration=True, encoding='utf-8'), encoding='utf-8')
        logger.info('\n' + flows_xml_str)
        return flows_xml_str

    @staticmethod
    def load_template(template_dir: str, template_filename: str):
        template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(template_filename)
        return template

    @staticmethod
    def generate_ini_file(network_name: str = 'TestScenario', flows: List[Flow] = None) -> str:
        if network_name == '':
            raise RuntimeError('parameter "network_name" is required')
        flows = flows if flows is not None else []
        hosts: List[dict] = []
        for flow in flows:
            items: List[dict] = list(filter(lambda host: host['host_id'] == flow.source, hosts))
            if len(items) != 0:
                item: dict = items[0]
                item['flows'].append({'flow_id': flow.flow_id})
            else:
                hosts.append({'host_id': flow.source, 'flows': [{'flow_id': flow.flow_id}]})
        # get template
        template: jinja2.Template = ConfigFileGenerator.load_template(config.template_dir, 'test_scenario_template.ini')
        return template.render(
            network_name=network_name,
            time_granularity='1ns',
            process_delay='0us',
            hosts=hosts
        )

    @staticmethod
    def generate_ned_file(tsn_network: TSNNetwork = None, flows: List[Flow] = None, solution: Solution = None,
                          node_edge_mac_info: MAG.NodeEdgeMacInfo = None) -> str:
        node_edge_port_pair_list: Dict[NodeId, List[Tuple[EdgeId, PortNo]]] = {}
        nodes: List[NetworkDevice] = tsn_network.tsn_switch_list + tsn_network.tsn_host_list
        for node in nodes:
            edge_port_pair_list: List[Tuple[EdgeId, PortNo]] = \
                GateControlListConfigurationInfo.generate_edge_port_pair_list(
                    node_id=node.device_id, node_edge_mac_info=node_edge_mac_info, ports=node.ports)
            node_edge_port_pair_list[node.device_id] = edge_port_pair_list
        # TSN hosts
        tsn_hosts: List[TSNHost] = tsn_network.tsn_host_list
        hosts: List[Dict] = []
        hosts_id: List[NodeId] = []
        for tsn_host in tsn_hosts:
            host: Dict = {'host_id': tsn_host.device_id, 'port_num': len(tsn_host.ports)}
            hosts_id.append(tsn_host.device_id)
            ports: List[Dict] = []
            for port in tsn_host.ports:
                forward_edge_id: EdgeId = \
                    list(filter(lambda edge_port_pair: edge_port_pair[1] == port.port_id,
                                node_edge_port_pair_list[tsn_host.device_id]))[0][0]
                peer_node_id: NodeId = NodeId(solution.graph.edge_mapper[forward_edge_id].out_node.node_id)
                backward_edge_id: EdgeId = list(filter(
                    lambda eid: solution.graph.edge_mapper[eid].out_node.node_id == tsn_host.device_id and
                                solution.graph.edge_mapper[eid].in_node.node_id == peer_node_id,
                    solution.graph.edge_mapper))[0]
                peer_port_id: PortNo = list(filter(lambda edge_port_pair: edge_port_pair[0] == backward_edge_id,
                                                       node_edge_port_pair_list[peer_node_id]))[0][1]
                port: Dict = \
                    {'port_id': port.port_id - 1, 'peer_node_id': peer_node_id, 'peer_port_id': peer_port_id - 1}
                ports.append(port)
            host['ports'] = ports
            hosts.append(host)
        # TSN switches
        tsn_switches: List[TSNSwitch] = tsn_network.tsn_switch_list
        switches: List[Dict] = []
        for tsn_switch in tsn_switches:
            switch: Dict = {'switch_id': tsn_switch.device_id, 'port_num': len(tsn_switch.ports)}
            ports: List[Dict] = []
            for port in tsn_switch.ports:
                forward_edge_id: EdgeId = \
                    list(filter(lambda edge_port_pair: edge_port_pair[1] == port.port_id,
                                node_edge_port_pair_list[tsn_switch.device_id]))[0][0]
                peer_node_id: NodeId = NodeId(solution.graph.edge_mapper[forward_edge_id].out_node.node_id)
                if peer_node_id in hosts_id:
                    continue
                backward_edge_id: EdgeId = list(filter(
                    lambda eid: solution.graph.edge_mapper[eid].out_node.node_id == tsn_switch.device_id and
                                solution.graph.edge_mapper[eid].in_node.node_id == peer_node_id,
                    solution.graph.edge_mapper))[0]
                peer_port_id: PortNo = list(filter(lambda edge_port_pair: edge_port_pair[0] == backward_edge_id,
                                                   node_edge_port_pair_list[peer_node_id]))[0][1]
                port: Dict = \
                    {'port_id': port.port_id - 1, 'peer_node_id': peer_node_id, 'peer_port_id': peer_port_id - 1}
                ports.append(port)
            switch['ports'] = ports
            switches.append(switch)
        # load template
        template: jinja2.Template = ConfigFileGenerator.load_template(config.template_dir, 'test_scenario_template.ned')
        return template.render(
            solution_name=solution.solution_name.lower(),
            simlation_time='{}s'.format(config.TESTING['simulation-time']),
            hosts=hosts,
            switches=switches,
            link={'delay': '{}ns'.format(config.GRAPH_CONFIG['all-propagation-delay']),
                  'datarate': '{}Gbps'.format(config.GRAPH_CONFIG['all-bandwidth']),
                  'per': '{}'.format(config.GRAPH_CONFIG['all-per'])})

    @staticmethod
    def create_test_scenario(tsn_network: TSNNetwork = None,
                             solution: Solution = None,
                             node_edge_mac_info: MAG.NodeEdgeMacInfo = None,
                             test_scenario_dirname: str = None):
        if test_scenario_dirname is not None:
            config.test_scenario_res_dir = test_scenario_dirname
        if not os.path.exists(config.test_scenario_res_dir):
            os.makedirs(config.test_scenario_res_dir)
        test_scenario_dir = os.path.join(config.test_scenario_res_dir, solution.solution_name.lower())
        # generate content
        ini_file_content: str = ConfigFileGenerator.generate_ini_file(flows=solution.flows)
        ned_file_content: str = ConfigFileGenerator.generate_ned_file(tsn_network=tsn_network,
                                                                      solution=solution,
                                                                      node_edge_mac_info=node_edge_mac_info)
        flows_flat_file_content: str = ConfigFileGenerator.generate_flows_xml(flows=solution.flows)
        routes_flat_file_content: str = ConfigFileGenerator.generate_routes_xml(tsn_network=tsn_network)
        GCLs_flat_file_conent: str = ConfigFileGenerator.generate_switch_schedule_xml(tsn_network=tsn_network)
        hosts_flows_content: Dict[NodeId, Dict[FlowId, str]] = \
            ConfigFileGenerator.generate_host_schedule_xml(tsn_network=tsn_network)
        # generate dirname and filename
        if os.path.exists(test_scenario_dir):
            # remove directories and files
            remove_dir(test_scenario_dir)
        ned_filename: str = os.path.join(test_scenario_dir, '{}.ned'.format(solution.solution_name.lower()))
        ini_filename: str = os.path.join(test_scenario_dir, '{}.ini'.format(solution.solution_name.lower()))
        results_dir: str = os.path.join(test_scenario_dir, 'results')
        xml_dir: str = os.path.join(test_scenario_dir, 'xml')
        flows_dir: str = os.path.join(xml_dir, 'flows')
        flows_flat_filename: str = os.path.join(flows_dir, 'flows_flat.xml')
        routes_dir: str = os.path.join(xml_dir, 'routes')
        routes_flat_filename: str = os.path.join(routes_dir, 'routes_flat.xml')
        schedules_dir: str = os.path.join(xml_dir, 'schedules')
        hosts_dir: str = os.path.join(schedules_dir, 'hosts')
        hosts_flows_file: Dict[str, Dict[str, str]] = {}  # Dict[HostName, Dict[FlowFilename, FileContent]]
        for host_id, host_content in hosts_flows_content.items():
            flows: Dict[str, str] = {}
            host_dir: str = os.path.join(hosts_dir, 'host{}'.format(host_id))
            for flow_id, flow_content in host_content.items():
                flow_filename: str = os.path.join(host_dir, 'flow{}.xml'.format(flow_id))
                flows[flow_filename] = flow_content
            hosts_flows_file[host_dir] = flows
        switches_dir: str = os.path.join(schedules_dir, 'switches')
        GCLs_flat_filename: str = os.path.join(switches_dir, 'GCLs_flat.xml')
        # create and write
        os.makedirs(test_scenario_dir)
        write_file(ned_filename, ned_file_content)
        write_file(ini_filename, ini_file_content)
        os.makedirs(results_dir)
        os.makedirs(xml_dir)
        os.makedirs(flows_dir)
        write_file(flows_flat_filename, flows_flat_file_content)
        os.makedirs(routes_dir)
        write_file(routes_flat_filename, routes_flat_file_content)
        os.makedirs(schedules_dir)
        os.makedirs(switches_dir)
        write_file(GCLs_flat_filename, GCLs_flat_file_conent)
        os.makedirs(hosts_dir)
        for host_dir, flows in hosts_flows_file.items():
            os.makedirs(host_dir)
            for flow_filename, file_content in flows.items():
                write_file(flow_filename, file_content)


def write_file(filename: str, file_content: str):
    with open(filename, 'w') as f:
        f.write(file_content)


def remove_dir(dir: str):
    import os
    dir = dir.replace('\\', '/')
    if os.path.isdir(dir):
        for p in os.listdir(dir):
            remove_dir(os.path.join(dir, p))
        if os.path.exists(dir):
            os.rmdir(dir)
    else:
        if os.path.exists(dir):
            os.remove(dir)
