from __future__ import annotations
from ...models.slg.negotitation import IssueSpec, Issues
from typing import Optional, List, Callable
import random
from abc import ABC, abstractmethod
from typing import     final
from ..base import _MethodEnforcer
from typing import Any, Dict, Type, TypeVar


T = TypeVar("T", bound="INegotiator")

class INegotiator(_MethodEnforcer, ABC):

    @abstractmethod
    def on_receive_offer(self, their_policy: Any, t: float) -> Dict: ...

    @abstractmethod
    def first_offer(self, t: float = 0.0) -> Dict: ...

    @abstractmethod
    def _state_dict(self) -> Dict[str, Any]: ...

    @classmethod
    @abstractmethod
    def _from_state_dict(cls: Type[T], state: Dict[str, Any]) -> T: ...

    @final
    def to_dict(self) -> Dict[str, Any]:
        """Stable, non-overridable envelope for serialization."""
        return {
            "type": self.__class__.__name__,
            "state": self._state_dict(),
        }

    @classmethod
    @final
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Stable, non-overridable factory.
        Validates version, then delegates to subclass state importer.
        """
        if not isinstance(data, dict):
            raise TypeError("from_dict expects a dict")

        state = data.get("state", {})
        if not isinstance(state, dict):
            raise TypeError("from_dict expects a dict in 'state'")
        return cls._from_state_dict(state)

class IDomainAdapter(ABC):
    @abstractmethod
    def extract_issues(self, policy: Any) -> Issues: ...

    @abstractmethod
    def apply_issues(self, base_policy: Any, issues: Issues) -> Any: ...

    @abstractmethod
    def issue_specs(self, policy: Any) -> List[IssueSpec]: ...


class IUtilityModel(ABC):
    @abstractmethod
    def per_issue_utility(self, name: str, value: Any) -> float: ...

    @abstractmethod
    def utility(self, issues: Issues) -> float: ...


class IOpponentModel(ABC):
    @abstractmethod
    def update(self, opp_offer_issues: Issues) -> None: ...

    @abstractmethod
    def u_hat(self, issues: Issues) -> float: ...

    @abstractmethod
    def last_offer(self) -> Optional[Issues]: return None

class IAcceptancePolicy(ABC):
    @abstractmethod
    def accept(self, my_U: float, t: float) -> bool: ...


class IBiddingStrategy(ABC):
    @abstractmethod
    def propose(
            self,
            my_issues: Issues,
            opp_last_issues: Optional[Issues],
            t: float,
            U_self: IUtilityModel,
            U_opp_hat: Callable[[Issues], float],
            issue_specs: Dict[str, IssueSpec],
            rng: random.Random = random.Random()) -> Issues: ...

