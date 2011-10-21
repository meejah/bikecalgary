
class ZeroDict(dict):
    "hash table which assigns 0 to any key you request that doesn't yet exist"

    def __getitem__(self, k):
        if not self.has_key(k):
            dict.__setitem__(self, k, 0)
        return dict.__getitem__(self, k)
