from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import user_pb2, user_pb2_grpc
from spaceone.identity.service.user_service import UserService


class User(BaseAPI, user_pb2_grpc.UserServicer):
    pb2 = user_pb2
    pb2_grpc = user_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        response: dict = user_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        response: dict = user_svc.update(params)
        return self.dict_to_message(response)

    def verify_email(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        user_svc.verify_email(params)
        return self.empty()

    def disable_mfa(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        response: dict = user_svc.disable_mfa(params)
        return self.dict_to_message(response)

    def set_required_actions(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        response: dict = user_svc.set_required_actions(params)
        return self.dict_to_message(response)

    def set_refresh_timeout(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        response: dict = user_svc.set_refresh_timeout(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        user_svc.delete(params)
        return self.empty()

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        response: dict = user_svc.enable(params)
        return self.dict_to_message(response)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        response: dict = user_svc.disable(params)
        return self.dict_to_message(response)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        response: dict = user_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        response: dict = user_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_svc = UserService(metadata)
        response: dict = user_svc.stat(params)
        return self.dict_to_message(response)
