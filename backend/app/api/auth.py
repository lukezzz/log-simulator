# from aioredis import Redis
import string
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import  RedirectResponse
from pydantic import BaseModel
from datetime import datetime

from core.auth_jwt import AuthJWT
from core.custom_api_route import HandleResponseRoute
from core.dependencies.db import DBSession
from core.security import get_password_hash
from services import account

from services.account import get_account_by_id, set_api_token_to_blacklist
from services.aaa import auth_user
from fastapi.logger import logger
from schemas.account import AccountOut, Permissions
from core.dependencies.aaa import AuthUser, require_permissions, oauth2_scheme
from models import Account
from sqlalchemy import select
from redis import Redis
from core.dependencies.redis import get_auth_redis
import random
import base64
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

    # TODO create event talbe and audit login event
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
):
    # Authorize.jwt_required()
    # payload = AuthJWT.get_raw_jwt(token)
    # await rds.setex(
    #     payload["jti"],
    #     timedelta(seconds=get_settings().authjwt_access_token_expires),
    #     "true",
    # )
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


# SSO
"""
@router.get("/saml_config")
@require_permissions(Permissions.admin)
async def get_saml_config(
    db: DBSession,
):
    # only support one config
    stmt = await db.execute(select(SysSAMLConfig))
    config = stmt.scalars().one_or_none()

    if not config:
        # create default config
        config = SysSAMLConfig()
        db.add(config)
        await db.commit()
        await db.refresh(config)

    return config


@router.post(
    "/saml_config",
    response_model=SAMLConfigOut,
)
@require_permissions(Permissions.admin)
async def update_saml_sp(req: SAMLConfigBase, db: DBSession):
    stmt = await db.execute(select(SysSAMLConfig))
    config = stmt.scalars().one_or_none()

    if not config:
        # create default config
        config = SysSAMLConfig()
        db.add(config)

    for k, v in req.model_dump().items():
        setattr(config, k, v)

    await db.commit()
    await db.refresh(config)

    return config


# SSO login
async def prepare_from_fastapi_request(request: Request):
    form_data = await request.form()
    rv = {
        "http_host": request.client.host,
        "server_port": request.url.port,
        "script_name": request.url.path,
        "post_data": {},
        "get_data": {},
        # Advanced request options
        # "https": "",
        # "request_uri": "",
        # "query_string": "",
        # "validate_signature_from_qs": False,
        # "lowercase_urlencoding": False
    }
    if request.query_params:
        rv["get_data"] = (request.query_params,)
    if "SAMLResponse" in form_data:
        SAMLResponse = form_data["SAMLResponse"]
        rv["post_data"]["SAMLResponse"] = SAMLResponse
    if "RelayState" in form_data:
        RelayState = form_data["RelayState"]
        rv["post_data"]["RelayState"] = RelayState
    return rv


async def update_saml_user(
    db: DBSession,
    user: Account,
    username: str,
    email: str,
    display_name: str,
    phone: str,
) -> Account:
    # 上次登录时间超过30天则block账户
    if user.last_login:
        if (datetime.now() - user.last_login).days > 30:
            user.is_blocked = True
    user.username = username
    user.email = email
    user.phone = phone
    user.display_name = display_name
    user.user_type = "sso"
    user.last_login = datetime.now()
    await db.commit()
    await db.refresh(user)
    return user


async def auth_saml_user(
    db: DBSession,
    username: str,
    email: str,
    display_name: str,
    phone: str,
    id: str = None,
    authing_role: Optional[str] = None
) -> Account:
    pre_config_user_mgmt = select(Account).where(Account.email == email)
    pre_config_user = (await db.scalars(pre_config_user_mgmt)).first()
    # 先校验email
    if pre_config_user:
        pre_config_user = await update_saml_user(
            db,
            user=pre_config_user,
            username=username,
            email=email,
            phone=phone,
            display_name=display_name,
        )
        # TODO need to sync role with authing
        # if user role defined in authing and current is admin, we will update the user role, else set default as guest for new user
        if authing_role and authing_role == "admin":
            admin_role = await account.get_role_by_name(db, "admin")
            pre_config_user.role_id = admin_role.id
            await db.commit()
        return pre_config_user
    # # 再校验display_name
    # elif (
    #     pre_config_user := db.query(Account)
    #     .filter_by(display_name=display_name)
    #     .first()
    # ):
    #     pre_config_user = update_saml_user(
    #         db, user=pre_config_user, username=username, email=email, phone=phone
    #     )
    #     return pre_config_user
    # # 最后校验username
    # elif pre_config_user := db.query(Account).filter_by(username=username).first():
    #     pre_config_user = update_saml_user(
    #         db, user=pre_config_user, username=username, email=email, phone=phone
    #     )
    #     return pre_config_user
    # # 都不存在则创建


    role = await account.get_role_by_name(db, "guest")
    if id:
        user = Account(
            id=id,
            username=username,
            display_name=display_name,
            email=email,
            phone=phone,
            role_id=role.id,
        )
    else:
        user = Account(
            username=username,
            display_name=display_name,
            email=email,
            phone=phone,
            role_id=role.id,
        )
    # generate random password
    user.password_hashed = get_password_hash(
        "".join(random.choices(string.ascii_letters + string.digits, k=16))
    )
    db.add(user)
    user.user_type = "sso"
    user.last_login = datetime.now()
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/saml_login")
async def saml_login(req: Request, redirectUrl: str, db: DBSession):
    saml_settings = await get_saml_settings(db)
    logger.debug(req.headers)
    auth = OneLogin_Saml2_Auth(None, saml_settings)
    logger.debug(redirectUrl)
    return_to = base64.urlsafe_b64decode(redirectUrl).decode("utf-8")
    logger.debug(f"return_to: {return_to}")
    callback_url = auth.login(return_to=return_to)
    logger.debug(callback_url)
    # response = RedirectResponse(url=callback_url)
    return callback_url


@router.post("/samlp", response_class=RedirectResponse)
async def sso_callback(request: Request, db: DBSession):
    req = await prepare_from_fastapi_request(request)
    saml_settings = await get_saml_settings(db)
    auth = OneLogin_Saml2_Auth(req, saml_settings)
    auth.process_response()  # Process IdP response
    errors = auth.get_errors()  # This method receives an array with the errors
    if len(errors) == 0:
        # logger.error("errors", errors)
        if (
            not auth.is_authenticated()
        ):  # This check if the response was ok and the user data retrieved or not (user authenticated)
            raise http_exceptions.AuthenticatedException
        else:
            data = auth.get_attributes()
            # Retrieve the RelayState (or redirect URL)
            redirect_url = req["post_data"].get("RelayState")
            logger.debug(f"redirect_url======{redirect_url}")

            if not redirect_url:
                redirect_url = "/"
            try:
                if saml_settings["issuer"] == "azure":
                    # return "User authenticated"
                    logger.debug(f"get azure attributes: {data}")

                    username = data[
                        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/samaccountname"
                    ][0]
                    display_name = data[
                        "http://schemas.microsoft.com/identity/claims/displayname"
                    ][0]
                    email = data[
                        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"
                    ][0]
                    id = data[
                        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"
                    ][0]
                    # username = data["name"][0]
                    # display_name = data["name"][0]
                    # email = data["email"][0]
                    # id = data["email"][0]
                elif saml_settings["issuer"] == "authing":
                    username = data["name"][0]
                    display_name = data["name"][0]
                    email = data["email"][0]
                    id = data["email"][0]
                    authing_role = data.get("role", "")[0]
                    # username = data[
                    #     "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/samaccountname"
                    # ][0]
                    # display_name = data[
                    #     "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/displayname"
                    # ][0]
                    # if data.get(
                    #     "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/email"
                    # ):
                    #     email = data[
                    #         "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/email"
                    #     ][0]
                    # else:
                    #     email = data[
                    #         "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/mail"
                    #     ][0]
                else:
                    username = data[
                        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/samaccountname"
                    ][0]
                    display_name = data[
                        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/displayname"
                    ][0]
                    if data.get(
                        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/email"
                    ):
                        email = data[
                            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/email"
                        ][0]
                    else:
                        email = data[
                            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/mail"
                        ][0]
            except Exception as e:
                logger.error(e)
                url = f"{redirect_url}?error={e}"
                return RedirectResponse(
                    url=url,
                    status_code=303,
                )
            user = await auth_saml_user(
                db=db,
                id=id,
                username=username,
                email=email,
                display_name=display_name,
                authing_role=authing_role,
                phone="",
            )
            
            scopes = [i.name for i in user.role.permissions]
            logger.debug(f"scopes: {', '.join(scopes)}")
            access_token = AuthJWT.create_access_token(
                subject=user.id, user_claims={"scopes": scopes}
            )
            refresh_token = AuthJWT.create_refresh_token(subject=user.id)
            # Set the JWT cookies in the response
            data = {"access_token": access_token, "refresh_token": refresh_token}
            # response = JSONResponse(content={"success": True, "data": data})
            url = f"{redirect_url}?access_token={access_token}&refresh_token={refresh_token}"
            response = RedirectResponse(
                url=url,
                status_code=303,
                headers=data,
            )
            # event.event_login_create(db, user)
            return response
    else:
        logger.error(
            "Error when processing SAML Response: %s %s"
            % (", ".join(errors), auth.get_last_error_reason())
        )
        raise HTTPException(
            status_code=400,
            detail="Error when processing SAML Response",
        )
"""
