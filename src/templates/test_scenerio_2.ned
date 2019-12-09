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

package nesting.simulations.test_scenario_2;

import ned.DatarateChannel;
import nesting.node.ethernet.VlanEtherSwitchPreemptable2;
import nesting.node.ethernet.TSNHost;


network TestScenario2
{
    types:
        channel C extends DatarateChannel
        {
            delay = 0.1us;
            datarate = 1Gbps;
            per = 0.5;
//            per = 1e-1;
//            per = 0.99;
        }
    submodules:
        switch1: VlanEtherSwitchPreemptable2 {
            parameters:
                @display("p=179,169");
            gates:
                ethg[3];
        }
        switch2: VlanEtherSwitchPreemptable2 {
            parameters:
                @display("p=282,105");
            gates:
                ethg[4];
        }
        switch3: VlanEtherSwitchPreemptable2 {
            parameters:
                @display("p=387,169");
            gates:
                ethg[4];
        }
        switch4: VlanEtherSwitchPreemptable2 {
            parameters:
                @display("p=299,243");
            gates:
                ethg[3];
        }
        host1: TSNHost {
            @display("p=53,170");
        }
        host2: TSNHost {
            @display("p=229,50");
        }
        host3: TSNHost {
            @display("p=519,125");
        }
        host4: TSNHost {
            @display("p=519,209");
        }
    connections:
        host1.ethg <--> C <--> switch1.ethg[0];
        host2.ethg <--> C <--> switch2.ethg[1];
        host3.ethg <--> C <--> switch3.ethg[1];
        host4.ethg <--> C <--> switch3.ethg[2];

        switch1.ethg[1] <--> C <--> switch2.ethg[0];
        switch1.ethg[2] <--> C <--> switch4.ethg[0];

        switch2.ethg[2] <--> C <--> switch3.ethg[0];
        switch2.ethg[3] <--> C <--> switch4.ethg[1];

        switch3.ethg[3] <--> C <--> switch4.ethg[2];
}
