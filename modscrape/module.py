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
    # only one of direct_entry and non_direct_entry can be true
    # but both can be false if not specified
    # these are noted by "(Direct Entry)" or "(Non Direct Entry)"
    is_direct_entry: bool
    is_non_direct_entry: bool
    # these states from what year
    # e.g. "EEEC(2018-onwards)"
    from_year: int


# TODO(lczm): how do we represent modules as part of an IR?
@dataclass
class Module:
    code: ModuleCode
    title: str
    au: float
    mutually_exclusives: list[str]
    needs_year: Optional[int]
    needs_modules: list[list[str]]
    rejects_modules: FrozenSet[str]
    rejects_courses: FrozenSet[str]
    allowed_courses: FrozenSet[str]
    is_bde: bool
    is_pass_fail: bool
