from pydantic import Field
from ...base import SingularBaseModel
from typing import List, Literal, Optional, Any
from .low_level import Offer, Agreement


# Forward references
# DatasetRef = ForwardRef("Dataset")
# DataServiceRef = ForwardRef("DataService")


class MessageOffer(Offer):
    target: Optional[str]

class ContractRequestMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["ContractRequestMessage"]= Field(alias="@type")
    callbackAddress: str
    consumerPid: str
    offer: MessageOffer
    providerPid: Optional[str] = None


class ContractOfferMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["ContractOfferMessage"] = Field(alias="@type")
    callbackAddress: str
    consumerPid: str
    offer: Any
    providerPid: Optional[str] = None


class ContractAgreementMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["ContractAgreementMessage"] = Field(alias="@type")
    agreement: Agreement
    callbackAddress: str
    consumerPid: str
    providerPid: str


class ContractAgreementVerificationMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["ContractAgreementVerificationMessage"] = Field(alias="@type")
    consumerPid: str
    providerPid: str

class ContractNegotiationEventMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["ContractNegotiationEventMessage"] = Field(alias="@type")
    consumerPid: str
    eventType: str
    providerPid: str


class ContractNegotiationTerminationMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["ContractNegotiationTerminationMessage"] = Field(alias="@type")
    consumerPid: str
    providerPid: str
    code: Optional[str] = None
    reason: Optional[List[Any]] = None

