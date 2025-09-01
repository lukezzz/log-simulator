from typing import Any, Dict, Optional, List
from typing_extensions import Annotated
from email_validator import  EmailNotValidError
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    computed_field,
)
from enum import Enum
import re
from datetime import datetime
from core.auth_jwt.auth_jwt import AuthJWT


def check_password_complex(password: str) -> Any:
    # password should be contain at least 8 characters, 1 uppercase, 1 lowercase, 1 number and 1 special character
    if not re.match(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
        password,
    ):
        raise ValueError(
            "Password should be contain at least 8 characters, 1 uppercase, 1 lowercase, 1 number and 1 special character"
        )
    return password


def check_mail_format(email: str) -> Any:
    try:
        # valid = validate_email(email)
        # Update with the normalized form.
        return email
    except EmailNotValidError as e:
        raise ValueError(e)


class RoleNames(str, Enum):
    admin = "admin"
    guest = "guest"
    api = "api"


class Permissions(str, Enum):
    me = "me"
    admin = "admin"
    api = "api"


# script to generate PermissionRules
class PermissionRules(list[str], Enum):
    admin = [
        Permissions.me,
        Permissions.admin,
    ]
   
    guest = [Permissions.me]
    # api account
    api = [Permissions.me, Permissions.api]


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    permissions: List[PermissionOut]


class Role(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str


class Login(BaseModel):
    username: str
    password: str
    remember: bool


class AccountBase(BaseModel):
    username: str
    display_name: Optional[str] = None
    email: Annotated[Optional[str], AfterValidator(check_mail_format)]
    phone: Optional[str] = None
    desc: Optional[str] = None
    is_blocked: Optional[bool] = None


class AccountCreate(AccountBase):
    password: str
    role: RoleNames

    @field_validator("username")
    @classmethod
    def validate_username(cls: Any, username: str, **kwargs: Any) -> str:
        if len(username) <= 3 or username == "admin":
            raise ValueError("Username is invalid")
        return username

    @field_validator("password")
    @classmethod
    def validate_password(cls: Any, password: str, **kwargs: Any) -> str:
        return check_password_complex(password)

    # @field_validator("role")
    # @classmethod
    # def validate_role(cls: Any, role: str, **kwargs: Any) -> str:
    #     # check role name should be in RoleNames
    #     if role not in RoleNames:
    #         raise ValueError("Role is invalid")
    #     return role

    # @field_validator("email")
    # @classmethod
    # def check_email_format(cls: Any, email: str, **kwargs: Any) -> Any:
    #     try:
    #         valid = validate_email(email)
    #         # Update with the normalized form.
    #         return valid.email
    #     except EmailNotValidError as e:
    #         raise ValueError(e)


class AccountPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    display_name: Optional[str] = None
    email: Annotated[Optional[str], AfterValidator(check_mail_format)] = None
    phone: Optional[str] = None
    desc: Optional[str] = None

    password: Annotated[Optional[str], AfterValidator(check_password_complex)] = None
    role: Optional[RoleNames] = None
    is_blocked: Optional[bool] = None


class AccountSetting(BaseModel):
    id: str
    role: Optional[str] = None
    is_blocked: Optional[bool] = None


class AccountPassword(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls: Any, password: str, **kwargs: Any) -> str:
        return check_password_complex(password)


class AccountQuery(BaseModel):
    query: Optional[Dict] = Field(
        default=None,
    )


class Account(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    role: Role

    # @validator("role")
    # def validate_roles(cls: Any, role: int, **kwargs: Any) -> Any:
    #     if not set(role).issubset(set(AppUserPermissionRule.all_permissions.value)):
    #         raise ValueError("Role is invalid")
    #     return role


class AccountOut(Account):
    model_config = ConfigDict(from_attributes=True)
    username:Optional[str] = None
    id: str
    user_type: str


class AccountDetailOut(Account):
    pass


class AccountBasicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_type: str
    username: str
    display_name: Optional[str] = None
    # email: Annotated[Optional[str], AfterValidator(check_mail_format)]

class KibanaAccountOut(AccountBasicOut):
    
    email: str
    kibana_roles: Optional[list[str]] = None

class CreateAPIAccountIn(BaseModel):
    username: str
    desc: str = ""
    valid_days: Optional[int] = 90


class APIAccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    desc: str
    created_at: datetime
    token: str = Field(validation_alias="password_hashed")
    is_blocked: bool = False

    @computed_field
    @property
    def expired_at(self) -> datetime:
        if (self.token is None) or (self.token == ""):
            return datetime.now()
        jwt = AuthJWT.get_raw_jwt(self.token)
        return datetime.fromtimestamp(jwt["exp"])


class APIAccountTokenRenewIn(BaseModel):
    valid_days: int


class UpdataAccountKibanaRolesIn(BaseModel):
    kibana_roles: List[str]
    username: str


class UpdataAccountKibanaRolesInOut(BaseModel):
    id: str
    kibana_roles: List[str]
    username: str
