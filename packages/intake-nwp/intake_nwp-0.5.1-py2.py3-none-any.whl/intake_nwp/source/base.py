import logging
from intake.source.base import DataSource


logger = logging.getLogger(__name__)


class DataSourceBase(DataSource):
    """Base behaviours for plugins in this repo."""

    container = "xarray"
    partition_access = True

    def _get_schema(self):
        """Make schema object, which embeds xarray object and some details"""
        from intake.source.base import Schema

        if self._ds is None:
            self._open_dataset()

            metadata = {
                "dims": dict(self._ds.sizes),
                "data_vars": {
                    k: list(self._ds[k].coords) for k in self._ds.data_vars.keys()
                },
                "coords": tuple(self._ds.coords.keys()),
            }
            metadata.update(self._ds.attrs)
            self._schema = Schema(
                datashape=None,
                dtype=None,
                shape=None,
                npartitions=None,
                extra_metadata=metadata,
            )
        return self._schema

    def read(self):
        """Return a version of the xarray with all the data in memory."""
        self._load_metadata()
        return self._ds.load()

    def read_chunked(self):
        """Return laxy xarray object."""
        self._load_metadata()
        return self._ds

    def to_dask(self):
        """Return xarray object where variables are dask arrays."""
        return self.read_chunked()

    def read_partition(self, i):
        """Fetch one chunk of data at tuple index i."""
        import numpy as np

        self._load_metadata()
        if not isinstance(i, (tuple, list)):
            raise TypeError("For Xarray sources, must specify partition as tuple")
        if isinstance(i, list):
            i = tuple(i)
        if hasattr(self._ds, 'variables') or i[0] in self._ds.coords:
            arr = self._ds[i[0]].data
            i = i[1:]
        else:
            arr = self._ds.data
        if isinstance(arr, np.ndarray):
            return arr
        return arr.blocks[i].compute()

    def close(self):
        """Delete open file from memory."""
        self._ds = None
        self._schema = None
