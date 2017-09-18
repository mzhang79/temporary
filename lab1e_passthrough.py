from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream  # as MockTransport
from playground.network.testing import MockTransportToProtocol
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BOOL, BUFFER
import io, asyncio, playground
from playground.network.protocols.packets.vsocket_packets import VNICSocketOpenPacket, VNICSocketOpenResponsePacket, \
    PacketType
from playground.network.protocols.packets.switching_packets import WirePacket
from playground.network.common import StackingProtocol, StackingTransport, StackingProtocolFactory
import playground


class higherProtocol1(StackingProtocol):
    def connection_made(self, transport):
        self.transport = transport
        self.higherProtocol().connection_made(transport)

    def data_received(self, data):
        self.higherProtocol().data_received(data)

    def connection_lost(self, exc):
        self.higherProtocol().connection_lost()



class higherProtocol2(StackingProtocol):
    def connection_made(self, transport):
        self.transport = transport
        self.higherProtocol().connection_made(transport)

    def data_received(self, data):
        self.higherProtocol().data_received(data)

    def connection_lost(self, exc):
        self.higherProtocol().connection_lost()





