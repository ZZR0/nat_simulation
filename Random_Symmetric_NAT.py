from utils import *
from random import sample

class Random_Symmetric_NAT:
    def __init__(self, id, local_ip, outer_ip, inner_internet, outer_internet, _type='random'):
        self.id = id
        self.local_addr = to_Address(local_ip)
        self.outer_addr = to_Address(outer_ip)
        self.inner_internet = inner_internet
        self.outer_internet = outer_internet
        self.available_ports = list(range(PORT_NUM))
        self.out_table = {}
        self.in_table = {}
        self.type = _type   # 'random' or 'increase'

    def transform_out(self, sender_addr, recei_addr):
        sender_addr = to_Ipv4(sender_addr)
        # print(addr)
        out_key = '{}_{}'.format(sender_addr, to_Ipv4(recei_addr))
        if out_key in self.out_table.keys():
            transform_addr = self.out_table[out_key]
        else:
            if self.type == 'random':
                port = sample(self.available_ports, 1)[0]
            elif self.type == 'increase':
                port = self.available_ports[0]
            self.available_ports.remove(port)
            transform_addr = '{}:{}'.format(self.outer_addr.ip, port)
            self.out_table[out_key] = transform_addr
            in_key = '{}_{}'.format(transform_addr, to_Ipv4(recei_addr))
            self.in_table[in_key] = sender_addr
        # print(transform_addr)
        return to_Address(transform_addr)

    # forward_out
    def send(self, sender_addr, message, recei_addr):
        transform_addr = self.transform_out(sender_addr, recei_addr)
        self.outer_internet.send(transform_addr, message, recei_addr)

    def transform_in(self, sender_addr, recei_addr):
        recei_addr = to_Ipv4(recei_addr)
        key = '{}_{}'.format(recei_addr, to_Ipv4(sender_addr))
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
        if not transform_addr.ip == '':
            self.inner_internet.send(sender_addr, message, transform_addr)