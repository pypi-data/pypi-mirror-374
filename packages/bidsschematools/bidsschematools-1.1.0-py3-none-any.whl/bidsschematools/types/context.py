"""BIDS validation context dataclasses

The classes in this module may be used to populate the context for BIDS validation.

This module has been auto-generated from the BIDS schema version 1.1.0.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

TYPE_CHECKING = False
if TYPE_CHECKING or "sphinx.ext.autodoc" in sys.modules:
    from collections.abc import Mapping, Sequence
    from typing import Any, Literal

    from . import protocols

if sys.version_info >= (3, 10):
    dc_kwargs = {"slots": True, "frozen": True}
else:  # PY39
    dc_kwargs = {"frozen": True}

__all__ = ['Subjects', 'Dataset', 'Events', 'Aslcontext', 'M0scan', 'Magnitude', 'Magnitude1', 'Bval', 'Bvec', 'Channels', 'Electrodes', 'Coordsystem', 'Associations', 'Sessions', 'Subject', 'Gzip', 'DimInfo', 'XyztUnits', 'NiftiHeader', 'Ome', 'Tiff', 'Context']


@dataclass(**dc_kwargs)
class Subjects:
    """Collections of subjects in dataset

    Attributes
    ----------
    sub_dirs: Sequence[str]
        Subjects as determined by sub-* directories

    participant_id: Sequence[str] | None
        The participant_id column of participants.tsv

"""

    sub_dirs: Sequence[str]
    #: Subjects as determined by sub-* directories

    participant_id: Sequence[str] | None = None
    #: The participant_id column of participants.tsv


@dataclass(**dc_kwargs)
class Dataset:
    """Properties and contents of the entire dataset

    Attributes
    ----------
    dataset_description: Mapping[str, Any]
        Contents of /dataset_description.json

    tree: Mapping[str, Any]
        Tree view of all files in dataset

    ignored: Sequence[str]
        Set of ignored files

    datatypes: Sequence[str]
        Data types present in the dataset

    modalities: Sequence[str]
        Modalities present in the dataset

    subjects: protocols.Subjects
        Collections of subjects in dataset

"""

    dataset_description: Mapping[str, Any]
    #: Contents of /dataset_description.json

    tree: Mapping[str, Any]
    #: Tree view of all files in dataset

    ignored: Sequence[str]
    #: Set of ignored files

    datatypes: Sequence[str]
    #: Data types present in the dataset

    modalities: Sequence[str]
    #: Modalities present in the dataset

    subjects: protocols.Subjects
    #: Collections of subjects in dataset


@dataclass(**dc_kwargs)
class Events:
    """Events file

    Attributes
    ----------
    path: str
        Path to associated events file

    onset: Sequence[str] | None
        Contents of the onset column

"""

    path: str
    #: Path to associated events file

    onset: Sequence[str] | None = None
    #: Contents of the onset column


@dataclass(**dc_kwargs)
class Aslcontext:
    """ASL context file

    Attributes
    ----------
    path: str
        Path to associated aslcontext file

    n_rows: int
        Number of rows in aslcontext.tsv

    volume_type: Sequence[str] | None
        Contents of the volume_type column

"""

    path: str
    #: Path to associated aslcontext file

    n_rows: int
    #: Number of rows in aslcontext.tsv

    volume_type: Sequence[str] | None = None
    #: Contents of the volume_type column


@dataclass(**dc_kwargs)
class M0scan:
    """M0 scan file

    Attributes
    ----------
    path: str
        Path to associated M0 scan file

"""

    path: str
    #: Path to associated M0 scan file


@dataclass(**dc_kwargs)
class Magnitude:
    """Magnitude image file

    Attributes
    ----------
    path: str
        Path to associated magnitude file

"""

    path: str
    #: Path to associated magnitude file


@dataclass(**dc_kwargs)
class Magnitude1:
    """Magnitude1 image file

    Attributes
    ----------
    path: str
        Path to associated magnitude1 file

"""

    path: str
    #: Path to associated magnitude1 file


@dataclass(**dc_kwargs)
class Bval:
    """B value file

    Attributes
    ----------
    path: str
        Path to associated bval file

    n_cols: int
        Number of columns in bval file

    n_rows: int
        Number of rows in bval file

    values: Sequence[float]
        B-values contained in bval file

"""

    path: str
    #: Path to associated bval file

    n_cols: int
    #: Number of columns in bval file

    n_rows: int
    #: Number of rows in bval file

    values: Sequence[float]
    #: B-values contained in bval file


@dataclass(**dc_kwargs)
class Bvec:
    """B vector file

    Attributes
    ----------
    path: str
        Path to associated bvec file

    n_cols: int
        Number of columns in bvec file

    n_rows: int
        Number of rows in bvec file

"""

    path: str
    #: Path to associated bvec file

    n_cols: int
    #: Number of columns in bvec file

    n_rows: int
    #: Number of rows in bvec file


@dataclass(**dc_kwargs)
class Channels:
    """Channels file

    Attributes
    ----------
    path: str
        Path to associated channels file

    type: Sequence[str] | None
        Contents of the type column

    short_channel: Sequence[str] | None
        Contents of the short_channel column

    sampling_frequency: Sequence[str] | None
        Contents of the sampling_frequency column

"""

    path: str
    #: Path to associated channels file

    type: Sequence[str] | None = None
    #: Contents of the type column

    short_channel: Sequence[str] | None = None
    #: Contents of the short_channel column

    sampling_frequency: Sequence[str] | None = None
    #: Contents of the sampling_frequency column


@dataclass(**dc_kwargs)
class Electrodes:
    """Electrodes file

    Attributes
    ----------
    path: str
        Path to associated electrodes.tsv file

"""

    path: str
    #: Path to associated electrodes.tsv file


@dataclass(**dc_kwargs)
class Coordsystem:
    """Coordinate system file

    Attributes
    ----------
    path: str
        Path to associated coordsystem file

"""

    path: str
    #: Path to associated coordsystem file


@dataclass(**dc_kwargs)
class Associations:
    """Associated files, indexed by suffix, selected according to the inheritance principle

    Attributes
    ----------
    events: protocols.Events | None
        Events file

    aslcontext: protocols.Aslcontext | None
        ASL context file

    m0scan: protocols.M0scan | None
        M0 scan file

    magnitude: protocols.Magnitude | None
        Magnitude image file

    magnitude1: protocols.Magnitude1 | None
        Magnitude1 image file

    bval: protocols.Bval | None
        B value file

    bvec: protocols.Bvec | None
        B vector file

    channels: protocols.Channels | None
        Channels file

    electrodes: protocols.Electrodes | None
        Electrodes file

    coordsystem: protocols.Coordsystem | None
        Coordinate system file

"""

    events: protocols.Events | None = None
    #: Events file

    aslcontext: protocols.Aslcontext | None = None
    #: ASL context file

    m0scan: protocols.M0scan | None = None
    #: M0 scan file

    magnitude: protocols.Magnitude | None = None
    #: Magnitude image file

    magnitude1: protocols.Magnitude1 | None = None
    #: Magnitude1 image file

    bval: protocols.Bval | None = None
    #: B value file

    bvec: protocols.Bvec | None = None
    #: B vector file

    channels: protocols.Channels | None = None
    #: Channels file

    electrodes: protocols.Electrodes | None = None
    #: Electrodes file

    coordsystem: protocols.Coordsystem | None = None
    #: Coordinate system file


@dataclass(**dc_kwargs)
class Sessions:
    """Collections of sessions in subject

    Attributes
    ----------
    ses_dirs: Sequence[str]
        Sessions as determined by ses-* directories

    session_id: Sequence[str] | None
        The session_id column of sessions.tsv

"""

    ses_dirs: Sequence[str]
    #: Sessions as determined by ses-* directories

    session_id: Sequence[str] | None = None
    #: The session_id column of sessions.tsv


@dataclass(**dc_kwargs)
class Subject:
    """Properties and contents of the current subject

    Attributes
    ----------
    sessions: protocols.Sessions
        Collections of sessions in subject

"""

    sessions: protocols.Sessions
    #: Collections of sessions in subject


@dataclass(**dc_kwargs)
class Gzip:
    """Parsed contents of gzip header

    Attributes
    ----------
    timestamp: float
        Modification time, unix timestamp

    filename: str | None
        Filename

    comment: str | None
        Comment

"""

    timestamp: float
    #: Modification time, unix timestamp

    filename: str | None = None
    #: Filename

    comment: str | None = None
    #: Comment


@dataclass(**dc_kwargs)
class DimInfo:
    """Metadata about dimensions data.

    Attributes
    ----------
    freq: int
        These fields encode which spatial dimension (1, 2, or 3).

    phase: int
        Corresponds to which acquisition dimension for MRI data.

    slice: int
        Slice dimensions.

"""

    freq: int
    #: These fields encode which spatial dimension (1, 2, or 3).

    phase: int
    #: Corresponds to which acquisition dimension for MRI data.

    slice: int
    #: Slice dimensions.


@dataclass(**dc_kwargs)
class XyztUnits:
    """Units of pixdim[1..4]

    Attributes
    ----------
    xyz: Literal['unknown', 'meter', 'mm', 'um']
        String representing the unit of voxel spacing.

    t: Literal['unknown', 'sec', 'msec', 'usec']
        String representing the unit of inter-volume intervals.

"""

    xyz: Literal['unknown', 'meter', 'mm', 'um']
    #: String representing the unit of voxel spacing.

    t: Literal['unknown', 'sec', 'msec', 'usec']
    #: String representing the unit of inter-volume intervals.


@dataclass(**dc_kwargs)
class NiftiHeader:
    """Parsed contents of NIfTI header referenced elsewhere in schema.

    Attributes
    ----------
    dim_info: protocols.DimInfo
        Metadata about dimensions data.

    dim: Sequence[int]
        Data seq dimensions.

    pixdim: Sequence[float]
        Grid spacings (unit per dimension).

    shape: Sequence[int]
        Data array shape, equal to dim[1:dim[0] + 1]

    voxel_sizes: Sequence[float]
        Voxel sizes, equal to pixdim[1:dim[0] + 1]

    xyzt_units: protocols.XyztUnits
        Units of pixdim[1..4]

    qform_code: int
        Use of the quaternion fields.

    sform_code: int
        Use of the affine fields.

    axis_codes: Sequence[Literal['R', 'L', 'A', 'P', 'S', 'I']]
        Orientation labels indicating primary direction of data axes defined with respect to the object of interest.

    mrs: Mapping[str, Any] | None
        NIfTI-MRS JSON fields

"""

    dim_info: protocols.DimInfo
    #: Metadata about dimensions data.

    dim: Sequence[int]
    #: Data seq dimensions.

    pixdim: Sequence[float]
    #: Grid spacings (unit per dimension).

    shape: Sequence[int]
    #: Data array shape, equal to dim[1:dim[0] + 1]

    voxel_sizes: Sequence[float]
    #: Voxel sizes, equal to pixdim[1:dim[0] + 1]

    xyzt_units: protocols.XyztUnits
    #: Units of pixdim[1..4]

    qform_code: int
    #: Use of the quaternion fields.

    sform_code: int
    #: Use of the affine fields.

    axis_codes: Sequence[Literal['R', 'L', 'A', 'P', 'S', 'I']]
    #: Orientation labels indicating primary direction of data axes defined with respect to the object of interest.

    mrs: Mapping[str, Any] | None = None
    #: NIfTI-MRS JSON fields


@dataclass(**dc_kwargs)
class Ome:
    """Parsed contents of OME-XML header, which may be found in OME-TIFF or OME-ZARR files

    Attributes
    ----------
    PhysicalSizeX: float | None
        Pixels / @PhysicalSizeX

    PhysicalSizeY: float | None
        Pixels / @PhysicalSizeY

    PhysicalSizeZ: float | None
        Pixels / @PhysicalSizeZ

    PhysicalSizeXUnit: str | None
        Pixels / @PhysicalSizeXUnit

    PhysicalSizeYUnit: str | None
        Pixels / @PhysicalSizeYUnit

    PhysicalSizeZUnit: str | None
        Pixels / @PhysicalSizeZUnit

"""

    PhysicalSizeX: float | None = None
    #: Pixels / @PhysicalSizeX

    PhysicalSizeY: float | None = None
    #: Pixels / @PhysicalSizeY

    PhysicalSizeZ: float | None = None
    #: Pixels / @PhysicalSizeZ

    PhysicalSizeXUnit: str | None = None
    #: Pixels / @PhysicalSizeXUnit

    PhysicalSizeYUnit: str | None = None
    #: Pixels / @PhysicalSizeYUnit

    PhysicalSizeZUnit: str | None = None
    #: Pixels / @PhysicalSizeZUnit


@dataclass(**dc_kwargs)
class Tiff:
    """TIFF file format metadata

    Attributes
    ----------
    version: int
        TIFF file format version (the second 2-byte block)

"""

    version: int
    #: TIFF file format version (the second 2-byte block)


@dataclass(**dc_kwargs)
class Context:
    """

    Attributes
    ----------
    schema: Mapping[str, Any]
        The BIDS specification schema

    dataset: protocols.Dataset
        Properties and contents of the entire dataset

    path: str
        Path of the current file

    size: int
        Length of the current file in bytes

    sidecar: Mapping[str, Any]
        Sidecar metadata constructed via the inheritance principle

    associations: protocols.Associations
        Associated files, indexed by suffix, selected according to the inheritance principle

    subject: protocols.Subject | None
        Properties and contents of the current subject

    entities: Mapping[str, Any] | None
        Entities parsed from the current filename

    datatype: str | None
        Datatype of current file, for examples, anat

    suffix: str | None
        Suffix of current file

    extension: str | None
        Extension of current file including initial dot

    modality: str | None
        Modality of current file, for examples, MRI

    columns: Mapping[str, Any] | None
        TSV columns, indexed by column header, values are arrays with column contents

    json: Mapping[str, Any] | None
        Contents of the current JSON file

    gzip: protocols.Gzip | None
        Parsed contents of gzip header

    nifti_header: protocols.NiftiHeader | None
        Parsed contents of NIfTI header referenced elsewhere in schema.

    ome: protocols.Ome | None
        Parsed contents of OME-XML header, which may be found in OME-TIFF or OME-ZARR files

    tiff: protocols.Tiff | None
        TIFF file format metadata

"""

    schema: Mapping[str, Any]
    #: The BIDS specification schema

    dataset: protocols.Dataset
    #: Properties and contents of the entire dataset

    path: str
    #: Path of the current file

    size: int
    #: Length of the current file in bytes

    sidecar: Mapping[str, Any]
    #: Sidecar metadata constructed via the inheritance principle

    associations: protocols.Associations
    #: Associated files, indexed by suffix, selected according to the inheritance principle

    subject: protocols.Subject | None = None
    #: Properties and contents of the current subject

    entities: Mapping[str, Any] | None = None
    #: Entities parsed from the current filename

    datatype: str | None = None
    #: Datatype of current file, for examples, anat

    suffix: str | None = None
    #: Suffix of current file

    extension: str | None = None
    #: Extension of current file including initial dot

    modality: str | None = None
    #: Modality of current file, for examples, MRI

    columns: Mapping[str, Any] | None = None
    #: TSV columns, indexed by column header, values are arrays with column contents

    json: Mapping[str, Any] | None = None
    #: Contents of the current JSON file

    gzip: protocols.Gzip | None = None
    #: Parsed contents of gzip header

    nifti_header: protocols.NiftiHeader | None = None
    #: Parsed contents of NIfTI header referenced elsewhere in schema.

    ome: protocols.Ome | None = None
    #: Parsed contents of OME-XML header, which may be found in OME-TIFF or OME-ZARR files

    tiff: protocols.Tiff | None = None
    #: TIFF file format metadata
