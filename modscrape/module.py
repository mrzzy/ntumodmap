from dataclasses import dataclass
from typing import Optional


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
    # There is a special case of course str: "Admyr" - admission year
    course: str
    # these are noted by "(Direct Entry)" or "(Non Direct Entry)"
    # when we refer to the course, this tells us
    # if a direct_entry or non direct entry to the course matters
    is_direct_entry: Optional[bool]
    # these states from what year
    # e.g. "EEEC(2018-onwards)"
    from_year: Optional[int]
    # Sometimes we need to state until which year
    # e.g. "(Admyr 2004-2013)"
    # 2004-onwards is treated as 2004-9999
    to_year: Optional[int]
    # Possible to have alternate representations
    # e.g. "ENG(ENE)"
    alt_course: Optional[str]


# TODO(lczm): how do we represent modules as part of an IR?
@dataclass
class Module:
    code: ModuleCode
    title: str
    au: float
    mutually_exclusives: list[ModuleCode]
    needs_year: Optional[int]
    needs_modules: list[list[ModuleCode]]
    rejects_modules: list[ModuleCode]
    rejects_courses: list[Course]
    rejects_courses_with: list[Course]
    allowed_courses: list[Course]
    is_bde: bool
    is_pass_fail: bool
