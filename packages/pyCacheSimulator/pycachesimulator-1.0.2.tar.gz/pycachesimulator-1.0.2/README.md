# pyCacheSimulator
A python library to simulate cache behavior.

## Table of contents
[[_TOC_]]

## Features
  * Configurable cache parameters
    * Number of lines
    * Bytes per line
    * Associativity
    * Replacement algorithms: FIFO, LRU
    * Write policy: write-back, write-through
    * Write-miss policy: write-allocate, no-write-allocate
  * Memory references: load and store
  * Cache invalidation and flushing
  * Multi-level cache hierarchies
  * UI functions to display:
    * Cache information and hierarchy structure
    * State of the cache directory
    * Results of memory references and cache flushes and invalidations
    * Statistics of a hierarchy level
  * Data structure library to easily compute memory addresses of n-dimensional arrays of arbitrary-size datatypes

## Future steps
Currently, a single hierarchy level can be used as the lower level for N child levels, for example, for multicore CPU or GPU -like caches.
However, the current version of ```pyCacheSimulator``` does not provide any means for thread safety.
For these kinds of hierarchies, the memory references must be serialized by the user.
It may be interesting to add some kind of support for multithreading with:
  * Cache coherency protocols
  * Memory models for consistency
  * Atomic and other advanced operations

## Installation
The package can be installed using ```pip```. It is available both at [PyPI](https://pypi.org/project/pyCacheSimulator/) and at the [GitLab Package registry](https://gitlab.com/bieito/pycachesim/-/packages/). You can read about the versions at the [Releases page](https://gitlab.com/bieito/pycachesim/-/releases).
```shell
python -m pip install pyCacheSimulator  # PyPI
python -m pip install pyCacheSimulator --index-url https://gitlab.com/api/v4/projects/64563558/packages/pypi/simple  # GitLab package registry
```

## Usage
An example for the usage of the library is included in the ```main.py``` file.
The example simulates some iterations of the following C code, with A starting at address ```0x2000``` and B just after A.

```c
#define N 8
float A[N][N], B[N];

for (i = 0; i < N; ++i) {
    for (j = 0; j < N; ++j) {
        A[i][j] = B[i];
        B[i] = A[j][i];
    }
}
```

Each iteration of the inner loop would be compiled to a pseudo-assembly like this.
Instructions are fetched from memory, and ```ld``` and ```st``` perform additional memory accesses.
```
ld  $r, %i($t1)    # load B[i]
st  $r, %ij($t0)   # store A[i, j]
ld  $r, %ji($t0)   # load A[j, i]
st  $r, $i($t1)    # store B[i]
```

The system uses a two level cache, with separate data/instruction L1 and unified L2.
The hierarchy information is printed at the beginning.
```python
    L2 = Level("L2", Cache(
        lines=16,
        line_size=16,
        associativity=4,
        write_back=True,
        write_allocate=True,
        replacement=LRU))
    L1i = Level("L1i", Cache(
        lines=4,
        line_size=8,
        associativity=1,
        write_back=False,
        write_allocate=False,
        replacement=FIFO), lower=L2)
    L1d = Level("L1d", Cache(
        lines=4,
        line_size=8,
        associativity=1,
        write_back=True,
        write_allocate=True,
        replacement=LRU), lower=L2)

    print(fmt.infoTree([L1i, L1d]))
```

The data structures are defined as per the C code:
```python
    N = 8
    A = C_float([N, N], 0x2000)  # float A[N][N], &a = 0x2000
    B = C_float([N], A.after())  # float B[N], b after a
    dsize = A._dsize             # sizeof(float)
```

The table of references for the L1d cache is printed during the execution of the code.
Some references to L1d generate references to L2, but these are skipped from the table for clarity.
The instruction-fetches are referenced to the L1i instead of the L1d.
The L1i is also updated (with collateral effects to the L2), but a table is not created for it.
```python
    table = ECTable(L1d, address_bits=16)
    table.separator()
    table.header()
    table.separator()

    for i in range(2):                                        # for (i = 0; i < 2; ++i)
        for j in range(2):                                        # for (j = 0; j < 2; ++j)
            L1i.reference(0x1000, 4, False)                           # instruction-fetch (load)
            table.load(f"B[{i}]", B[i], dsize, skip_ll=True)          # load B[i]
            L1i.reference(0x1004, 4, False)                           # instruction-fetch (store)
            table.store(f"A[{i},{j}]", A[i, j], dsize, skip_ll=True)  # store A[i][j]
            L1i.reference(0x1008, 4, False)                           # instruction-fetch (load)
            table.load(f"A[{j},{i}]", A[j, i], dsize, skip_ll=True)   # load A[j][i]
            L1i.reference(0x100C, 4, False)                           # instruction-fetch (store)
            table.store(f"B[{i}]", B[i], dsize, skip_ll=True)         # store B[i]
```

Then, the statistics and the state of the directory of each level are formatted and printed.
```python
    print(fmt.statistics(L1i))
    print(fmt.directory(L1i, 16))

    print(fmt.statistics(L1d))
    print(fmt.directory(L1d, 16))

    print(fmt.statistics(L2))
    print(fmt.directory(L2, 16))
```

Last, the L2 cache is flushed, formatting the result to show the modified lines that would be written to memory.
```python
    print(fmt.flush(L2, L2.flush(), 16))
```

The output that this program generates to the standard output is:
```
MEMORY
 L2 Cache 256 B, 16 B/line, 16 lines, 4-way associative/LRU (4 sets), write-back, write-allocate
  L1i Cache 32 B, 8 B/line, 4 lines, direct mapped, write-through, no-write-allocate
  L1d Cache 32 B, 8 B/line, 4 lines, direct mapped, write-back, write-allocate

---------+-------+--------------+----------------+------+----------+---------------------------------
  DATA   | LEVEL | ADDRESS+SIZE | SET:TAG+OFFSET | HIT? | REPLACES |           LOWER-LEVEL           
---------+-------+--------------+----------------+------+----------+---------------------------------
  B[0]   |  L1d  | (R)0x2100+4  |    0:108+0     | miss |          | [L2]   (R)0x2100+8              
 A[0,0]  |  L1d  | (W)0x2000+4  |    0:100+0     | miss |   108    | [L2]   (R)0x2000+8              
 A[0,0]  |  L1d  | (R)0x2000+4  |    0:100+0     | hit  |          |                                 
  B[0]   |  L1d  | (W)0x2100+4  |    0:108+0     | miss |   100    | [L2]   (W)0x2000+8, (R)0x2100+8 
  B[0]   |  L1d  | (R)0x2100+4  |    0:108+0     | hit  |          |                                 
 A[0,1]  |  L1d  | (W)0x2004+4  |    0:100+4     | miss |   108    | [L2]   (W)0x2100+8, (R)0x2000+8 
 A[1,0]  |  L1d  | (R)0x2020+4  |    0:101+0     | miss |   100    | [L2]   (W)0x2000+8, (R)0x2020+8 
  B[0]   |  L1d  | (W)0x2100+4  |    0:108+0     | miss |   101    | [L2]   (R)0x2100+8              
  B[1]   |  L1d  | (R)0x2104+4  |    0:108+4     | hit  |          |                                 
 A[1,0]  |  L1d  | (W)0x2020+4  |    0:101+0     | miss |   108    | [L2]   (W)0x2100+8, (R)0x2020+8 
 A[0,1]  |  L1d  | (R)0x2004+4  |    0:100+4     | miss |   101    | [L2]   (W)0x2020+8, (R)0x2000+8 
  B[1]   |  L1d  | (W)0x2104+4  |    0:108+4     | miss |   100    | [L2]   (R)0x2100+8              
  B[1]   |  L1d  | (R)0x2104+4  |    0:108+4     | hit  |          |                                 
 A[1,1]  |  L1d  | (W)0x2024+4  |    0:101+4     | miss |   108    | [L2]   (W)0x2100+8, (R)0x2020+8 
 A[1,1]  |  L1d  | (R)0x2024+4  |    0:101+4     | hit  |          |                                 
  B[1]   |  L1d  | (W)0x2104+4  |    0:108+4     | miss |   101    | [L2]   (W)0x2020+8, (R)0x2100+8 
---------+-------+--------------+----------------+------+----------+---------------------------------

L1i statistics:
  16 references, 14 cache hits, miss rate = 0.1250
  0 lines replaced
  16 B read from L2
  0 B written to L2
L1i cache directory:
  SET | TAG | MODIFIED
 -----+-----+----------
   0  | 080 |         
   1  | 080 |         

L1d statistics:
  16 references, 5 cache hits, miss rate = 0.6875
  10 lines replaced
  88 B read from L2
  56 B written to L2
L1d cache directory:
  SET | TAG | MODIFIED
 -----+-----+----------
   0  | 108 |    *    

L2 statistics:
  20 references, 16 cache hits, miss rate = 0.2000
  0 lines replaced
  64 B read from MEM
  0 B written to MEM
L2 cache directory:
  SET | TAG | MODIFIED
 -----+-----+----------
   0  | 040 |         
   0  | 084 |    *    
   0  | 080 |    *    
   2  | 080 |    *    

L2 flush:
  0:084 -> [MEM] (W)0x2100+10
  0:080 -> [MEM] (W)0x2000+10
  2:080 -> [MEM] (W)0x2020+10

```

## Development
UML class diagrams can be found under the ```doc/``` directory.

![UML Class diagram of pyCacheSim](https://gitlab.com/bieito/pycachesim/-/raw/main/doc/uml_classes.svg "UML Class diagram of pyCacheSim")
