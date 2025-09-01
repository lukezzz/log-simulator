from datetime import datetime
import random
import string
from fastapi import HTTPException, Request
from core.dependencies.db import DBSession
from core.security import verify_password, get_password_hash
from fastapi.exceptions import HTTPException
from models.aaa import Account
from services.account import get_account_by_username, get_role_by_name
# from services.sys import get_saml_config
# 

async def auth_user(db: DBSession, username: str, password: str) -> Account:
    # user = db.query(Account).filter_by(username=username).first()
    user = await get_account_by_username(db, username)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    if not verify_password(password, user.password_hashed):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password",
        )
    return user

"""
async def get_saml_settings(db: DBSession):
    saml = await get_saml_config(db)

    if not saml:
        raise HTTPException(
            status_code=404,
            detail="SAML config not found",
        )
    saml_settings = {
        "strict": saml.strict,  # can set to True to see problems such as Time skew/drift
        "debug": saml.debug,
        "idp": {
            "entityId": saml.idp_entityId,
            "singleSignOnService": {
                "url": saml.sso_url,
                "binding": saml.sso_binding,
            },
            "x509cert": saml.sso_signing_cert,
        },
        "sp": {
            "entityId": saml.sp_entityId,
            "assertionConsumerService": {
                "url": saml.sp_url,
                "binding": saml.sp_binding,
            },
            "x509cert": "",
        },
        "issuer":saml.issuer,
    }

    return saml_settings


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
    user.username = username
    user.email = email
    user.phone = phone
    user.display_name = display_name
    user.user_type = "sso"
    user.last_login = datetime.now()
    await db.commit()
    db.refresh(user)
    return user


async def auth_saml_user(
    db: DBSession, username: str, email: str, display_name: str, phone: str
) -> Account:
    pre_config_user = db.query(Account).filter_by(email=email).first()
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
        return pre_config_user

    user = Account(
        username=username,
        display_name=display_name,
        email=email,
        phone=phone,
        role_id=await get_role_by_name(db, "user").id,
    )
    # generate random password
    user.password_hashed = get_password_hash(
        "".join(random.choices(string.ascii_letters + string.digits, k=16))
    )
    db.add(user)
    user.user_type = "sso"
    user.last_login = datetime.now()
    await db.commit()
    db.refresh(user)
    return user
"""