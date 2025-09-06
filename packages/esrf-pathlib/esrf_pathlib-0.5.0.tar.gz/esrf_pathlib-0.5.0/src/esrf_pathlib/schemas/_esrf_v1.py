import datetime
import os
from dataclasses import dataclass
from typing import List
from typing import Optional

from . import _base
from ._base import BEAMLINE_DIR_TO_NAME
from ._base import BEAMLINE_NAME_TO_DIR
from ._base import get_default_data_root

_PATH_SEGMENTS: List[_base.PathSegment] = [
    _base.PathSegment(
        match_pattern=r"(?P<data_root>.*?)",
        render_template="{data_root}",
    ),
    _base.PathSegment(
        match_pattern=rf"{_base.SEP}(?P<proposal>{_base.NOTSEP}+)",
        render_template="{proposal}",
    ),
    _base.PathSegment(
        match_pattern=rf"{_base.SEP}(?P<beamline>{_base.NOTSEP}+)",
        render_template="{beamline}",
    ),
    _base.PathSegment(
        match_pattern=rf"{_base.SEP}(?P<session_date>\d{{8}})",
        render_template="{session_date:%Y%m%d}",
    ),
    _base.PathSegment(
        match_pattern=rf"(?:{_base.SEP}(?P<collection>{_base.NOTSEP}+))?",
        render_template="{collection}",
    ),
    _base.PathSegment(
        match_pattern=rf"(?:{_base.SEP}(?P=collection)_(?P<dataset>{_base.NOTSEP}+))?",
        render_template="{collection}_{dataset}",
    ),
]


@dataclass
class ESRFv1Schema(_base.BaseSchema):
    data_root: Optional[str] = None
    proposal: Optional[str] = None
    beamline: Optional[str] = None
    session_date: Optional[datetime.date] = None

    collection: Optional[str] = None
    dataset: Optional[str] = None

    @staticmethod
    def _path_segments() -> List[_base.PathSegment]:
        return _PATH_SEGMENTS

    def __post_init__(self):
        self.data_root = get_default_data_root(self.data_root)
        if isinstance(self.session_date, str):
            self.session_date = datetime.datetime.strptime(
                self.session_date, "%Y%m%d"
            ).date()
        elif isinstance(self.session_date, datetime.datetime):
            self.session_date = self.session_date.date()
        if self.beamline is not None:
            self.beamline = BEAMLINE_NAME_TO_DIR.get(self.beamline, self.beamline)

    @_base.esrfpath_property
    def raw_data_path(self) -> str:
        return self._replace_and_reconstruct(collection=None, dataset=None)

    @_base.esrfpath_property
    def raw_dataset_path(self) -> str:
        return self._replace_and_reconstruct()

    @_base.esrfpath_property
    def raw_dataset_file(self) -> str:
        path = self._replace_and_reconstruct()
        return os.path.join(path, f"{self.collection}_{self.dataset}.h5")

    @_base.esrfpath_property
    def raw_collection_file(self) -> str:
        path = self._replace_and_reconstruct(dataset=None)
        return os.path.join(path, f"{self.proposal}_{self.collection}.h5")

    @_base.esrfpath_property
    def raw_proposal_file(self) -> str:
        path = self._replace_and_reconstruct(collection=None, dataset=None)
        return os.path.join(path, f"{self.proposal}_{self.beamline}.h5")

    @_base.field_property
    def beamline_normalized(self) -> str:
        if self.beamline is None:
            return None
        return BEAMLINE_DIR_TO_NAME.get(self.beamline, self.beamline)

    @_base.esrfpath_property
    def raw_metadata_path(self) -> str:
        path = self._replace_and_reconstruct(collection=None, dataset=None)
        return os.path.join(path, "__icat__")

    @_base.esrfpath_property
    def raw_metadata_file(self) -> str:
        if self.collection is None or self.dataset is None:
            raise AttributeError(
                "'collection' and 'dataset' must be defined to build raw_metadata_file"
            )
        return os.path.join(
            self.raw_metadata_path, f"{self.collection}_{self.dataset}.xml"
        )
