from cachesim.cache import CacheResult


class Stats:
    def __init__(self):
        self.references = 0
        self.hits = 0
        self.bytes_read = 0
        self.bytes_written = 0
        self.lines_replaced = 0

    def add(self, result: CacheResult):
        self.references += 1
        if result.hit:
            self.hits += 1
        for (w_nr, addr, nbytes) in result.ll_ops:
            if w_nr:
                self.bytes_written += nbytes
            else:
                self.bytes_read += nbytes
        if result.replaced_tag != None:
            self.lines_replaced += 1
