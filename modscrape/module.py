from typing import FrozenSet, Optional
from dataclasses import dataclass


@dataclass
class ModuleCode:
    code: str
    is_corequisite: bool = False
    # Some module pre-requisite have strings that are standardized
    # and are not ideal to parse / keep
    # e.g. CC0001 (Not Applicable to IEM)
    # but I don't think we should throw the data away, even if
    # we dont form a data model for them so anything that is not
    # matched will be kept in misc to be shown/displayed
    misc: str = ""


@dataclass
class Course:
    course: str
    # these are noted by "(Direct Entry)" or "(Non Direct Entry)"
    # when we refer to the course, this tells us
    # if a direct_entry or non direct entry to the course matters
    is_direct_entry: Optional[bool]
    # these states from what year
    # e.g. "EEEC(2018-onwards)"
    from_year: int


# TODO(lczm): how do we represent modules as part of an IR?
@dataclass
class Module:
    code: ModuleCode
    title: str
    au: float
    mutually_exclusives: list[ModuleCode]
    needs_year: Optional[int]
    needs_modules: list[list[ModuleCode]]
    rejects_modules: FrozenSet[ModuleCode]
    rejects_courses: FrozenSet[Course]
    allowed_courses: FrozenSet[Course]
    is_bde: bool
    is_pass_fail: bool
