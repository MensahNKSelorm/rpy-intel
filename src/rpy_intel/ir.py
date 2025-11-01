from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class Assign:
    target: str
    expr: Any


@dataclass
class Call:
    func: str
    args: List[Any]
    kwargs: dict


@dataclass
class Import:
    module: str
    alias: Optional[str] = None
