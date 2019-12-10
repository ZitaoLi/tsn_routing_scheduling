//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
// 

package nesting.simulations.{{solution_name}};

import ned.DatarateChannel;
import nesting.node.ethernet.VlanEtherSwitchPreemptable2;
import nesting.node.ethernet.TSNHost;
import nesting.node.ethernet.FlowStatisticsApp;


network TestScenario
{
    types:
        channel C extends DatarateChannel
        {
            delay = {{link['delay'] or '0us'}};
            datarate = {{link['datarate'] or '1Gbps'}};
            per = {{link['per'] or '0'}};
        }
    submodules:
        flowStatisticsApp: FlowStatisticsApp;
        {% for switch in switches -%}
        switch{{switch['switch_id']}}: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[{{switch['port_num']}}];
        }
        {% endfor -%}
        {% for host in hosts -%}
        host{{host['host_id']}}: TSNHost;
        {% endfor %}
    connections:
        {%- for host in hosts -%}
            {%- for port in host['ports'] %}
        host{{host['host_id']}}.ethg$o --> C --> switch{{port['peer_node_id']}}.ethg$i[{{port['peer_port_id']}}];
        switch{{port['peer_node_id']}}.ethg$o[{{port['peer_port_id']}}] --> C --> host{{host['host_id']}}.ethg$i;
            {% endfor -%}
        {% endfor %}
        {%- for switch in switches -%}
            {%- for port in switch['ports'] %}
        switch{{switch['switch_id']}}.ethg$o[{{port['port_id']}}] --> C --> switch{{port['peer_node_id']}}.ethg$i[{{port['peer_port_id']}}];
            {% endfor -%}
        {% endfor %}
}
