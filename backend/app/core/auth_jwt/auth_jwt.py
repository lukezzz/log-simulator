from datetime import datetime, timedelta
from typing import Annotated, Optional, Dict, Union, Sequence
from fastapi import Depends, HTTPException

from core.security import gen_uuid

# from fastapi_jwt_auth.auth_config import AuthConfig
# from ..config import get_settings
from .auth_config import AuthConfig

import jwt

from jwt.exceptions import ExpiredSignatureError, PyJWTError

oauth2_scheme = None


class AuthJWT(AuthConfig):
    @classmethod
    def _get_secret_key(cls, algorithm: Union[str, list], process: str) -> str:
        """
        Get key with a different algorithm

        :param algorithm: algorithm for decode and encode token
        :param process: for indicating get key for encode or decode token

        :return: plain text or RSA depends on algorithm
        """
        if isinstance(algorithm, list):
            algorithm = algorithm[0]
        if not cls._secret_key:
            raise RuntimeError(
                "jwt_secret_key must be set when using symmetric algorithm {}".format(
                    algorithm
                )
            )

        return cls._secret_key

        # if process == "encode":
        #     if not cls._private_key:
        #         raise RuntimeError(
        #             "authjwt_private_key must be set when using asymmetric algorithm {}".format(
        #                 algorithm
        #             )
        #         )

        #     return cls._private_key

        # if process == "decode":
        #     if not cls._public_key:
        #         raise RuntimeError(
        #             "authjwt_public_key must be set when using asymmetric algorithm {}".format(
        #                 algorithm
        #             )
        #         )

        #     return cls._public_key

    @classmethod
    def _create_token(
        cls,
        subject: Union[str, int],
        type_token: str,
        exp_time: Optional[int],
        algorithm: Optional[str] = None,
        headers: Optional[Dict] = None,
        issuer: Optional[str] = None,
        audience: Optional[Union[str, Sequence[str]]] = None,
        user_claims: Optional[Dict] = {},
    ) -> str:
        """
        Create token for access_token and refresh_token (utf-8)

        :param subject: Identifier for who this token is for example id or username from database.
        :param type_token: indicate token is access_token or refresh_token
        :param exp_time: Set the duration of the JWT
        :param fresh: Optional when token is access_token this param required
        :param algorithm: algorithm allowed to encode the token
        :param headers: valid dict for specifying additional headers in JWT header section
        :param issuer: expected issuer in the JWT
        :param audience: expected audience in the JWT
        :param user_claims: Custom claims to include in this token. This data must be dictionary

        :return: Encoded token
        """
        # Validation type data
        if not isinstance(subject, (str, int)):
            raise TypeError("subject must be a string or integer")
        if audience and not isinstance(audience, (str, list, tuple, set, frozenset)):
            raise TypeError("audience must be a string or sequence")
        if algorithm and not isinstance(algorithm, str):
            raise TypeError("algorithm must be a string")
        if user_claims and not isinstance(user_claims, dict):
            raise TypeError("user_claims must be a dictionary")

        # Data section
        reserved_claims = {
            "sub": subject,
            "iat": datetime.utcnow(),
            "nbf": datetime.utcnow(),
            "jti": gen_uuid(),
        }

        custom_claims = {"type": type_token}
        # if cookie in token location and csrf protection enabled
        if exp_time:
            reserved_claims["exp"] = exp_time
        if issuer:
            reserved_claims["iss"] = issuer
        if audience:
            reserved_claims["aud"] = audience

        algorithm = algorithm or cls._algorithm

        try:
            secret_key = cls._get_secret_key(algorithm, "encode")
        except Exception:
            raise

        return jwt.encode(
            {**reserved_claims, **custom_claims, **user_claims},
            secret_key,
            algorithm=algorithm,
            headers=headers,
        )

    @classmethod
    def _has_token_in_denylist_callback(cls) -> bool:
        """
        Return True if token denylist callback set
        """
        return cls._token_in_denylist_callback is not None

    @classmethod
    async def _check_token_is_revoked(
        cls, raw_token: Dict[str, Union[str, int, bool]]
    ) -> None:
        """
        Ensure that JWT_DENYLIST_ENABLED is true and callback regulated, and then
        call function denylist callback with passing decode JWT, if true
        raise exception Token has been revoked
        """
        if not cls._denylist_enabled:
            return

        if not cls._has_token_in_denylist_callback():
            raise RuntimeError(
                "A token_in_denylist_callback must be provided via "
                "the '@AuthJWT.token_in_denylist_loader' if "
                "jwt_denylist_enabled is 'True'"
            )

        if await cls._token_in_denylist_callback(raw_token):
            raise RevokedTokenError(status_code=401, detail="Token has been revoked")

    @classmethod
    def _get_expired_time(
        cls,
        type_token: str,
        expires_time: Optional[Union[timedelta, int, bool]] = None,
    ) -> Union[None, int]:
        """
        Dynamic token expired, if expires_time is False exp claim not created

        :param type_token: indicate token is access_token or refresh_token
        :param expires_time: duration expired jwt

        :return: duration exp claim jwt
        """
        if expires_time and not isinstance(expires_time, (timedelta, int, bool)):
            raise TypeError("expires_time must be between timedelta, int, bool")

        if expires_time is not False:
            if type_token == "access":
                expires_time = expires_time or cls._access_token_expires
            if type_token == "refresh":
                expires_time = expires_time or cls._refresh_token_expires
            if isinstance(expires_time, bool):
                if type_token == "access":
                    expires_time = cls._access_token_expires
                if type_token == "refresh":
                    expires_time = cls._refresh_token_expires
            if isinstance(expires_time, int):
                expires_time = timedelta(seconds=expires_time)
            return datetime.utcnow() + expires_time
        else:
            return None

    @classmethod
    def create_access_token(
        cls,
        subject: Union[str, int],
        algorithm: Optional[str] = None,
        headers: Optional[Dict] = None,
        expires_delta: Optional[Union[timedelta, int, bool]] = None,
        audience: Optional[Union[str, Sequence[str]]] = None,
        user_claims: Optional[Dict] = {},
    ) -> str:
        """
        Create a access token with 15 minutes for expired time (default),
        info for param and return check to function create token

        :return: hash token
        """
        return cls._create_token(
            subject=subject,
            type_token="access",
            exp_time=cls._get_expired_time("access", expires_delta),
            algorithm=algorithm,
            headers=headers,
            audience=audience,
            user_claims=user_claims,
            issuer=cls._encode_issuer,
        )

    @classmethod
    def create_refresh_token(
        cls,
        subject: Union[str, int],
        algorithm: Optional[str] = None,
        headers: Optional[Dict] = None,
        expires_delta: Optional[Union[timedelta, int, bool]] = None,
        audience: Optional[Union[str, Sequence[str]]] = None,
        user_claims: Optional[Dict] = {},
    ) -> str:
        """
        Create a refresh token with 30 days for expired time (default),
        info for param and return check to function create token

        :return: hash token
        """
        return cls._create_token(
            subject=subject,
            type_token="refresh",
            exp_time=cls._get_expired_time("refresh", expires_delta),
            algorithm=algorithm,
            headers=headers,
            audience=audience,
            user_claims=user_claims,
        )

    @classmethod
    def _verify_jwt_optional_in_request(cls, token: str) -> None:
        """
        Optionally check if this request has a valid access token

        :param token: The encoded JWT
        """
        if token:
            cls._verifying_token(token)

        if token and cls.get_raw_jwt(token)["type"] != "access":
            raise AccessTokenRequired(
                status_code=422, detail="Only access tokens are allowed"
            )

    @classmethod
    async def _verify_jwt_in_request(
        cls,
        token: str,
        type_token: str,
        token_from: str,
        fresh: Optional[bool] = False,
    ) -> None:
        """
        Ensure that the requester has a valid token. this also check the freshness of the access token

        :param token: The encoded JWT
        :param type_token: indicate token is access or refresh token
        :param token_from: indicate token from headers cookies, websocket
        :param fresh: check freshness token if True
        """
        if type_token not in ["access", "refresh"]:
            raise ValueError("type_token must be between 'access' or 'refresh'")
        if token_from not in ["headers", "cookies", "websocket"]:
            raise ValueError(
                "token_from must be between 'headers', 'cookies', 'websocket'"
            )

        if not token:
            if token_from == "headers":
                raise MissingTokenError(
                    status_code=401,
                    detail="Missing {} Header".format(cls._header_name),
                )

        # verify jwt
        issuer = cls._decode_issuer if type_token == "access" else None
        await cls._verifying_token(token, issuer)

        if cls.get_raw_jwt(token)["type"] != type_token:
            msg = "Only {} tokens are allowed".format(type_token)
            if type_token == "access":
                raise AccessTokenRequired(status_code=422, detail=msg)
            if type_token == "refresh":
                raise RefreshTokenRequired(status_code=422, detail=msg)

        if fresh and not cls.get_raw_jwt(token)["fresh"]:
            raise FreshTokenRequired(status_code=401, detail="Fresh token required")

    @classmethod
    async def _verifying_token(
        cls, encoded_token: str, issuer: Optional[str] = None
    ) -> None:
        """
        Verified token and check if token is revoked

        :param encoded_token: token hash
        :param issuer: expected issuer in the JWT
        """
        raw_token = cls._verified_token(encoded_token, issuer)
        if raw_token["type"] in cls._denylist_token_checks:
            await cls._check_token_is_revoked(raw_token)

    @classmethod
    def _verified_token(
        cls,
        encoded_token: str,
        issuer: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> Dict[str, Union[str, int, bool]]:
        """
        Verified token and catch all error from jwt package and return decode token

        :param encoded_token: token hash
        :param issuer: expected issuer in the JWT

        :return: raw data from the hash token in the form of a dictionary
        """
        algorithms = cls._decode_algorithms or [cls._algorithm]
        try:
            # 验证 JWT
            return jwt.decode(
                encoded_token,
                cls._get_secret_key(algorithms, "decode"),
                algorithms,
                options=options,
                issuer=issuer,
            )
            # 验证成功
        except ExpiredSignatureError as e:
            # token expired
            raise InvalidHeaderError(status_code=401, detail="The access token expired")
        except PyJWTError as e:
            # 验证失败
            raise InvalidHeaderError(status_code=401, detail="Invalid token header")
        # algorithms = cls._decode_algorithms or [cls._algorithm]
        # try:
        #     unverified_headers = cls.get_unverified_jwt_headers(encoded_token)
        # except Exception as err:
        #     raise InvalidHeaderError(status_code=422, detail=str(err))

        # try:
        #     secret_key = cls._get_secret_key(unverified_headers["alg"], "decode")
        # except Exception:
        #     raise

    @classmethod
    async def jwt_required(cls, token: str):
        """
        Only access token can access this function

        :param auth_from: for identity get token from HTTP or WebSocket
        :param token: the encoded JWT, it's required if the protected endpoint use WebSocket to
                      authorization and get token from Query Url or Path
        :param websocket: an instance of WebSocket, it's required if protected endpoint use a cookie to authorization
        :param csrf_token: the CSRF double submit token. since WebSocket cannot add specifying additional headers
                           its must be passing csrf_token manually and can achieve by Query Url or Path
        """
        # algorithms = cls._decode_algorithms or [cls._algorithm]

        # try:
        #     jwt.decode(
        #         token,
        #         cls._get_secret_key(cls._algorithm, "decode"),
        #         algorithms=algorithms,
        #     )
        # except JWTError:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Could not validate credentials",
        #         headers={"WWW-Authenticate": "bearer"},
        #     )

        await cls._verify_jwt_in_request(token, "access", "headers")

        # if len(c l s._token_location) == 2:
        #     if cls._token and cls.jwt_in_headers:
        #         cls._verify_jwt_in_request(cls._token, "access", "headers")
        # else:
        #     if cls.jwt_in_headers:
        #         cls._verify_jwt_in_request(cls._token, "access", "headers")
        #     if cls.jwt_in_cookies:
        #         cls._verify_and_get_jwt_in_cookies("access", cls._request)

    @classmethod
    def jwt_optional(
        cls,
        # auth_from: str = "request",
        token: Optional[str] = None,
    ) -> None:
        """
        If an access token in present in the request you can get data from get_raw_jwt() or get_jwt_subject(),
        If no access token is present in the request, this endpoint will still be called, but
        get_raw_jwt() or get_jwt_subject() will return None

        :param auth_from: for identity get token from HTTP or WebSocket
        :param token: the encoded JWT, it's required if the protected endpoint use WebSocket to
                      authorization and get token from Query Url or Path
        :param websocket: an instance of WebSocket, it's required if protected endpoint use a cookie to authorization
        :param csrf_token: the CSRF double submit token. since WebSocket cannot add specifying additional headers
                           its must be passing csrf_token manually and can achieve by Query Url or Path
        """

        cls._verify_jwt_optional_in_request(token)

    @classmethod
    async def jwt_refresh_token_required(
        cls,
        token: Annotated[str, Depends(oauth2_scheme)],
        auth_from: str = "request",
    ) -> None:
        """
        This function will ensure that the requester has a valid refresh token

        :param auth_from: for identity get token from HTTP or WebSocket
        :param token: the encoded JWT, it's required if the protected endpoint use WebSocket to
                      authorization and get token from Query Url or Path
        :param websocket: an instance of WebSocket, it's required if protected endpoint use a cookie to authorization
        :param csrf_token: the CSRF double submit token. since WebSocket cannot add specifying additional headers
                           its must be passing csrf_token manually and can achieve by Query Url or Path
        """
        if auth_from == "request":
            await cls._verify_jwt_in_request(token, "refresh", "headers")

    def fresh_jwt_required(
        cls,
        auth_from: str = "request",
        token: Optional[str] = None,
    ) -> None:
        """
        This function will ensure that the requester has a valid access token and fresh token

        :param auth_from: for identity get token from HTTP or WebSocket
        :param token: the encoded JWT, it's required if the protected endpoint use WebSocket to
                      authorization and get token from Query Url or Path
        :param websocket: an instance of WebSocket, it's required if protected endpoint use a cookie to authorization
        :param csrf_token: the CSRF double submit token. since WebSocket cannot add specifying additional headers
                           its must be passing csrf_token manually and can achieve by Query Url or Path
        """
        if auth_from == "request":
            if len(cls._token_location) == 2:
                if cls._token and cls.jwt_in_headers:
                    cls._verify_jwt_in_request(cls._token, "access", "headers", True)
            else:
                if cls.jwt_in_headers:
                    cls._verify_jwt_in_request(cls._token, "access", "headers", True)

    @classmethod
    def get_raw_jwt(
        cls, encoded_token: Annotated[str, Depends(AuthConfig._oauth2_scheme)]
    ) -> Optional[Dict[str, Union[str, int, bool]]]:
        """
        this will return the python dictionary which has all of the claims of the JWT that is accessing the endpoint.
        If no JWT is currently present, return None instead

        :param encoded_token: The encoded JWT from parameter
        :return: claims of JWT
        """
        token = encoded_token

        if token:
            return cls._verified_token(token, options={"verify_exp": False})
        return None

    def get_jti(cls, encoded_token: str) -> str:
        """
        Returns the JTI (unique identifier) of an encoded JWT

        :param encoded_token: The encoded JWT from parameter
        :return: string of JTI
        """
        return cls.get_raw_jwt(encoded_token)["jti"]

    @classmethod
    def get_jwt_subject(
        cls,
        token: str,
    ):
        """
        this will return the subject of the JWT that is accessing this endpoint.
        If no JWT is present, `None` is returned instead.

        :return: sub of JWT
        """

        return cls.get_raw_jwt(token)["sub"]

    @classmethod
    def get_unverified_jwt_headers(cls, encoded_token: Optional[str] = None) -> dict:
        """
        Returns the Headers of an encoded JWT without verifying the actual signature of JWT

        :param encoded_token: The encoded JWT to get the Header from
        :return: JWT header parameters as a dictionary
        """
        encoded_token = encoded_token or cls._token

        return jwt.get_unverified_header(encoded_token)


class InvalidHeaderError(HTTPException):
    """
    An error getting jwt in header or jwt header information from a request
    """


class JWTDecodeError(HTTPException):
    """
    An error decoding a JWT
    """


class CSRFError(HTTPException):
    """
    An error with CSRF protection
    """


class MissingTokenError(HTTPException):
    """
    Error raised when token not found
    """


class RevokedTokenError(HTTPException):
    """
    Error raised when a revoked token attempt to access a protected endpoint
    """


class AccessTokenRequired(HTTPException):
    """
    Error raised when a valid, non-access JWT attempt to access an endpoint
    protected by jwt_required, jwt_optional, fresh_jwt_required
    """


class RefreshTokenRequired(HTTPException):
    """
    Error raised when a valid, non-refresh JWT attempt to access an endpoint
    protected by jwt_refresh_token_required
    """


class FreshTokenRequired(HTTPException):
    """
    Error raised when a valid, non-fresh JWT attempt to access an endpoint
    protected by fresh_jwt_required
    """
