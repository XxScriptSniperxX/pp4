from sysa.api import api
from collections import OrderedDict

class TableCriteria(api.Criteria):
    def __init__(self, criteria, ownership=False):
        proxy = criteria._proxy
        super().__init__(proxy, ownership)
        self._arrays = OrderedDict()
        self._inputs = OrderedDict()
        self._outputs = OrderedDict()

        for a in self._proxy.arrays():
            p = api.Parameter(a)
            self._arrays[a.id] = p
            if a.isInput():
                self._inputs[a.id] = p
            elif a.isOutput():
                self._outputs[a.id] = p

    @property
    def dim(self):
        """Number of input and output arrays (:class:`int`, read-only)."""
        return self._proxy.dim

    @property
    def arrays(self):
        """List of values of spline arrays (:class:`list`, read-only)."""
        return list(self._arrays.values())

    @property
    def items(self):
        """List of tuple (id, value) of spline arrays (:class:`list`, read-only)."""
        return list(self._arrays.items())

    @property
    def inputs(self):
        """List of values of input arrays (:class:`list`, read-only)."""
        return list(self._inputs.values())

    @property
    def outputs(self):
        """List of values of output arrays (:class:`list`, read-only)."""
        return list(self._outputs.values())
