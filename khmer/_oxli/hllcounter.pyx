# cython: c_string_type=unicode, c_string_encoding=utf8
from cython.operator cimport dereference as deref, address

from parsing cimport CpFastxReader
from .utils cimport _bstring, _ustring

cdef class HLLCounter:
    """HyperLogLog counter.

    A HyperLogLog counter is a probabilistic data structure specialized on
    cardinality estimation.
    There is a precision/memory consumption trade-off: error rate determines
    how much memory is consumed.

    # Creating a new HLLCounter:

    >>> khmer.HLLCounter(error_rate, ksize)

    where the default values are:
      - error_rate: 0.01
      - ksize: 20
    """

    def __cinit__(self, double error_rate=0.01, int ksize=20):
        self._this.reset(new CpHLLCounter(error_rate, ksize))

    def __len__(self):
        """Return the cardinality estimate."""
        return self.estimate_cardinality()

    def add(self, kmer):
        """Add a k-mer to the counter."""
        deref(self._this).add(_bstring(kmer))

    def estimate_cardinality(self):
        """Return the current estimative."""
        return deref(self._this).estimate_cardinality()

    def consume_string(self, seq):
        """Break a sequence into k-mers and add each k-mer to the counter."""
        return deref(self._this).consume_string(_bstring(seq))

    cpdef tuple consume_seqfile(self, filename, bool stream_records=False):
        "Read sequences from file, break into k-mers, "
        "and add each k-mer to the counter. If optional keyword 'stream_out' "
        "is True, also prints each sequence to stdout."
        cdef unsigned long long n_consumed = 0
        cdef unsigned int total_reads = 0

        deref(self._this).consume_seqfile[CpFastxReader](
                             _bstring(filename), stream_records,
                             total_reads, n_consumed)

        return total_reads, n_consumed

    def merge(self, HLLCounter other):
        """Merge other counter into this one."""
        deref(self._this).merge(deref(other._this))

    @property
    def alpha(self):
        """alpha constant for this HLL counter."""
        return deref(self._this).get_alpha()

    @property
    def error_rate(self):
        "Error rate for this HLL counter."
        "Can be changed prior to first counting, but becomes read-only after "
        "that (raising AttributeError)"
        return deref(self._this).get_erate()

    @error_rate.setter
    def error_rate(self, erate):
        deref(self._this).set_erate(float(erate))

    @error_rate.deleter
    def error_rate(self):
        raise TypeError("Cannot delete attribute")

    @property
    def ksize(self):
        "k-mer size for this HLL counter."
        "Can be changed prior to first counting, but becomes read-only after "
        "that (raising AttributeError)"
        return deref(self._this).get_ksize()

    @ksize.setter
    def ksize(self, object new_k):
        if new_k <= 0:
            raise ValueError("Please set k-mer size to a value greater "
                             "than zero")
        if isinstance(new_k, float):
            raise TypeError("Please use an integer value for k-mer size")
        deref(self._this).set_ksize(<int>new_k)

    @ksize.deleter
    def ksize(self):
        raise TypeError("Cannot delete attribute")

    @property
    def counters(self):
        """Read-only internal counters."""
        return deref(self._this).get_M()
