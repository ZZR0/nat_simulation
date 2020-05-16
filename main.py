from utils import *
from Full_Cone_NAT import *
from Restricted_Cone_NAT import *
from Port_Restricted_Cone_NAT import *
from Random_Symmetric_NAT import *
from Static_Symmetric_NAT import *
from random import random

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
        # print('Register Action:', self.clients)

    def get_addr(self, client_id):
        return self.clients[client_id]

    def send(self):
        pass

    def receive(self, sender_addr, message, recei_addr):
        if 'Register' in message:
            self.register(message.split()[1], sender_addr)

    def get_predicted_port(self, client_id, rate=1):
        port = 0
        if client_id in self.clients.keys() and random() < rate:
            client_addr = to_Address(self.clients[client_id])
            client_nat = self.internet.get_client(client_addr.ip)
            port = client_nat.available_ports[0]
        return port


class Client:
    def __init__(self, id, local_addr, outer_addr, internet, nat):
        self.id = id
        self.local_addr = to_Address(local_addr)
        self.outer_addr = to_Address(outer_addr)
        self.internet = internet
        self.nat = nat

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

    def get_predicted_port(self, _id, rate=1):
        return self.server.get_predicted_port(_id, rate=rate)

    def register_to_server(self, port, server):
        self.server = server
        self.send(port, 'Register {}'.format(self.id), self.server.outer_addr.ip)
        self.outer_addr = to_Address(self.get_id_addr(self.id))

def cone2cone_connect_test(count):
    success = 0

    for i in range(count):
        clients = init_internet_env(0,0,2,0,0)
        client_a = clients[2][0]
        client_b = clients[2][1]
        addrB = client_a.get_id_addr(client_b.id)
        addrA = client_b.get_id_addr(client_a.id)

        try:
            client_a.send(0, 'Hello', addrB)
            success += 1
            continue
        except:
            pass
        try:
            client_b.send(0, 'Hello', addrA)
            success += 1
            continue
        except:
            pass

    print('Success rate:%.2f%%' % (success/count*100))

def cone2sys_connect_test(count, port_count):
    success = 0
    for _ in range(count):
        s = 0
        clients = init_internet_env(0,0,1,1,0)
        client_a = clients[2][0]
        client_b = clients[3][0]

        addrB = client_a.get_id_addr(client_b.id)
        addrA = client_b.get_id_addr(client_a.id)
        addrB = to_Address(addrB)
        ports = sample(range(PORT_NUM), port_count)

        for i in range(port_count):
            try:
                addr = '{}:{}'.format(addrB.ip, ports[i])
                client_a.send(0, 'Hello', addr)
                s = 1
                break
            except:
                pass
        
        if s == 1:
            success += s
            continue
        
        for i in range(port_count):
            try:
                client_b.send(ports[i], 'Hello', addrA)
                success += 1
                break
            except:
                pass

    print('Success rate:%.2f%%' % (success/count*100))

def sys2sys_connect_test(count, port_count):
    success = 0
    for _ in range(count):
        s = 0
        clients = init_internet_env(0,0,1,1,0)
        client_a = clients[2][0]
        client_b = clients[3][0]

        addrB = client_a.get_id_addr(client_b.id)
        addrA = client_b.get_id_addr(client_a.id)
        addrB = to_Address(addrB)
        ports = sample(range(PORT_NUM), port_count)

        for i in range(port_count):
            try:
                addr = '{}:{}'.format(addrB.ip, ports[i])
                client_a.send(0, 'Hello', addr)
                s = 1
                break
            except:
                pass
        
        if s == 1:
            success += s
            continue

        ports = sample(range(PORT_NUM), port_count)
        for i in range(port_count):
            try:
                addr = '{}:{}'.format(addrB.ip, ports[i])
                client_b.send(0, 'Hello', addr)
                success += 1
                break
            except:
                pass

    print('Success rate:%.2f%%' % (success/count*100))

def init_NAT_client(client_id, nat_id, num, NAT, server, outer_internet):
    clients = []
    for i in range(1, num+1):
        local_internet = Internet()
        local_ip = '{}.{}.0.0'.format(nat_id, i)
        public_ip = '0.0.{}.{}'.format(nat_id, i)
        nat = NAT('{}.{}'.format(nat_id, i), local_ip, public_ip, local_internet, outer_internet)
        client = Client('{}.{}'.format(client_id, i), 
                        '{}.{}.0.1'.format(nat_id, i), 
                        '{}.{}.0.1'.format(nat_id, i), 
                        local_internet, nat)
        
        local_internet.register(client)
        local_internet.register_route(nat)

        outer_internet.register(nat)

        client.register_to_server(0, server)
        
        clients.append(client)

    return clients


def init_internet_env(A_num, B_num, C_num, D_num, E_num):
    # A:1.0.0.0   out:0.0.0.0   B:2.0.0.0
    outer_internet = Internet()
    server = Server('server', '0.0.0.0', '0.0.0.0', outer_internet)
    outer_internet.register(server)

    clients_A = init_NAT_client('clientA', 'natA', A_num, Full_Cone_NAT, server, outer_internet)
    clients_B = init_NAT_client('clientB', 'natB', B_num, Restricted_Cone_NAT, server, outer_internet)
    clients_C = init_NAT_client('clientC', 'natC', C_num, Port_Restricted_Cone_NAT, server, outer_internet)
    clients_D = init_NAT_client('clientD', 'natD', D_num, Random_Symmetric_NAT, server, outer_internet)
    clients_E = init_NAT_client('clientE', 'natE', E_num, Static_Symmetric_NAT, server, outer_internet)

    return clients_A, clients_B, clients_C, clients_D, clients_E

def predicted_cone2sys_connect_test(count, port_count, predict_rate=1):
    success = 0
    for _ in range(count):
        s = 0
        clients = init_internet_env(0,0,1,0,1)
        client_a = clients[2][0]
        client_b = clients[4][0]

        addrB = client_a.get_id_addr(client_b.id)
        addrA = client_b.get_id_addr(client_a.id)
        addrB = to_Address(addrB)
        ports = sample(range(PORT_NUM), port_count)

        for i in range(port_count):
            try:
                port = client_a.get_predicted_port(client_b.id, rate=predict_rate)
                addr = '{}:{}'.format(addrB.ip, port)
                client_a.send(0, 'Hello', addr)
                success += 1
                break
            except:
                pass

            try:
                client_b.send(ports[i], 'Hello', addrA)
                success += 1
                break
            except:
                pass       

    print('Success rate:%.2f%%' % (success/count*100))

def predicted_sys2sys_connect_test(count, port_count, predict_rate=1):
    success = 0
    for _ in range(count):
        s = 0
        clients = init_internet_env(0,0,0,0,2)
        client_a = clients[4][0]
        client_b = clients[4][1]

        addrB = client_a.get_id_addr(client_b.id)
        addrA = client_b.get_id_addr(client_a.id)
        addrA = to_Address(addrA)
        addrB = to_Address(addrB)

        for i in range(port_count):
            bport = client_a.get_predicted_port(client_b.id, rate=predict_rate)
            aport = client_b.get_predicted_port(client_a.id, rate=predict_rate)
            try:
                addr = '{}:{}'.format(addrB.ip, bport)
                client_a.send(0, 'Hello', addr)
                success += 1
                break
            except:
                pass

            try:
                addr = '{}:{}'.format(addrA.ip, aport)
                client_b.send(0, 'Hello', addr)
                success += 1
                break
            except:
                pass          

    print('Success rate:%.2f%%' % (success/count*100))

if __name__ == "__main__":
    
    # cone2cone_connect_test(100)
    # cone2sys_connect_test(100, 200)
    # sys2sys_connect_test(100, 53706)
    # predicted_cone2sys_connect_test(100, 200)
    predicted_sys2sys_connect_test(100, 200)
