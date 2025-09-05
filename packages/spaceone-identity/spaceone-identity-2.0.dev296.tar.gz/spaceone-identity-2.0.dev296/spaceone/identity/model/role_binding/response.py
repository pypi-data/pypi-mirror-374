from datetime import datetime
from typing import List, Union

from pydantic import BaseModel
from spaceone.core import utils

from spaceone.identity.model.role_binding.request import ResourceGroup

__all__ = ["RoleBindingResponse", "RoleBindingsResponse"]


class RoleBindingResponse(BaseModel):
    role_binding_id: Union[str, None] = None
    user_id: Union[str, None] = None
    role_id: Union[str, None] = None
    role_type: Union[str, None] = None
    resource_group: Union[ResourceGroup, None] = None
    workspace_id: Union[str, None] = None
    workspace_group_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        return data


class RoleBindingsResponse(BaseModel):
    results: List[RoleBindingResponse]
    total_count: int
