from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream# as MockTransport
from playground.network.testing import MockTransportToProtocol
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BOOL, BUFFER
import io, asyncio, playground
from playground.network.protocols.packets.vsocket_packets import VNICSocketOpenPacket, VNICSocketOpenResponsePacket, \
    PacketType
from playground.network.protocols.packets.switching_packets import WirePacket
from playground.network.common import StackingProtocol, StackingTransport, StackingProtocolFactory
import playground
from lab_1e_passthrough import *


class ConnectionRequest(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.student_x.ConnectionRequest"
    DEFINITION_VERSION = "1.0"
    FIELDS = []
# This is the class used in the first step of my protocol: client send ConnectionRequest() to server

class VerifyingInfo(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.student_x.VerifyingInfo"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("ID", UINT32),
        ("IfPermit", BOOL)
    ]
# This is the class used in the second step of my protocol:server send VerifyingInfo(ID, IfPermit) to client

class ConnectionInfo(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.student_x.ConnectionInfo"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("ID", UINT32),
        ("Address", STRING)
    ]
# This is the class used in the third step of my protocol:client send ConnectionInfo(ID, address) to server

class MyClientProtocol(asyncio.Protocol):
    state = 0
    def __init__(self):
        self._deserializer = PacketType.Deserializer()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        #pktCR = ConnectionRequest()
        #transport.write(pktCR.__serialize__())
        print("Client made success")
        #self._deserializer = PacketType.Deserializer()

    def data_received(self, data):
        self._deserializer.update(data)
        print("Client receive data")
        self.state = 1
        for pkt in self._deserializer.nextPackets():
            #print(pkt)
            if pkt == None:
                print("Error.The packet is empty.")
                self.transport.close
            else:
                if isinstance(pkt, VerifyingInfo):
                    if self. state == 1:
                        print("The state of the client now is %d" % self.state)
                        print("The packet is VerifyingInfo")
                    #if pkt.DEFINITION_IDENTIFIER == "lab1b.student_x.VerifyingInfo":
                        if pkt.IfPermit == True:
                            pktCI = ConnectionInfo()
                            pktCI.ID = pkt.ID
                            pktCI.Address = "1.1.1.1"
                            self.state = 2
                            print("The client is sending ConnectionInfo to the server")
                            self.transport.write(pktCI.__serialize__())
                            print("The client finish sending ConnectionInfo to the server")
                        else:
                            print("Don't get permission!Connection fail.")
                            self.transport.close()
                    else:
                        print("The state of the server now is ERROR")
                        self.transport.close
                else:
                    print("Error.The type of the received packet is wrong.")
                    self.transport.close()


    def connection_lost(self, exc):
        self.transport = None
        print("The connection is stopped(Client).")

    def send(self, packet):
        self.transport.write(packet.__serialize__())

def lab_1e_test():
    loop = asyncio.get_event_loop()
    loop.set_debug(enabled=True)
    f = StackingProtocolFactory(lambda: higherProtocol1(), lambda: higherProtocol2())

    ptConnector = playground.Connector(protocolStack=f)
    playground.setConnector("passthrough", ptConnector)
    #message = 'Hello World!'
    myconnect = playground.getConnector('passthrough').create_playground_connection (lambda:MyClientProtocol(), '20174.1.1.1', 46427)
    transport, client = loop.run_until_complete(myconnect)
    pktCR = ConnectionRequest()
    client.send(pktCR)
    loop.run_forever()
    loop.close()

if __name__ == "__main__":
    lab_1e_test()
