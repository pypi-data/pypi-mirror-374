from .replacement import ReplacementPolicy, LRU, FIFO

from math import ceil, log2

import sys


class Line:
    def __init__(self, tag: int = 0, valid: bool = False):
        self.tag = tag
        self.valid = valid
        self.modified = False

    def invalidate(self) -> None:
        self.valid = False


class Set:
    def __init__(self, num_lines: int, replacement_policy: ReplacementPolicy):
        self.lines = [Line(valid=False) for _ in range(num_lines)]
        self._rep = replacement_policy  # replacement algorithm

    def index(self, tag: int) -> int:
        """Get index of cache line with tag *tag*"""
        line_idx = None
        for (i, line) in enumerate(self.lines):
            if (line.valid and line.tag == tag):
                line_idx = i
                break

        if line_idx is not None:
            return line_idx
        else:
            raise ValueError(f"Tag '{hex(tag)}' not in Set")

    def __contains__(self, tag: int) -> bool:
        try:
            return self.index(tag) is not None
        except ValueError:
            return False

    def __getitem__(self, tag: int) -> Line:
        """Gets cache line by tag"""
        try:
            idx = self.index(tag)
            return self.lines[idx]
        except ValueError:
            raise KeyError(f"Tag '{hex(tag)}' not in Set")

    def invalidate(self) -> None:
        """Invalidate all lines in set and resets replacement policy"""
        # invalidate lines
        for line in self.lines:
            line.invalidate()

        # reset policy
        self._rep.reset()

    def flush(self) -> list[int]:
        """Returns a list with the tags of modified lines that would be written to LL (for WB)"""
        written = []

        # write lines to LL and mark them as modified
        for line in self.lines:
            # XXX for write-through caches, line.modified should be never True
            if line.valid and line.modified:
                written.append(line.tag)
                line.modified = False

        return written

    def insert(self, tag: int) -> Line:
        """Insert a line with tag *tag* and return the replaced line"""
        idx = self._rep.getLineIndexToReplace()
        replaced = self.lines[idx]

        self.lines[idx] = Line(tag, valid=True)

        return replaced

    def reference(self, tag: int) -> None:
        """Flags usage of tag *tag* for replacement algorithm"""
        idx = self.index(tag)
        self._rep.onLineIndexReferenced(idx)


class CacheResult:
    def __init__(self, hit: bool, ll_ops: list[tuple[bool, int, int]], replaced_tag: int):
        """Result of a reference to a cache:
            * hit: True if cache hit
            * ll_op: list of operations to perform on lower level (w_not_r, address, nbytes)
            * replaced_tag: tag of replaced line, or None if no replacement occurred
        """
        self.hit = hit
        self.ll_ops = ll_ops
        self.replaced_tag = replaced_tag


class Cache:
    def __init__(
            self,
            lines: int = 32,
            line_size: int = 16,
            associativity: int = 2,
            write_back: bool = True,
            write_allocate: bool = True,
            replacement: ReplacementPolicy = LRU):
        assert lines >= associativity, "Associativity cannot be great than number of lines"
        self._lines = 2 ** int(ceil(log2(lines)))
        self._bpl = 2 ** int(ceil(log2(line_size)))
        self._assoc = 2 ** int(ceil(log2(associativity)))
        self._wb = write_back
        self._wa = write_allocate
        self._replp = replacement

        if (self._lines != lines or self._bpl != line_size or self._assoc != associativity):
            print("[Warning] Cache: values adjusted to greater closest power of 2", file=sys.stderr)

        self._nsets = self._lines // self._assoc
        self._sets = [Set(self._assoc, replacement(self._assoc)) for _ in range(self._nsets)]

    def __len__(self) -> int:
        """Size of the cache (in B)"""
        return self._lines * self._bpl

    def _buildAddress(self, tag: int, idx: int, offset: int) -> int:
        address = (tag * self._nsets + idx) * self._bpl + offset
        return address

    def splitAddress(self, address: int) -> tuple[int, int, int]:
        """Split address into tag, set index and offset"""
        offset = address % self._bpl
        a = address // self._bpl
        idx = a % self._nsets
        tag = a // self._nsets

        return (tag, idx, offset)

    def invalidate(self) -> list[tuple[int, int]]:
        """Invalidates the cache"""
        for s in self._sets:
            s.invalidate()

    def flush(self) -> list[tuple[int, int]]:
        """Flushes the cache and returns the (set, tag) of lines that would be written to LL (modified lines)"""
        l = []
        for (si, s) in enumerate(self._sets):
            for tag in s.flush():
                l.append((si, tag))

        return l

    def reference(self, address: int, nbytes: int, wr: bool) -> CacheResult:
        """Performs a reference (load if *!wr*, store if *wr*) to the address *address*, updating the state
           depending on configuration.
        """
        assert nbytes <= self._bpl, "Tried to read/write more bytes than there are in a line"

        (tag, idx, offset) = self.splitAddress(address)

        seti = self._sets[idx]
        miss = tag not in seti
        ll_op = []
        replaced_tag = None

        # if miss and (self._wa or (not wr and not self._wa)):
        # simplifying conditions: m&(wa|(~wa&~w)) = m&(wa|~w)
        if miss and (self._wa or not wr):
            # replace cache line
            # takes into account WB
            #
            # write-allocate: for all misses
            # no-write-allocate: for read misses

            # swap old and new tag in set
            old_line = seti.insert(tag)
            if old_line.valid:
                replaced_tag = old_line.tag

                # write line to lower level if modified (WB only)
                if self._wb and old_line.modified:
                    # write line to lower level
                    line_address = self._buildAddress(old_line.tag, idx, 0)
                    ll_op.append((True, line_address, self._bpl))

            # read line from lower level
            line_address = self._buildAddress(tag, idx, 0)
            ll_op.append((False, line_address, self._bpl))
            if self._wb:
                # mark not modified
                seti[tag].modified = False

        # if wr and ((not self._wb) or (miss and self._wb and not self._wa)):
        # simplifying conditions: w&(~wb|(m&wb&~wa))) = w&(~wb|m|~wa)
        if wr and (not self._wb or miss and not self._wa):
            # write data to lower level
            #
            # write-through: for all writes
            # write-back and no-write-allocate: for write misses
            ll_op.append((True, address, nbytes))

            # NOTE: the code doesn't need to handle it, but the current level would also be written if:
            #   write-allocate: always (line was already in cache OR has just been brought from lower level)
            #   no-write-allocate: only if line was already in cache

        if self._wa or not (wr and miss):
            # "use" cache line -> updates replacement policy
            # and mark modified (if WB)
            #
            # write-allocate: always
            # no-write-allocate: after any hit or after a read miss

            # mark modified if write (WB only)
            if wr and self._wb:
                seti[tag].modified = True

            # forward reference to set to update replacement policy
            seti.reference(tag)

        return CacheResult(not miss, ll_op, replaced_tag)
