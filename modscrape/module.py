from typing import FrozenSet
from dataclasses import dataclass


# TODO(lczm): how do we represent modules as part of an IR?
@dataclass
class Module:
    code: str
    title: str
    au: float
    mutually_exclusives: list[str]
    needs_modules: list[str]
    rejects_modules: FrozenSet[str]
    rejects_courses: FrozenSet[str]
    allowed_courses: FrozenSet[str]
    is_bde: bool
