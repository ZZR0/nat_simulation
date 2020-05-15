from utils import *
from Full_Cone_NAT import *
from Restricted_Cone_NAT import *
from Port_Restricted_Cone_NAT import *
from Symmetric_NAT import *

class Internet:
    def __init__(self):
        self.clients = {}
        self.route = ''

    def register_route(self, route):
        self.route = route

    def send(self, sender_addr, message, addr):
        
        if addr.ip in self.clients.keys():
            client = self.get_client(addr.ip)
            client.receive(sender_addr, message, addr)
        elif self.route:
            self.route.send(sender_addr, message, addr)
        else:
            print('Abandom message:', message)

    def get_client(self, ip):
        return self.clients[ip]

    def register(self, client):
        # print(client.outer_addr)
        self.clients[client.outer_addr.ip] = client


class Server:
    def __init__(self, id, local_addr, outer_addr, internet):
        self.id = id
        self.local_addr = to_Address(local_addr)
        self.outer_addr = to_Address(outer_addr)
        self.internet = internet
        self.clients = {}

    def register(self, client_id, client_addr):
        self.clients[client_id] = to_Ipv4(client_addr)
        print('Register Action:', self.clients)

    def get_addr(self, client_id):
        return self.clients[client_id]

    def send(self):
        pass

    def receive(self, sender_addr, message, recei_addr):
        if 'Register' in message:
            self.register(message.split()[1], sender_addr)


class Client:
    def __init__(self, id, local_addr, outer_addr, internet):
        self.id = id
        self.local_addr = to_Address(local_addr)
        self.outer_addr = to_Address(outer_addr)
        self.internet = internet

    def register(self, server):
        server.register(self)

    def connect(self, server, peer_id):
        peer_addr = server.get_addr(peer_id)

    def send(self, port, message, addr):
        assert type(addr) == str
        addr = to_Address(addr)
        sender_addr = to_Address('{}:{}'.format(self.local_addr.ip, port))
        self.internet.send(sender_addr, message, addr)

    def receive(self, sender_addr, message, recei_addr):
        print('{} Port: {}     Receive from: {}    Message: {}'.format(self.id, recei_addr.port, to_Ipv4(sender_addr), message))

    def get_id_addr(self, id):
        return self.server.get_addr(id)

    def register_to_server(self, port, server):
        self.server = server
        self.send(port, 'Register {}'.format(self.id), self.server.outer_addr.ip)
        self.outer_addr = to_Address(self.get_id_addr(self.id))

def connect(client_a, client_b):
    addrB = client_a.get_id_addr(client_b.id)
    addrA = client_b.get_id_addr(client_a.id)

    client_a.send(0, 'Hello', addrB)
    client_b.send(0, 'Hello', addrA)



if __name__ == "__main__":
    # A:1.0.0.0   out:0.0.0.0   B:2.0.0.0
    local_internet_A = Internet()
    local_internet_B = Internet()
    outer_internet = Internet()

    natA = Port_Restricted_Cone_NAT('natA', '1.0.0.0', '0.0.0.1', local_internet_A, outer_internet)
    natB = Port_Restricted_Cone_NAT('natB', '2.0.0.0', '0.0.0.2', local_internet_B, outer_internet)

    clientA = Client('clientA', '1.0.0.0', '1.0.0.0', local_internet_A)
    clientB = Client('clientB', '2.0.0.0', '2.0.0.0', local_internet_B)
    clientC = Client('clientC', '2.0.0.1', '2.0.0.1', local_internet_B)


    server = Server('server', '0.0.0.0', '0.0.0.0', outer_internet)

    local_internet_A.register(clientA)
    local_internet_A.register_route(natA)

    local_internet_B.register(clientB)
    local_internet_B.register(clientC)
    local_internet_B.register_route(natB)

    outer_internet.register(natA)
    outer_internet.register(natB)
    outer_internet.register(server)

    clientA.register_to_server(0, server)
    clientB.register_to_server(0, server)
    clientC.register_to_server(0, server)


    connect(clientA, clientB)
    # addrB = clientA.get_id_addr('clientB')
    # addrC = clientA.get_id_addr('clientC')
    # addrA = clientB.get_id_addr('clientA')

    # clientA.send(0, 'Hello', '0.0.0.2:2')
    # clientB.send(0, 'Hi', '0.0.0.1:1')
    # clientC.send(0, 'Hi', addrA)
    # clientA.send(0, 'Hello', addrB)