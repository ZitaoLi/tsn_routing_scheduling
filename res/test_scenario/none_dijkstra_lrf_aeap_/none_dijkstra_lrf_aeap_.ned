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

package nesting.simulations.none_dijkstra_lrf_aeap_;

import ned.DatarateChannel;
import nesting.node.ethernet.VlanEtherSwitchPreemptable2;
import nesting.node.ethernet.TSNHost;
import nesting.node.ethernet.FlowStatisticsApp;


network TestScenario
{
    types:
        channel C extends DatarateChannel
        {
            delay = 0ns;
            datarate = 1Gbps;
            per = 0;
        }
    submodules:
        flowStatisticsApp: FlowStatisticsApp;
        switch2: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[3];
        }
        switch3: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[4];
        }
        switch4: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[3];
        }
        switch5: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[4];
        }
        host1: TSNHost;
        host8: TSNHost;
        host6: TSNHost;
        host7: TSNHost;
        
    connections:
        host1.ethg$o --> C --> switch2.ethg$i[0];
        switch2.ethg$o[0] --> C --> host1.ethg$i;
            
        host8.ethg$o --> C --> switch3.ethg$i[3];
        switch3.ethg$o[3] --> C --> host8.ethg$i;
            
        host6.ethg$o --> C --> switch5.ethg$i[2];
        switch5.ethg$o[2] --> C --> host6.ethg$i;
            
        host7.ethg$o --> C --> switch5.ethg$i[3];
        switch5.ethg$o[3] --> C --> host7.ethg$i;
            
        switch2.ethg$o[1] --> C --> switch3.ethg$i[0];
            
        switch2.ethg$o[2] --> C --> switch4.ethg$i[0];
            
        switch3.ethg$o[0] --> C --> switch2.ethg$i[1];
            
        switch3.ethg$o[1] --> C --> switch4.ethg$i[1];
            
        switch3.ethg$o[2] --> C --> switch5.ethg$i[0];
            
        switch4.ethg$o[0] --> C --> switch2.ethg$i[2];
            
        switch4.ethg$o[1] --> C --> switch3.ethg$i[1];
            
        switch4.ethg$o[2] --> C --> switch5.ethg$i[1];
            
        switch5.ethg$o[0] --> C --> switch3.ethg$i[2];
            
        switch5.ethg$o[1] --> C --> switch4.ethg$i[2];
            
}