class NDArray:
    def __init__(self, dimensions, data_size, base_address):
        self._dim = dimensions
        self._dsize = data_size
        self.base = base_address

    def __getitem__(self, indices):
        if isinstance(indices, int):
            indices = (indices, )
        assert len(indices) == len(self._dim), "Invalid number of dimensions"

        offset = indices[0]
        for n in range(1, len(self._dim)):
            assert indices[n] < self._dim[n], "Out of bounds"

            offset = offset * self._dim[n] + indices[n]

        return self.base + offset * self._dsize

    def __len__(self):
        stride = 1
        for d in self._dim:
            stride = stride * d

        return stride * self._dsize

    def after(self):
        return self.base + len(self)
