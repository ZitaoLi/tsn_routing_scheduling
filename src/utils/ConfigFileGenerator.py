import copy
import logging
from enum import Enum
from typing import List

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
from src.net_envs.network_element.TSNHost import TSNHost, TSNFlowInfo
from src.net_envs.network_element.TSNSwitch import TSNSwitch
from src.type import NodeId, MacAddress, PortNo, SimTime, FlowId

etree = html.etree  # ???
logger = logging.getLogger(__name__)


class ConfigFileGenerator:

    @staticmethod
    def generate_routes_xml(tsn_network: TSNNetwork):
        tsn_switch_list: List[TSNSwitch] = tsn_network.tsn_switch_list
        root: etree.Element = etree.Element('filteringDatabases')
        for tsn_switch in tsn_switch_list:
            tsn_switch_id: NodeId = tsn_switch.device_id
            filtering_database: FilteringDatabase = tsn_switch.filtering_database
            xml_filtering_database: etree.Element = etree.SubElement(root, 'filteringDatabase')
            xml_filtering_database.attrib['id'] = str(tsn_switch_id)
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
                    elif mac_type == MAC_TYPE.MULTICAST:
                        xml_filtering_database_item: etree.Element = etree.SubElement(xml_forward, 'multicastAddress')
                    elif mac_type == MAC_TYPE.BROADCAST:
                        xml_filtering_database_item: etree.Element = etree.SubElement(xml_forward, 'broadcastAddress')
                    else:
                        raise RuntimeError('unknown mac type')
                    xml_filtering_database_item.attrib['macAddress'] = mac
                    xml_filtering_database_item.attrib['ports'] = ports_str
            else:
                # TODO non-static situation
                pass
        logger.info('\n' + str(
            etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'), encoding='utf-8'))
        # TODO save to file

    @staticmethod
    # TODO flat and hierarchical xml
    def generate_switch_schedule_xml(tsn_network: TSNNetwork):
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
            xml_switch.attrib['name'] = tsn_switch.device_name
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
        logger.info('\n' + str(
            etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'), encoding='utf-8'))
        # TODO save to file

    @staticmethod
    def generate_host_schedule_xml(tsn_network: TSNNetwork):
        tsn_host_list: List[TSNHost] = tsn_network.tsn_host_list
        for tsn_host in tsn_host_list:
            # if tsn_host.port_gate_control_list.__len__() == 0:  # this port has no gcl
            #     break
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
                xml_host.attrib['name'] = 'flow'
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
                xml_size.text = str(tsn_flow_info.size)
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
                # TODO save to file

                logger.info('\n' + str(
                    etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'), encoding='utf-8'))

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
            flow_xml.attrib['size'] = str(flow.size)
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
    def generate_ini_file(network_name: str = '', flows: List[Flow] = None) -> str:
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
    def generate_ned_file():
        pass
