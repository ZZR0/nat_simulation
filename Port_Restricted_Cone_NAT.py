from utils import *
from random import sample

class Port_Restricted_Cone_NAT:
    def __init__(self, id, local_ip, outer_ip, inner_internet, outer_internet):
        self.id = id
        self.local_addr = to_Address(local_ip)
        self.outer_addr = to_Address(outer_ip)
        self.inner_internet = inner_internet
        self.outer_internet = outer_internet
        self.available_ports = set(range(PORT_NUM))
        self.out_table = {}
        self.in_table = {}

    def transform_out(self, sender_addr, recei_addr):
        sender_addr = to_Ipv4(sender_addr)
        # print(addr)
        if sender_addr in self.out_table.keys():
            transform_addr = self.out_table[sender_addr]
            key = '{}_{}:{}'.format(transform_addr, recei_addr.ip, recei_addr.port)
            self.in_table[key] = sender_addr
        else:
            port = sample(self.available_ports, 1)[0]
            self.available_ports.remove(port)
            transform_addr = '{}:{}'.format(self.outer_addr.ip, port)
            self.out_table[sender_addr] = transform_addr
            key = '{}_{}:{}'.format(transform_addr, recei_addr.ip, recei_addr.port)
            self.in_table[key] = sender_addr
        # print(transform_addr)
        return to_Address(transform_addr)

    # forward_out
    def send(self, sender_addr, message, recei_addr):
        transform_addr = self.transform_out(sender_addr, recei_addr)
        self.outer_internet.send(transform_addr, message, recei_addr)

    def transform_in(self, sender_addr, recei_addr):
        recei_addr = to_Ipv4(recei_addr)
        key = '{}_{}:{}'.format(recei_addr, sender_addr.ip, sender_addr.port)
        # print(self.id, key, self.in_table.keys())
        if key in self.in_table.keys():
            transform_addr = self.in_table[key]
        else:
            raise Exception('Message rejected by NAT.')
            transform_addr = ''
        return to_Address(transform_addr)

    # forward_in
    def receive(self, sender_addr, message, recei_addr):
        transform_addr = self.transform_in(sender_addr, recei_addr)
        self.inner_internet.send(sender_addr, message, transform_addr)