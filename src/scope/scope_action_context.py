from dataclasses import dataclass
from typing import Optional
from .scope import Scope

@dataclass
class ActionContext:
    pass

@dataclass
class ScopeActionContext(ActionContext):
    scope: Optional[Scope] = None
