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

    def get_predicted_port(self, client_id, rate=1, num=1):
        ports = []
        if client_id in self.clients.keys():
            client_addr = to_Address(self.clients[client_id])
            client_nat = self.internet.get_client(client_addr.ip)

            if client_nat.type == 3:
                for i in range(num):
                    if random() < rate:
                        ports.append(client_nat.available_ports[i])
                        rate -= 0.01
                    else:
                        ports.extend(sample(range(PORT_NUM), 1))
            elif client_nat.type == 4:
                ports = sample(client_nat.available_ports, num)
            else:
                ports = [client_addr.port] * num
            
            return ports

        ports = sample(range(PORT_NUM), num)
        return ports

def get_nat_type(nat):
    type_map = {Full_Cone_NAT:0, 
                Restricted_Cone_NAT:1, 
                Port_Restricted_Cone_NAT:2,
                Static_Symmetric_NAT:3,
                Random_Symmetric_NAT:4}

    if type(nat) in type_map.keys():
        return type_map[type(nat)]
    else:
        raise 'Unknown NAT Type.'

class Client:
    def __init__(self, id, local_addr, outer_addr, internet, nat):
        self.id = id
        self.local_addr = to_Address(local_addr)
        self.outer_addr = to_Address(outer_addr)
        self.internet = internet
        self.nat = nat
        self.nat_type = get_nat_type(nat)
        self.bind_port = 0

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

    def get_predicted_port(self, _id, rate=1, num=1):
        return self.server.get_predicted_port(_id, rate=rate, num=num)

    def register_to_server(self, port, server):
        self.server = server
        self.send(port, 'Register {}'.format(self.id), self.server.outer_addr.ip)
        self.outer_addr = to_Address(self.get_id_addr(self.id))
        self.bind_port = port

def cone2cone_connect_test(count):
    success = 0

    for i in range(count):
        clients = init_internet_env(0,0,2,0,0)
        client_a = clients[2][0]
        client_b = clients[2][1]
        if UDP_Hole_Punching(client_a, client_b):
            success += 1

    print('Success rate:%.2f%%' % (success/count*100))

def cone2sys_connect_test(count, port_count):
    success = 0
    for _ in range(count):
        clients = init_internet_env(1,1,1,1,1)
        client_a = clients[2][0]
        client_b = clients[3][0]

        if UDP_Multiple_Hole_Punching(client_a, client_b, port_count):
            success += 1

    print('Success rate:%.2f%%' % (success/count*100))

def sys2sys_connect_test(count, port_count):
    success = 0
    for _ in range(count):
        clients = init_internet_env(0,0,1,2,2)
        client_a = clients[4][0]
        client_b = clients[4][1]

        if UDP_Multiple_Hole_Punching(client_a, client_b, port_count):
            success += 1

        if _%100 == 0:
            print('%d%% Test Completed.'%(_/count*100))

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
    clients_D = init_NAT_client('clientD', 'natD', D_num, Static_Symmetric_NAT, server, outer_internet)
    clients_E = init_NAT_client('clientE', 'natE', E_num, Random_Symmetric_NAT, server, outer_internet)

    return clients_A, clients_B, clients_C, clients_D, clients_E

def proposed_cone2sys_connect_test(count, port_count, predict_rate=1):
    success = 0
    for _ in range(count):
        s = 0
        clients = init_internet_env(0,0,1,1,1)
        client_a = clients[2][0]
        client_b = clients[4][0]

        if Proposed_Method(client_a, client_b, port_count, predict_rate=predict_rate):
            success += 1         

    print('Success rate:%.2f%%' % (success/count*100))

def proposed_sys2sys_connect_test(count, port_count, predict_rate=1):
    success = 0
    for _ in range(count):
        s = 0
        clients = init_internet_env(0,0,0,2,2)
        client_a = clients[3][0]
        client_b = clients[4][1]

        if Proposed_Method(client_a, client_b, port_count, predict_rate=predict_rate):
            success += 1     

    print('Success rate:%.2f%%' % (success/count*100))


def predicted_cone2sys_connect_test(count, port_count, predict_rate=1):
    success = 0
    for _ in range(count):
        s = 0
        clients = init_internet_env(1,1,1,1,1)
        client_a = clients[2][0]
        client_b = clients[3][0]

        if Port_Prediction_Multiple_Hole_Punching(client_a, client_b, port_count, predict_rate=predict_rate):
            success += 1

    print('Success rate:%.2f%%' % (success/count*100))

def predicted_sys2sys_connect_test(count, port_count, predict_rate=1):
    success = 0
    for _ in range(count):
        s = 0
        clients = init_internet_env(0,0,0,2,2)
        client_a = clients[3][0]
        client_b = clients[4][1]

        if Port_Prediction_Multiple_Hole_Punching(client_a, client_b, port_count, predict_rate=predict_rate):
            success += 1

    print('Success rate:%.2f%%' % (success/count*100))

def UDP_Hole_Punching(client_a, client_b):
    addrB = client_a.get_id_addr(client_b.id)
    addrA = client_b.get_id_addr(client_a.id)

    try:
        client_a.send(client_a.bind_port, 'Hello', addrB)
        return True
    except:
        pass

    try:
        client_b.send(client_b.bind_port, 'Hello', addrA)
        return True
    except:
        pass

    return False

def UDP_Multiple_Hole_Punching(client_a, client_b, port_count):
    if client_a.nat_type < 3 and client_b.nat_type < 3:
        return UDP_Hole_Punching(client_a, client_b)

    addrB = client_a.get_id_addr(client_b.id)
    addrA = client_b.get_id_addr(client_a.id)
    addrB = to_Address(addrB)
    addrA = to_Address(addrA)

    if client_b.nat_type < 3:
        bports = [addrB.port] * port_count
        b_send_port = [client_b.bind_port] * port_count
    else:
        bports = sample(range(PORT_NUM), port_count)
        b_send_port = sample(range(PORT_NUM), port_count)

    if client_a.nat_type < 3:
        aports = [addrA.port] * port_count
        a_send_port = [client_a.bind_port] * port_count
    else:
        aports = sample(range(PORT_NUM), port_count)
        a_send_port = sample(range(PORT_NUM), port_count)

    for i in range(port_count):
        try:
            addr = '{}:{}'.format(addrB.ip, bports[i])
            client_a.send(a_send_port[i], 'Hello', addr)
            return True
        except:
            pass

    for i in range(port_count):
        try:
            addr = '{}:{}'.format(addrA.ip, aports[i])
            client_b.send(b_send_port[i], 'Hello', addr)
            return True
        except:
            pass

    return False

def Port_Prediction_Multiple_Hole_Punching(client_a, client_b, port_count, predict_rate=1):
    if not (client_a.nat_type == 3 or client_b.nat_type == 3):
        return UDP_Multiple_Hole_Punching(client_a, client_b, port_count)

    addrB = client_a.get_id_addr(client_b.id)
    addrA = client_b.get_id_addr(client_a.id)
    addrB = to_Address(addrB)
    addrA = to_Address(addrA)

    bports = client_a.get_predicted_port(client_b.id, rate=predict_rate, num=port_count)
    aports = client_b.get_predicted_port(client_a.id, rate=predict_rate, num=port_count)

    if client_b.nat_type < 3:
        b_send_port = [client_b.bind_port] * port_count
    else:
        b_send_port = sample(range(PORT_NUM), port_count)

    if client_a.nat_type < 3:
        a_send_port = [client_a.bind_port] * port_count
    else:
        a_send_port = sample(range(PORT_NUM), port_count)

    for i in range(port_count):
        try:
            addr = '{}:{}'.format(addrB.ip, bports[i])
            client_a.send(a_send_port[i], 'Hello', addr)
            return True
        except:
            pass

    for i in range(port_count):
        try:
            addr = '{}:{}'.format(addrA.ip, aports[i])
            client_b.send(b_send_port[i], 'Hello', addr)
            return True
        except:
            pass
    
    return False

def Proposed_Method(client_a, client_b, port_count, predict_rate=1):
    if not (client_a.nat_type == 3 or client_b.nat_type == 3):
        return UDP_Multiple_Hole_Punching(client_a, client_b, port_count)

    addrB = client_a.get_id_addr(client_b.id)
    addrA = client_b.get_id_addr(client_a.id)
    addrB = to_Address(addrB)
    addrA = to_Address(addrA)

    if client_b.nat_type < 3:
        b_send_port = [client_b.bind_port] * port_count
    else:
        b_send_port = sample(range(PORT_NUM), port_count)

    if client_a.nat_type < 3:
        a_send_port = [client_a.bind_port] * port_count
    else:
        a_send_port = sample(range(PORT_NUM), port_count)

    for i in range(port_count):
        bports = client_a.get_predicted_port(client_b.id, rate=predict_rate, num=1)
        aports = client_b.get_predicted_port(client_a.id, rate=predict_rate, num=1)
        try:
            addr = '{}:{}'.format(addrB.ip, bports[0])
            client_a.send(a_send_port[i], 'Hello', addr)
            return True
        except:
            pass

        try:
            addr = '{}:{}'.format(addrA.ip, aports[0])
            client_b.send(b_send_port[i], 'Hello', addr)
            return True
        except:
            pass
    
    return False

def network_connect_test(A_num, B_num, C_num, D_num, E_num, port_count, predict_rate=1):
    clients = []
    for client in init_internet_env(A_num, B_num, C_num, D_num, E_num):
        clients.extend(client)

    success = 0
    for client_a in clients:
        for client_b in clients:
        
            if client_a.id == client_b.id:
                success += 1
                continue
            
            # if UDP_Multiple_Hole_Punching(client_a, client_b, port_count):
            #     success += 1

            # if Port_Prediction_Multiple_Hole_Punching(client_a, client_b, port_count, predict_rate=predict_rate):
            #     success += 1

            if Proposed_Method(client_a, client_b, port_count, predict_rate=predict_rate):
                success += 1
    
    print('Network Connective: %.2f%%' % (success/100))
    

if __name__ == "__main__":
    
    # cone2cone_connect_test(100)
    # cone2sys_connect_test(10000, 200)
    # sys2sys_connect_test(10000, 200)
    # predicted_cone2sys_connect_test(10000, 200, predict_rate=0.2)
    predicted_sys2sys_connect_test(10000, 200, predict_rate=0.2)
    # proposed_cone2sys_connect_test(10000, 200,  predict_rate=0.2)
    # proposed_sys2sys_connect_test(10000, 200, predict_rate=0.2)
    # network_connect_test(14, 4, 62, 10, 10, 200, predict_rate=0.2)
