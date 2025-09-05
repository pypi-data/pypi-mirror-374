from spaceone.api.identity.v2 import role_pb2, role_pb2_grpc
from spaceone.core.pygrpc import BaseAPI

from spaceone.identity.service.role_service import RoleService


class Role(BaseAPI, role_pb2_grpc.RoleServicer):
    pb2 = role_pb2
    pb2_grpc = role_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        endpoint_svc = RoleService(metadata)
        response: dict = endpoint_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        endpoint_svc = RoleService(metadata)
        response: dict = endpoint_svc.update(params)
        return self.dict_to_message(response)

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)
        endpoint_svc = RoleService(metadata)
        response: dict = endpoint_svc.enable(params)
        return self.dict_to_message(response)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)
        endpoint_svc = RoleService(metadata)
        response: dict = endpoint_svc.disable(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        endpoint_svc = RoleService(metadata)
        endpoint_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        endpoint_svc = RoleService(metadata)
        response: dict = endpoint_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        endpoint_svc = RoleService(metadata)
        response: dict = endpoint_svc.list(params)
        return self.dict_to_message(response)

    def list_basic_role(self, request, context):
        params, metadata = self.parse_request(request, context)
        endpoint_svc = RoleService(metadata)
        response: dict = endpoint_svc.list_basic_role(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        endpoint_svc = RoleService(metadata)
        response: dict = endpoint_svc.stat(params)
        return self.dict_to_message(response)
