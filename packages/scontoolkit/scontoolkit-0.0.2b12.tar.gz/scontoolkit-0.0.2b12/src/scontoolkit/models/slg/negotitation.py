from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Mapping, Protocol
import math, random
from ..base import SingularBaseModel

class IssueType:
    NUMERIC = "numeric"
    SET = "set"
    BOOL = "bool"
    INTERVAL = "interval"
    DURATION = "duration"
    STRING = "string"

class IssueSpec(SingularBaseModel):
    name: str
    itype: str
    lo: Optional[float] = None
    hi: Optional[float] = None
    preference_order: Optional[List[str]] = None
    desired_bool: Optional[bool] = None

Issues = Dict[str, Any]
