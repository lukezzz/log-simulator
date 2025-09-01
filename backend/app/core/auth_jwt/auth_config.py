from datetime import timedelta
from typing import Literal, Optional, Union, Sequence, List, Callable
from pydantic import (
    BaseModel,
    StrictBool,
    StrictInt,
    StrictStr,
    field_validator,
    ConfigDict,
    ValidationError,
)


class LoadConfig(BaseModel):
    authjwt_token_location: set[Literal["headers", "cookies"]] = {"headers"}
    authjwt_secret_key: Optional[StrictStr] = None
    authjwt_public_key: Optional[StrictStr] = None
    authjwt_private_key: Optional[StrictStr] = None
    authjwt_algorithm: Optional[StrictStr] = "HS256"
    authjwt_decode_algorithms: Optional[List[StrictStr]] = None
    authjwt_decode_leeway: Optional[Union[StrictInt, timedelta]] = 0
    authjwt_encode_issuer: Optional[StrictStr] = None
    authjwt_decode_issuer: Optional[StrictStr] = None
    authjwt_decode_audience: Optional[Union[StrictStr, Sequence[StrictStr]]] = None
    authjwt_denylist_enabled: Optional[StrictBool] = False
    authjwt_denylist_token_checks: set[Literal["access", "refresh"]] = {
        "access",
        "refresh",
    }
    authjwt_access_token_expires: Optional[Union[StrictBool, StrictInt, timedelta]] = (
        timedelta(minutes=15)
    )
    authjwt_refresh_token_expires: Optional[Union[StrictBool, StrictInt, timedelta]] = (
        timedelta(days=30)
    )
    # option for create cookies
    authjwt_access_cookie_key: Optional[StrictStr] = "access_token_cookie"
    authjwt_refresh_cookie_key: Optional[StrictStr] = "refresh_token_cookie"
    authjwt_access_cookie_path: Optional[StrictStr] = "/"
    authjwt_refresh_cookie_path: Optional[StrictStr] = "/"
    # option for double submit csrf protection
    authjwt_cookie_csrf_protect: Optional[StrictBool] = True
    authjwt_access_csrf_cookie_key: Optional[StrictStr] = "csrf_access_token"
    authjwt_refresh_csrf_cookie_key: Optional[StrictStr] = "csrf_refresh_token"
    authjwt_access_csrf_cookie_path: Optional[StrictStr] = "/"
    authjwt_refresh_csrf_cookie_path: Optional[StrictStr] = "/"
    authjwt_access_csrf_header_name: Optional[StrictStr] = "X-CSRF-Token"
    authjwt_refresh_csrf_header_name: Optional[StrictStr] = "X-CSRF-Token"
    authjwt_csrf_methods: set = {"POST", "PUT", "PATCH", "DELETE"}

    @field_validator("authjwt_access_token_expires")
    def validate_access_token_expires(cls, v):
        if v is True:
            raise ValueError(
                "The 'authauthjwt_access_token_expires' only accept value False (bool)"
            )
        return v

    @field_validator("authjwt_refresh_token_expires")
    def validate_refresh_token_expires(cls, v):
        if v is True:
            raise ValueError(
                "The 'authjwt_refresh_token_expires' only accept value False (bool)"
            )
        return v

    @field_validator("authjwt_csrf_methods")
    def validate_csrf_methods(cls, v):
        for item in v:
            try:
                item.upper()
                if item.upper() not in {
                    "GET",
                    "HEAD",
                    "POST",
                    "PUT",
                    "DELETE",
                    "PATCH",
                }:
                    raise ValueError(
                        "The 'authjwt_csrf_methods' must be between http request methods"
                    )
            except AttributeError:
                raise ValueError(
                    "The 'authjwt_csrf_methods' must be between http request methods"
                )
        return [item.upper() for item in v]

    model_config = ConfigDict(
        arbitrary_types_allowed=True, str_min_length=1, str_strip_whitespace=True
    )


class AuthConfig:
    _token = None
    _token_location = {"headers"}

    _secret_key = None
    _public_key = None
    _private_key = None
    _algorithm = "HS256"
    _decode_algorithms = None
    _decode_leeway = 0
    _encode_issuer = None
    _decode_issuer = None
    _decode_audience = None
    _denylist_enabled = False
    _denylist_token_checks = {"access", "refresh"}
    _header_name = "Authorization"
    _header_type = "Bearer"
    _token_in_denylist_callback = None
    _access_token_expires = timedelta(minutes=15)
    _refresh_token_expires = timedelta(days=30)

    # option for create cookies
    _access_cookie_key = "access_token_cookie"
    _refresh_cookie_key = "refresh_token_cookie"
    _access_cookie_path = "/"
    _refresh_cookie_path = "/"
    _cookie_max_age = None
    _cookie_domain = None
    _cookie_secure = False
    _cookie_samesite = None

    # option for double submit csrf protection
    _cookie_csrf_protect = True
    _access_csrf_cookie_key = "csrf_access_token"
    _refresh_csrf_cookie_key = "csrf_refresh_token"
    _access_csrf_cookie_path = "/"
    _refresh_csrf_cookie_path = "/"
    _access_csrf_header_name = "X-CSRF-Token"
    _refresh_csrf_header_name = "X-CSRF-Token"
    _csrf_methods = {"POST", "PUT", "PATCH", "DELETE"}

    _oauth2_scheme = None

    @property
    def authjwt_in_cookies(self) -> bool:
        return "cookies" in self._token_location

    @property
    def authjwt_in_headers(self) -> bool:
        return "headers" in self._token_location

    @classmethod
    def load_config(cls, settings: Callable[..., List[tuple]]):
        try:
            config = LoadConfig(**{key.lower(): value for key, value in settings()})
            cls._token_location = config.authjwt_token_location
            cls._secret_key = config.authjwt_secret_key
            cls._public_key = config.authjwt_public_key
            cls._private_key = config.authjwt_private_key
            cls._algorithm = config.authjwt_algorithm
            cls._decode_algorithms = config.authjwt_decode_algorithms
            cls._decode_leeway = config.authjwt_decode_leeway
            cls._encode_issuer = config.authjwt_encode_issuer
            cls._decode_issuer = config.authjwt_decode_issuer
            cls._decode_audience = config.authjwt_decode_audience
            cls._denylist_enabled = config.authjwt_denylist_enabled
            cls._denylist_token_checks = config.authjwt_denylist_token_checks
            cls._access_token_expires = config.authjwt_access_token_expires
            cls._refresh_token_expires = config.authjwt_refresh_token_expires
            # option for create cookies
            cls._access_cookie_key = config.authjwt_access_cookie_key
            cls._refresh_cookie_key = config.authjwt_refresh_cookie_key
            cls._access_cookie_path = config.authjwt_access_cookie_path
            cls._refresh_cookie_path = config.authjwt_refresh_cookie_path
            # option for double submit csrf protection
            cls._cookie_csrf_protect = config.authjwt_cookie_csrf_protect
            cls._access_csrf_cookie_key = config.authjwt_access_csrf_cookie_key
            cls._refresh_csrf_cookie_key = config.authjwt_refresh_csrf_cookie_key
            cls._access_csrf_cookie_path = config.authjwt_access_csrf_cookie_path
            cls._refresh_csrf_cookie_path = config.authjwt_refresh_csrf_cookie_path
            cls._access_csrf_header_name = config.authjwt_access_csrf_header_name
            cls._refresh_csrf_header_name = config.authjwt_refresh_csrf_header_name
            cls._csrf_methods = config.authjwt_csrf_methods
        except ValidationError:
            raise
        except Exception:
            raise TypeError("Config must be pydantic 'BaseSettings' or list of tuple")

    @classmethod
    def token_in_denylist_loader(cls, callback: Callable[..., bool]):
        """
        This decorator sets the callback function that will be called when
        a protected endpoint is accessed and will check if the JWT has been
        been revoked. By default, this callback is not used.

        *HINT*: The callback must be a function that takes decrypted_token argument,
        args for object jwt and this is not used, decrypted_token is decode
        JWT (python dictionary) and returns *`True`* if the token has been deny,
        or *`False`* otherwise.
        """
        cls._token_in_denylist_callback = callback
