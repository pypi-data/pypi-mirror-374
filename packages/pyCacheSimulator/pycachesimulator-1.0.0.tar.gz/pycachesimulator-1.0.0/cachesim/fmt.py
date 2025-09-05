from cachesim.hierarchy import Level, HierarchyResult

from math import ceil, log2


def info(level: Level) -> str:
    """Get a string with the cache configuration"""
    cache = level._cache
    nm = f"{level._name} " if level._name else ""
    size = len(cache)
    rep = str(cache._sets[0]._rep)
    wb = f"write-{'back' if cache._wb else 'through'}"
    wa = f"{'' if cache._wa else 'no-'}write-allocate"
    assoc = f"{cache._assoc}-way associative/{rep} ({cache._nsets} sets)"
    if cache._assoc == 1:
        assoc = "direct mapped"
    elif cache._assoc == cache._lines:
        assoc = f"fully associative/{rep}"

    return f"{nm}Cache {size} B, {cache._bpl} B/line, {cache._lines} lines, {assoc}, {wb}, {wa}"


def infoTree(upper: list[Level]) -> str:
    """Get a string with the hierarchy configuration, starting from the upmost levels *upper*"""
    children = {}
    roots = []

    visited = set()
    next_nodes = set(h for h in upper)
    while next_nodes:
        node = next_nodes.pop()

        if not node in children:
            children[node] = set()

        visited.add(node)

        if node._lower:
            # add node to parent's children
            if not node._lower in children:
                children[node._lower] = set()
            children[node._lower].add(node)

            # add parent to next_nodes
            if node._lower not in visited:
                next_nodes.add(node._lower)
        else:
            roots.append(node)

    #s = "Cache hierarchy:"
    s = "MEMORY"
    next_nodes = [(1, r) for r in roots]
    while next_nodes:
        (level, node) = next_nodes.pop()
        next_nodes.extend((level+1, c) for c in children[node])

        s += f"\n{' '*level}{info(node)}"

    return s


def directory(level: Level, address_bits: int, skip_invalid: bool = True) -> str:
    """Get a string with a table with the cache state"""
    cache = level._cache
    off_bits = int(ceil(log2(cache._bpl)))
    set_bits = int(ceil(log2(cache._nsets)))
    align_set = max(len("SET"), int(ceil(set_bits / 4)))
    tag_bits = address_bits - off_bits - set_bits
    align_tag = max(len("TAG"), int(ceil(tag_bits / 4)))

    align_bm = len("MODIFIED")

    directory = f"{level._name} cache directory:"
    directory += f"\n  {'SET':^{align_set}s} | {'TAG':^{align_tag}s} | {'MODIFIED':^{align_bm}s}"
    directory += f"\n -{'-'*align_set}-+-{'-'*align_tag}-+-{'-'*align_bm}-"

    for (si, s) in enumerate(cache._sets):
        set_idx = f"{si:^0{int(ceil(set_bits / 4))}X}"

        for line in s.lines:
            tag = f"{line.tag:0{int(ceil(tag_bits / 4))}X}" if line.valid else ""
            modified = '*' if line.valid and line.modified else ''

            if line.valid or not skip_invalid:
                directory += f"\n  {set_idx:^{align_set}} | {tag:>{align_tag}s} | {modified:^{align_bm}}"

    return directory


def header(level: Level, address_bits: int) -> str:
    """Get a string with a header for a table of references"""
    cache = level._cache

    clev = "LEVEL"
    clev_align = max(len(clev), len(level._name))

    addr = "ADDRESS+SIZE"
    addr_align = max(len(addr), 4 + 2 + int(ceil(address_bits / 4)) + 2)  # 4 (R/W) + 2 (0x) + addr + 2 (+size)

    off_bits = int(ceil(log2(cache._bpl)))
    align_offset = int(ceil(off_bits / 4))
    set_bits = int(ceil(log2(cache._nsets)))
    align_set = int(ceil(set_bits / 4))
    tag_bits = address_bits - off_bits - set_bits
    align_tag = int(ceil(tag_bits / 4))
    sto = f"SET:TAG+OFFSET"
    sto_align = max(len(sto), align_set + align_tag + align_offset + 2)

    rep = "REPLACES"
    rep_align = max(len(rep), align_tag)

    #lln = level._lower._name if level._lower else "MEM"
    lln = "LOWER-LEVEL"
    lln_align = 32

    return f"{clev:^{clev_align}} | {addr:^{addr_align}} | {sto:^{sto_align}} | HIT? | {rep:^{rep_align}} | {lln:^{lln_align}}"


def hseparator(level: Level, address_bits: int) -> str:
    """Get a string to separate the header for a table of references"""
    cache = level._cache

    clev = "LEVEL"
    clev_align = max(len(clev), len(level._name))

    addr = "ADDRESS+SIZE"
    addr_align = max(len(addr), 4 + 2 + int(ceil(address_bits / 4)) + 2)  # 4 (R/W) + 2 (0x) + addr + 2 (+size)

    off_bits = int(ceil(log2(cache._bpl)))
    align_offset = int(ceil(off_bits / 4))
    set_bits = int(ceil(log2(cache._nsets)))
    align_set = int(ceil(set_bits / 4))
    tag_bits = address_bits - off_bits - set_bits
    align_tag = int(ceil(tag_bits / 4))
    sto = f"SET:TAG+OFFSET"
    sto_align = max(len(sto), align_set + align_tag + align_offset + 2)

    rep = "REPLACES"
    rep_align = max(len(rep), align_tag)

    #lln = level._lower._name if level._lower else "MEM"
    lln = "LOWER-LEVEL"
    lln_align = 32

    return f"{'-'*clev_align}-+-{'-'*addr_align}-+-{'-'*sto_align}-+------+-{'-'*rep_align}-+-{'-'*lln_align}"


def reference(level: Level, result: HierarchyResult, address_bits: int) -> list[str]:
    """Format cache result *result* for access to address *address* as a row for a table of references"""
    cache = level._cache
    # split address and send reference
    (tag, idx, offset) = cache.splitAddress(result.address)
    (hit, replaced_tag) = (result.hit, result.replaced_tag)
    ll_writes = []
    for op in result.ll_ops:
        #if op.w_not_r:
        ll_writes.append((op.address, op.nbytes, op.w_not_r))

    # format
    clev = level._name
    clev_align = max(len("LEVEL"), len(level._name))

    op = "(W)" if result.w_not_r else "(R)"
    addr = f"{op}0x{result.address:0{int(ceil(address_bits / 4))}X}+{result.nbytes:X}"
    addr_align = max(len("ADDRESS+SIZE"), 4 + 2 + int(ceil(address_bits / 4)) + 2)  # 4 (R/W) + 2 (0x) + addr + 2 (+size)

    off_bits = int(ceil(log2(cache._bpl)))
    align_offset = int(ceil(off_bits / 4))
    set_bits = int(ceil(log2(cache._nsets)))
    align_set = int(ceil(set_bits / 4))
    tag_bits = address_bits - off_bits - set_bits
    align_tag = int(ceil(tag_bits / 4))
    stoh = f"SET:TAG+OFFSET"
    sto = f"{idx:>0{align_set}X}:{tag:0{align_tag}X}+{offset:0{align_offset}X}"
    sto_align = max(len(stoh), len(sto))

    hm = "hit" if hit else "miss"
    rep = f"{replaced_tag:0{align_tag}X}" if replaced_tag else " " * align_tag
    rep_align = max(len("REPLACES"), align_tag)
    lln = level._lower._name if level._lower else "MEM"
    mw = f"{'[' + lln + ']':6} " + ', '.join(f"({'W' if ll_write[2] else 'R'})0x{ll_write[0]:X}+{ll_write[1]:X}" for ll_write in ll_writes) if ll_writes else ""
    mw_align = max(32, len(mw))
    _mw = f"{mw:<{mw_align}}" if ll_writes else f"{mw:^{mw_align}}"

    rows = [f"{clev:^{clev_align}} | {addr:^{addr_align}} | {sto:^{sto_align}} | {hm:^4} | {rep:^{rep_align}} | {_mw}"]
    if level._lower:
        for op in result.ll_ops:
            rows.extend(reference(level._lower, op, address_bits))

    return rows


def writeChain(level: Level, result: list[HierarchyResult], address_bits: int, _level: int = 0) -> list[str]:
    cache = level._cache
    off_bits = int(ceil(log2(cache._bpl)))
    align_offset = int(ceil(off_bits / 4))
    set_bits = int(ceil(log2(cache._nsets)))
    align_set = int(ceil(set_bits / 4))
    tag_bits = address_bits - off_bits - set_bits
    align_tag = int(ceil(tag_bits / 4))

    nl = level._name

    mw = []
    for res in result:
        if res.w_not_r:
            (tag, si, _) = level._cache.splitAddress(res.address)
            lln = level._lower._name if level._lower else "MEM"
            mw.append(f"{'  '*_level}{si:0{align_set}X}:{tag:0{align_tag}X} -> [{lln}] (W)0x{res.address:X}+{res.nbytes:X}")

        if level._lower:
            ll = writeChain(level._lower, res.ll_ops, address_bits, _level+1)
            mw.extend(ll)

    return mw

def flush(level: Level, result: list[HierarchyResult], address_bits: int) -> str:
    mw = writeChain(level, result, address_bits, 1)
    return f"{level._name} flush:\n{'\n'.join(mw)}"


def statistics(level: Level) -> str:
    stats = level._stats
    ll = level._lower._name if level._lower else "MEM"
    l = [f"{level._name} statistics:",
        f"\n  {stats.references} references, {stats.hits} cache hits, miss rate = {1.0 - stats.hits/stats.references if stats.references > 0 else 0.0:.4f}",
        f"\n  {stats.lines_replaced} lines replaced",
        f"\n  {stats.bytes_read} B read from {ll}",
        f"\n  {stats.bytes_written} B written to {ll}"
    ]

    return ''.join(l)
