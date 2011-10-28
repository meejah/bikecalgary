
class ZeroDict(dict):
    "hash table which assigns 0 to any key you request that doesn't yet exist"

    def __init__(self, zerocreator=lambda: 0):
        dict.__init__(self)
        self.zerocreator = zerocreator

    def __getitem__(self, k):
        if not self.has_key(k):
            dict.__setitem__(self, k, self.zerocreator())
        return dict.__getitem__(self, k)
