class Address:
    def __init__(self, ipv4_addr):
        if len(ipv4_addr.split(':')) == 2:
            self.ip = ipv4_addr.split(':')[0]
            self.port = ipv4_addr.split(':')[1]
        elif len(ipv4_addr.split(':')) == 1:
            self.ip = ipv4_addr
            self.port = ''
        else:
            self.ip = ''
            self.port = ''

def to_Address(ipv4_addr):
    return Address(ipv4_addr)

def to_Ipv4(addr):
    return '{}:{}'.format(addr.ip, addr.port)