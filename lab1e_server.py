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



class MyServerProtocol(asyncio.Protocol):
    ConnectionID = 0
    state = 0
    def __init__(self):
        self.transport = None
        self._deserializer = PacketType.Deserializer()

    def connection_made(self, transport):
        self.transport = transport
        self._deserializer = PacketType.Deserializer()
        print("Server made success")

    def data_received(self, data):
        self._deserializer.update(data)
        print("Server receive data")
        for pkt in self._deserializer.nextPackets():
            #print(pkt)
            if pkt == None:
                print("Error.The packet is empty.")
                self.transport.close()
            else:
                if isinstance(pkt, ConnectionRequest):
                    self.state = 0
                    print("The state of the server now is %d" % self.state)
                    print("The packet is ConnectionRequest")
                    #if pkt.DEFINITION_IDENTIFIER == "lab1b.student_x.ConnectionRequest":
                    pktVI = VerifyingInfo()
                    self.ConnectionID = self.ConnectionID + 1
                    pktVI.ID = self.ConnectionID
                    pktVI.IfPermit = True
                    self.state = 1
                    print("The server is sending the VerifyingInfo to the client")
                    self.transport.write(pktVI.__serialize__())
                    print("The server finish sending the VerifyingInfo to the client")

                elif isinstance(pkt,ConnectionInfo):
                    self.state = 2
                    print("The state of the server now is %d" % self.state)
                    print("The packet is ConnectionInfo")
                    #pkt.DEFINITION_IDENTIFIER == "lab1b.student_x.ConnectionInfo":
                    print("Connection success!")
                    print("The ID of the Client is %d" % pkt.ID)
                    print("The Address of the Cilent is %s" % pkt.Address)
                    self.state = 3
                    print("The state of the server now is %d" % self.state)
                    #self.transport.close()
                else:
                    print("Error.The type of the received packet is wrong.")
                    self.transport.close()


    def connection_lost(self, exc):
        self.transport = None
        print("The connection is stopped(Server)")



def lab_1e_test():
    loop = asyncio.get_event_loop()
    loop.set_debug(enabled=True)
    f = StackingProtocolFactory(lambda: higherProtocol1(), lambda: higherProtocol2())

    ptConnector = playground.Connector(protocolStack=f)
    playground.setConnector("passthrough", ptConnector)
    coro = playground.getConnector('passthrough').create_playground_server(lambda:MyServerProtocol(), 46427)
    server = loop.run_until_complete(coro)
    print('Serving on {}'.format(server.sockets[0].gethostname()))
    loop.run_forever()
    server.close()
    loop.close()

if __name__ == "__main__":
    lab_1e_test()
