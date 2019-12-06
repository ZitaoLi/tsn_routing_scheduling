import copy
import logging
from enum import Enum
from typing import List

from src import config
from src.graph.Flow import Flow
from src.net_envs.network.TSNNetwork import TSNNetwork
from lxml import html

from src.net_envs.network_component.FilteringDatabase import FilteringDatabase
from src.net_envs.network_component.GateControlList import EnhancementGateControlList, GateControlList, \
    GateControlListItem, EnhancementGateControlListItem
from src.net_envs.network_component.Mac import MAC_TYPE
from src.net_envs.network_element.TSNHost import TSNHost
from src.net_envs.network_element.TSNSwitch import TSNSwitch
from src.type import NodeId, MacAddress, PortNo, SimTime

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
            if tsn_switch.port_gate_control_list.__len__() == 0:  # this port has no gcl
                break
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
    def generate_host_schedule_xml(tsn_network: TSNNetwork, flows: List[Flow]):
        tsn_host_list: List[TSNHost] = tsn_network.tsn_host_list
        for tsn_host in tsn_host_list:
            if tsn_host.port_gate_control_list.__len__() == 0:  # this port has no gcl
                break
            # TODO
            for port_no, gcl in tsn_host.port_gate_control_list.items():
                assert gcl.items.__len__() != 0, 'incorrect gate control list'
                start_time: SimTime = SimTime(0)
                for gcl_item in gcl:
                    if gcl_item.flow_id == 0:
                        start_time += gcl_item.time
                        continue
                    _F: List[Flow] = list(filter(lambda f: f.flow_id == gcl_item.flow_id, flows))
                    if _F is None or len(_F) == 0:
                        raise RuntimeError('flow [{}] does not exist'.format(gcl_item.flow_id))
                    flow: Flow = _F[0]
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
                    xml_cycle.text = flow.period
                    root.append(xml_cycle)
                    # <!-- flow-id=fid -->
                    xml_flow_id_comment: etree.Comment = etree.Comment('flow-id={}'.format(flow.flow_id))
                    root.append(xml_flow_id_comment)
                    # <host></host>
                    xml_host: etree.Element = etree.Element('host')
                    xml_host.attrib['name'] = 'flow'
                    root.append(xml_host)
                    xml_entry: etree.Element = etree.Element('entry')
                    xml_host.append(xml_entry)
                    # <start></start>
                    xml_start: etree.Element = etree.Element('start')
                    xml_start.text = start_time
                    xml_entry.append(xml_start)
                    # <queue></queue>
                    xml_queue: etree.Element = etree.Element('queue')
                    xml_queue.text = 7
                    xml_entry.append(xml_queue)
                    # <dest></dest>

                    # <size></size>
                    if type(gcl) is EnhancementGateControlList:
                        # <group></group>
                        # <uniqueID></uniqueID>
                        # <phase></phase>
                        pass
                    # TODO save to file
