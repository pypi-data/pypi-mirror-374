import logging
import secrets
from abc import abstractmethod, ABC
from datetime import datetime
from typing import Union

from spaceone.core import config, cache
from spaceone.core.manager import BaseManager
from spaceone.identity.error.error_authentication import *

from spaceone.identity.error.error_token import *
from spaceone.identity.lib.key_generator import KeyGenerator

__all__ = ["TokenManager"]
_LOGGER = logging.getLogger(__name__)


class TokenManager(BaseManager, ABC):
    is_authenticated = False
    auth_type = None
    owner_type = "USER"
    user = None
    app = None
    role_type = "USER"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_conf()

    @abstractmethod
    def authenticate(self, domain_id, *args, **kwargs):
        pass

    @classmethod
    def get_token_manager_by_auth_type(cls, auth_type):
        for subclass in cls.__subclasses__():
            if subclass.auth_type == auth_type:
                return subclass()
        raise ERROR_INVALID_AUTHENTICATION_TYPE(auth_type=auth_type)

    def issue_token(
        self,
        private_jwk,
        refresh_private_jwk,
        domain_id,
        workspace_id=None,
        timeout=None,
        permissions=None,
        projects=None,
        user_groups=None,
        app_id=None,
    ):
        if self.is_authenticated is False:
            raise ERROR_NOT_AUTHENTICATED()

        if self.owner_type == "USER":
            audience = self.user.user_id
        elif self.owner_type == "SYSTEM":
            # todo : remove
            audience = app_id
        else:
            audience = self.app.app_id

        key_gen = KeyGenerator(
            private_jwk,
            domain_id,
            self.owner_type,
            audience,
            refresh_prv_jwk=refresh_private_jwk,
        )

        timeout = self.set_timeout(timeout)
        identity_base_url = config.get_global("IDENTITY_BASE_URL")

        access_token = key_gen.generate_token(
            "ACCESS_TOKEN",
            timeout=timeout,
            role_type=self.role_type,
            workspace_id=workspace_id,
            permissions=permissions,
            projects=projects,
            users_group=user_groups,
            identity_base_url=identity_base_url,
        )

        refresh_token = key_gen.generate_token(
            "REFRESH_TOKEN", timeout=self._get_refresh_token_timeout()
        )
        if self.owner_type != "SYSTEM":
            # todo: remove
            self.user.update({"last_accessed_at": datetime.utcnow()})

        return {"access_token": access_token, "refresh_token": refresh_token}

    def issue_temporary_token(
        self,
        user_id: str,
        domain_id: str,
        private_jwk: dict,
        timeout: int,
        injected_params: dict,
    ) -> dict:
        permissions = [
            "identity:UserProfile",
        ]

        key_gen = KeyGenerator(
            private_jwk,
            domain_id,
            self.owner_type,
            user_id,
        )

        # Issue token
        access_token = key_gen.generate_token(
            "ACCESS_TOKEN",
            timeout=timeout,
            role_type="USER",
            permissions=permissions,
            injected_params=injected_params,
        )

        return {"access_token": access_token}

    def create_verify_code(self, user_id, domain_id):
        if cache.is_set():
            verify_code = self._generate_verify_code()
            cache.delete(f"identity:verify-code:{domain_id}:{user_id}")
            cache.set(
                f"identity:verify-code:{domain_id}:{user_id}",
                verify_code,
                expire=self.CONST_VERIFY_CODE_TIMEOUT,
            )
            return verify_code

    def set_timeout(self, timeout: Union[int, None]) -> int:
        if timeout and timeout > 0:
            timeout = min(timeout, self.CONST_MAX_TOKEN_TIMEOUT)
        else:
            timeout = self.CONST_TOKEN_TIMEOUT
        return timeout

    def _get_refresh_token_timeout(self) -> int:
        refresh_timeout = self.CONST_REFRESH_TIMEOUT
        if (
            self.user
            and self.user.role_type == "DOMAIN_ADMIN"
            and self.user.refresh_timeout
        ):
            refresh_timeout = max(self.user.refresh_timeout, refresh_timeout)

        if refresh_timeout > self.CONST_MAX_REFRESH_TIMEOUT:
            refresh_timeout = self.CONST_MAX_REFRESH_TIMEOUT

        return refresh_timeout

    @staticmethod
    def check_verify_code(user_id, domain_id, verify_code):
        if cache.is_set():
            cached_verify_code = cache.get(
                f"identity:verify-code:{domain_id}:{user_id}"
            )
            if cached_verify_code == verify_code:
                return True
        return False

    @staticmethod
    def _generate_verify_code(length: int = 6) -> str:
        first_digit = str(secrets.randbelow(9) + 1)
        remaining_digits = "".join(
            str(secrets.randbelow(10)) for _ in range(length - 1)
        )
        verify_code = first_digit + remaining_digits
        return verify_code

    def _load_conf(self):
        identity_conf = config.get_global("IDENTITY") or {}
        token_conf = identity_conf.get("token", {})
        self.CONST_TOKEN_TIMEOUT = token_conf.get("token_timeout", 1800)
        self.CONST_VERIFY_CODE_TIMEOUT = token_conf.get("verify_code_timeout", 3600)
        self.CONST_REFRESH_TIMEOUT = token_conf.get("refresh_timeout", 10800)
        self.CONST_MAX_REFRESH_TIMEOUT = token_conf.get(
            "admin_refresh_max_timeout", 2592000
        )
        self.CONST_MAX_TOKEN_TIMEOUT = token_conf.get("token_max_timeout", 604800)
