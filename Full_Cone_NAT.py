from utils import *
from random import sample

class Full_Cone_NAT:
    def __init__(self, id, local_ip, outer_ip, inner_internet, outer_internet):
        self.id = id
        self.local_addr = to_Address(local_ip)
        self.outer_addr = to_Address(outer_ip)
        self.inner_internet = inner_internet
        self.outer_internet = outer_internet
        self.available_ports = set(range(PORT_NUM))
        self.out_table = {}
        self.in_table = {}
        self.type = 0

    def transform_out(self, addr):
        addr = to_Ipv4(addr)
        # print(addr)
        if addr in self.out_table.keys():
            transform_addr = self.out_table[addr]
        else:
            port = sample(self.available_ports, 1)[0]
            self.available_ports.remove(port)
            transform_addr = '{}:{}'.format(self.outer_addr.ip, port)
            self.out_table[addr] = transform_addr
            self.in_table[transform_addr] = addr
        # print(transform_addr)
        return to_Address(transform_addr)

    # forward_out
    def send(self, sender_addr, message, recei_addr):
        transform_addr = self.transform_out(sender_addr)
        self.outer_internet.send(transform_addr, message, recei_addr)

    def transform_in(self, addr):
        addr = to_Ipv4(addr)
        if addr in self.in_table.keys():
            transform_addr = self.in_table[addr]
        else:
            raise Exception('Message rejected by NAT.')
            transform_addr = ''
        return to_Address(transform_addr)

    # forward_in
    def receive(self, sender_addr, message, recei_addr):
        transform_addr = self.transform_in(recei_addr)
        self.inner_internet.send(sender_addr, message, transform_addr)