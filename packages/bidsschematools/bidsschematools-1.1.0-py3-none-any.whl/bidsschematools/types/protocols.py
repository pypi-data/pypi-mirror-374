"""BIDS validation context definitions

The classes in this module are used to define the context for BIDS validation.
The context is a namespace that contains relevant information about the dataset
as a whole and an individual file to be validated.

These classes are used to define the structure of the context,
but they cannot be instantiated directly.
Conforming subtypes need only match the structure of these classes,
and do not need to inherit from them.
It is recommended to import this module in an ``if TYPE_CHECKING`` block
to avoid import costs.

The classes use ``@property`` decorators to indicate that subtypes need only
provide read access to the attributes, and may restrict writing, for example,
when calculating attributes dynamically based on other attributes.

Note that some type checkers will not match classes that use
:class:`functools.cached_property`.
To permit this, add the following to your module::

    if TYPE_CHECKING:
        cached_property = property
    else:
        from functools import cached_property

This module has been auto-generated from the BIDS schema version 1.1.0.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Protocol

__all__ = ['Subjects', 'Dataset', 'Events', 'Aslcontext', 'M0scan', 'Magnitude', 'Magnitude1', 'Bval', 'Bvec', 'Channels', 'Electrodes', 'Coordsystem', 'Associations', 'Sessions', 'Subject', 'Gzip', 'DimInfo', 'XyztUnits', 'NiftiHeader', 'Ome', 'Tiff', 'Context']


class Subjects(Protocol):
    """Collections of subjects in dataset"""

    @property
    def sub_dirs(self) -> Sequence[str]:
        """Subjects as determined by sub-* directories"""

    @property
    def participant_id(self) -> Sequence[str] | None:
        """The participant_id column of participants.tsv"""


class Dataset(Protocol):
    """Properties and contents of the entire dataset"""

    @property
    def dataset_description(self) -> Mapping[str, Any]:
        """Contents of /dataset_description.json"""

    @property
    def tree(self) -> Mapping[str, Any]:
        """Tree view of all files in dataset"""

    @property
    def ignored(self) -> Sequence[str]:
        """Set of ignored files"""

    @property
    def datatypes(self) -> Sequence[str]:
        """Data types present in the dataset"""

    @property
    def modalities(self) -> Sequence[str]:
        """Modalities present in the dataset"""

    @property
    def subjects(self) -> Subjects:
        """Collections of subjects in dataset"""


class Events(Protocol):
    """Events file"""

    @property
    def path(self) -> str:
        """Path to associated events file"""

    @property
    def onset(self) -> Sequence[str] | None:
        """Contents of the onset column"""


class Aslcontext(Protocol):
    """ASL context file"""

    @property
    def path(self) -> str:
        """Path to associated aslcontext file"""

    @property
    def n_rows(self) -> int:
        """Number of rows in aslcontext.tsv"""

    @property
    def volume_type(self) -> Sequence[str] | None:
        """Contents of the volume_type column"""


class M0scan(Protocol):
    """M0 scan file"""

    @property
    def path(self) -> str:
        """Path to associated M0 scan file"""


class Magnitude(Protocol):
    """Magnitude image file"""

    @property
    def path(self) -> str:
        """Path to associated magnitude file"""


class Magnitude1(Protocol):
    """Magnitude1 image file"""

    @property
    def path(self) -> str:
        """Path to associated magnitude1 file"""


class Bval(Protocol):
    """B value file"""

    @property
    def path(self) -> str:
        """Path to associated bval file"""

    @property
    def n_cols(self) -> int:
        """Number of columns in bval file"""

    @property
    def n_rows(self) -> int:
        """Number of rows in bval file"""

    @property
    def values(self) -> Sequence[float]:
        """B-values contained in bval file"""


class Bvec(Protocol):
    """B vector file"""

    @property
    def path(self) -> str:
        """Path to associated bvec file"""

    @property
    def n_cols(self) -> int:
        """Number of columns in bvec file"""

    @property
    def n_rows(self) -> int:
        """Number of rows in bvec file"""


class Channels(Protocol):
    """Channels file"""

    @property
    def path(self) -> str:
        """Path to associated channels file"""

    @property
    def type(self) -> Sequence[str] | None:
        """Contents of the type column"""

    @property
    def short_channel(self) -> Sequence[str] | None:
        """Contents of the short_channel column"""

    @property
    def sampling_frequency(self) -> Sequence[str] | None:
        """Contents of the sampling_frequency column"""


class Electrodes(Protocol):
    """Electrodes file"""

    @property
    def path(self) -> str:
        """Path to associated electrodes.tsv file"""


class Coordsystem(Protocol):
    """Coordinate system file"""

    @property
    def path(self) -> str:
        """Path to associated coordsystem file"""


class Associations(Protocol):
    """Associated files, indexed by suffix, selected according to the inheritance principle"""

    @property
    def events(self) -> Events | None:
        """Events file"""

    @property
    def aslcontext(self) -> Aslcontext | None:
        """ASL context file"""

    @property
    def m0scan(self) -> M0scan | None:
        """M0 scan file"""

    @property
    def magnitude(self) -> Magnitude | None:
        """Magnitude image file"""

    @property
    def magnitude1(self) -> Magnitude1 | None:
        """Magnitude1 image file"""

    @property
    def bval(self) -> Bval | None:
        """B value file"""

    @property
    def bvec(self) -> Bvec | None:
        """B vector file"""

    @property
    def channels(self) -> Channels | None:
        """Channels file"""

    @property
    def electrodes(self) -> Electrodes | None:
        """Electrodes file"""

    @property
    def coordsystem(self) -> Coordsystem | None:
        """Coordinate system file"""


class Sessions(Protocol):
    """Collections of sessions in subject"""

    @property
    def ses_dirs(self) -> Sequence[str]:
        """Sessions as determined by ses-* directories"""

    @property
    def session_id(self) -> Sequence[str] | None:
        """The session_id column of sessions.tsv"""


class Subject(Protocol):
    """Properties and contents of the current subject"""

    @property
    def sessions(self) -> Sessions:
        """Collections of sessions in subject"""


class Gzip(Protocol):
    """Parsed contents of gzip header"""

    @property
    def timestamp(self) -> float:
        """Modification time, unix timestamp"""

    @property
    def filename(self) -> str | None:
        """Filename"""

    @property
    def comment(self) -> str | None:
        """Comment"""


class DimInfo(Protocol):
    """Metadata about dimensions data."""

    @property
    def freq(self) -> int:
        """These fields encode which spatial dimension (1, 2, or 3)."""

    @property
    def phase(self) -> int:
        """Corresponds to which acquisition dimension for MRI data."""

    @property
    def slice(self) -> int:
        """Slice dimensions."""


class XyztUnits(Protocol):
    """Units of pixdim[1..4]"""

    @property
    def xyz(self) -> Literal['unknown', 'meter', 'mm', 'um']:
        """String representing the unit of voxel spacing."""

    @property
    def t(self) -> Literal['unknown', 'sec', 'msec', 'usec']:
        """String representing the unit of inter-volume intervals."""


class NiftiHeader(Protocol):
    """Parsed contents of NIfTI header referenced elsewhere in schema."""

    @property
    def dim_info(self) -> DimInfo:
        """Metadata about dimensions data."""

    @property
    def dim(self) -> Sequence[int]:
        """Data seq dimensions."""

    @property
    def pixdim(self) -> Sequence[float]:
        """Grid spacings (unit per dimension)."""

    @property
    def shape(self) -> Sequence[int]:
        """Data array shape, equal to dim[1:dim[0] + 1]"""

    @property
    def voxel_sizes(self) -> Sequence[float]:
        """Voxel sizes, equal to pixdim[1:dim[0] + 1]"""

    @property
    def xyzt_units(self) -> XyztUnits:
        """Units of pixdim[1..4]"""

    @property
    def qform_code(self) -> int:
        """Use of the quaternion fields."""

    @property
    def sform_code(self) -> int:
        """Use of the affine fields."""

    @property
    def axis_codes(self) -> Sequence[Literal['R', 'L', 'A', 'P', 'S', 'I']]:
        """Orientation labels indicating primary direction of data axes defined with respect to the object of interest."""

    @property
    def mrs(self) -> Mapping[str, Any] | None:
        """NIfTI-MRS JSON fields"""


class Ome(Protocol):
    """Parsed contents of OME-XML header, which may be found in OME-TIFF or OME-ZARR files"""

    @property
    def PhysicalSizeX(self) -> float | None:
        """Pixels / @PhysicalSizeX"""

    @property
    def PhysicalSizeY(self) -> float | None:
        """Pixels / @PhysicalSizeY"""

    @property
    def PhysicalSizeZ(self) -> float | None:
        """Pixels / @PhysicalSizeZ"""

    @property
    def PhysicalSizeXUnit(self) -> str | None:
        """Pixels / @PhysicalSizeXUnit"""

    @property
    def PhysicalSizeYUnit(self) -> str | None:
        """Pixels / @PhysicalSizeYUnit"""

    @property
    def PhysicalSizeZUnit(self) -> str | None:
        """Pixels / @PhysicalSizeZUnit"""


class Tiff(Protocol):
    """TIFF file format metadata"""

    @property
    def version(self) -> int:
        """TIFF file format version (the second 2-byte block)"""


class Context(Protocol):
    """"""

    @property
    def schema(self) -> Mapping[str, Any]:
        """The BIDS specification schema"""

    @property
    def dataset(self) -> Dataset:
        """Properties and contents of the entire dataset"""

    @property
    def path(self) -> str:
        """Path of the current file"""

    @property
    def size(self) -> int:
        """Length of the current file in bytes"""

    @property
    def sidecar(self) -> Mapping[str, Any]:
        """Sidecar metadata constructed via the inheritance principle"""

    @property
    def associations(self) -> Associations:
        """Associated files, indexed by suffix, selected according to the inheritance principle"""

    @property
    def subject(self) -> Subject | None:
        """Properties and contents of the current subject"""

    @property
    def entities(self) -> Mapping[str, Any] | None:
        """Entities parsed from the current filename"""

    @property
    def datatype(self) -> str | None:
        """Datatype of current file, for examples, anat"""

    @property
    def suffix(self) -> str | None:
        """Suffix of current file"""

    @property
    def extension(self) -> str | None:
        """Extension of current file including initial dot"""

    @property
    def modality(self) -> str | None:
        """Modality of current file, for examples, MRI"""

    @property
    def columns(self) -> Mapping[str, Any] | None:
        """TSV columns, indexed by column header, values are arrays with column contents"""

    @property
    def json(self) -> Mapping[str, Any] | None:
        """Contents of the current JSON file"""

    @property
    def gzip(self) -> Gzip | None:
        """Parsed contents of gzip header"""

    @property
    def nifti_header(self) -> NiftiHeader | None:
        """Parsed contents of NIfTI header referenced elsewhere in schema."""

    @property
    def ome(self) -> Ome | None:
        """Parsed contents of OME-XML header, which may be found in OME-TIFF or OME-ZARR files"""

    @property
    def tiff(self) -> Tiff | None:
        """TIFF file format metadata"""
