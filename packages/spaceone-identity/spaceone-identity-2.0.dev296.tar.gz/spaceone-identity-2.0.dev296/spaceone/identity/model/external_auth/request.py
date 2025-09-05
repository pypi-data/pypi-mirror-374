from typing import Union, Literal
from pydantic import BaseModel, Field

__all__ = [
    "ExternalAuthSetRequest",
    "ExternalAuthUnsetRequest",
    "ExternalAuthGetRequest",
]

UpgradeMode = Literal["AUTO", "MANUAL"]


class Plugin(BaseModel):
    plugin_id: str
    version: Union[str, None] = None
    upgrade_mode: Union[str, None] = None
    options: Union[dict, None] = None
    secret_data: Union[dict, None] = None
    schema_id: Union[str, None] = Field(None, alias="schema")


class ExternalAuthSetRequest(BaseModel):
    domain_id: str
    plugin_info: Plugin


class ExternalAuthUnsetRequest(BaseModel):
    domain_id: str


class ExternalAuthGetRequest(BaseModel):
    domain_id: str
