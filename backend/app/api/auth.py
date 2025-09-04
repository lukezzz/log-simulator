# from aioredis import Redis
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime

from core.auth_jwt import AuthJWT
from core.custom_api_route import HandleResponseRoute
from core.dependencies.db import DBSession

from services.account import get_account_by_id, set_api_token_to_blacklist
from services.aaa import auth_user
from schemas.account import AccountOut, Permissions
from core.dependencies.aaa import AuthUser, require_permissions, oauth2_scheme
from redis import Redis
from core.dependencies.redis import get_auth_redis

# from schemas.auth import SAMLConfigBase, SAMLConfigOut
# from models.config import SysSAMLConfig
# from variable import http_exceptions
# from onelogin.saml2.auth import OneLogin_Saml2_Auth


router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["auth"],
    responses={404: {"detail": "Not found"}},
)


@router.post(
    "/login",
    summary="Local user login",
    description="Local user login",
    # response_model=schemas.TokenOut,
)
async def login_for_access_token(
    db: DBSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await auth_user(db, form_data.username, form_data.password)
    scopes = [i.name for i in user.role.permissions]
    access_token = AuthJWT.create_access_token(
        subject=user.id, user_claims={"scopes": scopes}
    )
    refresh_token = AuthJWT.create_refresh_token(subject=user.id)

    # TODO create event table and audit login event
    # services.event.event_login_create(db, user)

    # Set the JWT cookies in the response
    data = {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "scopes": scopes,
    }
    return data


class RefreshReq(BaseModel):
    access_token: str
    refresh_token: str


# Standard refresh endpoint. Token in denylist will not
# be able to access this endpoint
@router.post("/refresh", summary="refresh access_token")
async def refresh(db: DBSession, refresh: RefreshReq):
    await AuthJWT.jwt_refresh_token_required(refresh.refresh_token)
    user_id = AuthJWT.get_jwt_subject(refresh.access_token)
    obj = AuthJWT.get_raw_jwt(refresh.access_token)
    exp = obj["exp"]
    # 判断当前时间是否大于过期时间超过20分钟
    if datetime.now().timestamp() > exp + 1200:
        raise HTTPException(status_code=401, detail="Token expired")
    user = await get_account_by_id(db, user_id)
    scopes = [i.name for i in user.role.permissions]
    access_token = AuthJWT.create_access_token(
        subject=user.id, user_claims={"scopes": scopes}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Local user logout api, clear access_token and refresh_token
@router.post("/logout")
@require_permissions(Permissions.me)
async def logout(
    rds: Annotated[Redis, Depends(get_auth_redis)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> str:
    await set_api_token_to_blacklist(rds, token)
    return "Logout successfully"


@router.get(
    "/self",
    response_model=AccountOut,
    summary="Get current account info",
)
@require_permissions(Permissions.me)
async def get_self(
    user: AuthUser,
):
    return user
