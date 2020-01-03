from enum import Enum
from typing import NewType

MacAddress = NewType('MacAddress', str)
NodeId = NewType('NodeId', int)
EdgeId = NewType('EdgeId', int)
FlowId = NewType('FlowId', int)
PortNo = NewType('PortNo', int)
NodeName = NewType('NodeName', str)
SimTime = NewType('SimTime', float)
QueueId = NewType('QueueId', int)

TOPO_STRATEGY = Enum('TOPO_STRATEGY', (
    'ER_STRATEGY', 'BA_STRATEGY',
    'RRG_STRATEGY', 'WS_STRATEGY'))

ROUTING_STRATEGY = Enum('ROUTING_STRATEGY', (
    'BACKTRACKING_REDUNDANT_ROUTING_STRATEGY',
    'DIJKSTRA_SINGLE_ROUTING_STRATEGY'))
RELIABILITY_STRATEGY = Enum('RELIABILITY_STRATEGY', (
    'MULTI_ROUTES_RELIABILITY_STRATEGY',
    'ENUMERATION_METHOD_RELIABILITY_STRATEGY',
    'UNI_ROUTES_RELIABILITY_STRATEGY'))
SCHEDULING_STRATEGY = Enum('SCHEDULING_STRATEGY', (
    'LRF_REDUNDANT_SCHEDULING_STRATEGY'))
ALLOCATING_STRATEGY = Enum('ALLOCATING_STRATEGY', (
    'AEAP_ALLOCATING_STRATEGY'))

TIME_GRANULARITY = Enum('TIME_GRANULARITY', ('NS, US, MS, S'))

FLOW_TYPE = Enum('FLOW_TYPE', ('TSN_FLOW', 'NON_TSN_FLOW'))
