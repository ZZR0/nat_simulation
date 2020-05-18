import copy

class t(object):
    def __init__(self):
        self.a = [1,2,3,4,5]

s = t()
print(s.a)

b = copy.deepcopy(s.a)
print(b)

b.remove(3)
print(b)
print(s.a)