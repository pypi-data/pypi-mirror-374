from cachesim.cache import Cache
from cachesim.statistics import Stats
from typing import Self


class HierarchyResult:
    def __init__(self, address: int, nbytes: int, w_not_r: bool, hit: bool, replaced_tag: int, ll_ops: list[Self]):
        self.address = address
        self.nbytes = nbytes
        self.w_not_r = w_not_r
        self.hit = hit
        self.replaced_tag = replaced_tag
        self.ll_ops = ll_ops


class Level:
    def __init__(self, name: str, cache: Cache, lower: Self = None):
        """Creates a level of cache hierarchy:
            - *cache*: current level cache (data cache if i_cache!=None, unified cache otherwise)
            - *i_cache*: current level instruction cache, None if unified
            - *parent*: lower hierarchy level
        """
        self._name = name
        self._cache = cache
        self._lower = lower
        self._stats = Stats()

    def reference(self, address: int, nbytes: int, w_not_r: bool) -> HierarchyResult:
        """Look up a reference of *nbytes* starting from *address*
        """
        result = self._cache.reference(address, nbytes, w_not_r)

        # update stats
        self._stats.add(result)

        # handle operations to lower level
        ll = []
        for (ll_w, ll_addr, ll_nb) in result.ll_ops:
            ll_result = None
            if self._lower:
                ll_result = self._lower.reference(ll_addr, ll_nb, ll_w)
            else:
                ll_result = HierarchyResult(ll_addr, ll_nb, ll_w, True, None, [])
            ll.append(ll_result)

        return HierarchyResult(address, nbytes, w_not_r, result.hit, result.replaced_tag, ll)

    def invalidate(self) -> None:
        self._cache.invalidate()

    def flush(self) -> list[HierarchyResult]:
        res = self._cache.flush()

        # (si, tag) in res are written to lower level
        ll = []
        for (si, tag) in res:
            self._stats.bytes_written += self._cache._bpl

            address = self._cache._buildAddress(tag, si, 0)
            ll_result = None
            if self._lower:
                ll_result = self._lower.reference(address, self._cache._bpl, True)
            else:
                ll_result = HierarchyResult(address, self._cache._bpl, True, True, None, [])
            ll.append(ll_result)

        return ll
