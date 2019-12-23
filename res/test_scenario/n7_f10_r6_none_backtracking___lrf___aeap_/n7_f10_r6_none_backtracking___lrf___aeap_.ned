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

package nesting.simulations.n7_f10_r6_none_backtracking___lrf___aeap_;

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
        switch5: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[3];
        }
        switch6: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[3];
        }
        switch9: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[4];
        }
        switch7: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[3];
        }
        switch8: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[4];
        }
        switch11: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[3];
        }
        switch10: VlanEtherSwitchPreemptable2 {
            gates:
                ethg[2];
        }
        host1: TSNHost;
        host2: TSNHost;
        host3: TSNHost;
        host4: TSNHost;
        
    connections:
        host1.ethg$o --> C --> switch5.ethg$i[0];
        switch5.ethg$o[0] --> C --> host1.ethg$i;
            
        host2.ethg$o --> C --> switch6.ethg$i[1];
        switch6.ethg$o[1] --> C --> host2.ethg$i;
            
        host3.ethg$o --> C --> switch8.ethg$i[0];
        switch8.ethg$o[0] --> C --> host3.ethg$i;
            
        host4.ethg$o --> C --> switch11.ethg$i[1];
        switch11.ethg$o[1] --> C --> host4.ethg$i;
            
        switch5.ethg$o[1] --> C --> switch6.ethg$i[0];
            
        switch5.ethg$o[2] --> C --> switch9.ethg$i[0];
            
        switch6.ethg$o[0] --> C --> switch5.ethg$i[1];
            
        switch6.ethg$o[2] --> C --> switch7.ethg$i[0];
            
        switch9.ethg$o[0] --> C --> switch5.ethg$i[2];
            
        switch9.ethg$o[1] --> C --> switch8.ethg$i[2];
            
        switch9.ethg$o[2] --> C --> switch7.ethg$i[2];
            
        switch9.ethg$o[3] --> C --> switch10.ethg$i[1];
            
        switch7.ethg$o[0] --> C --> switch6.ethg$i[2];
            
        switch7.ethg$o[1] --> C --> switch8.ethg$i[1];
            
        switch7.ethg$o[2] --> C --> switch9.ethg$i[2];
            
        switch8.ethg$o[1] --> C --> switch7.ethg$i[1];
            
        switch8.ethg$o[2] --> C --> switch9.ethg$i[1];
            
        switch8.ethg$o[3] --> C --> switch11.ethg$i[0];
            
        switch11.ethg$o[0] --> C --> switch8.ethg$i[3];
            
        switch11.ethg$o[2] --> C --> switch10.ethg$i[0];
            
        switch10.ethg$o[0] --> C --> switch11.ethg$i[2];
            
        switch10.ethg$o[1] --> C --> switch9.ethg$i[3];
            
}