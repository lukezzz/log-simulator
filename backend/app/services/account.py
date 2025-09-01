from sqlalchemy import select
from models import Account, Role
from core.dependencies.db import DBSession

from schemas import (
    AccountCreate,
    AccountPatch,
    AccountPassword,
    AccountSetting,
    CreateAPIAccountIn,
)
from core.security import get_password_hash
from fastapi.exceptions import HTTPException
from core.security import gen_uuid
from datetime import timedelta, datetime, timezone
from core.auth_jwt.auth_jwt import AuthJWT

# async def get_asset_by_id(db: DBSession, asset_id: str) -> Asset:
#     res = await db.execute(select(Asset).where(Asset.asset_id == asset_id))
#     return res.scalars().one_or_none()


async def get_role_by_name(db: DBSession, name: str) -> Role:
    res = await db.execute(select(Role).where(Role.name == name))
    return res.scalars().one_or_none()


async def get_account_by_username(db: DBSession, username: str) -> Account:
    query = select(Account).where(Account.username == username)
    res = await db.execute(query)
    return res.scalars().one_or_none()


async def get_account_by_email(db: DBSession, email: str) -> Account:
    res = await db.execute(select(Account).where(Account.email == email))
    return res.scalars().one_or_none()


async def get_account_by_id(db: DBSession, user_account_id: str) -> Account:
    res = await db.execute(select(Account).where(Account.id == user_account_id))
    return res.scalars().one_or_none()


async def create_account(db: DBSession, req: AccountCreate):
    try:
        password_hashed = get_password_hash(req.password)

        user_data = req.model_dump(exclude_none=True)
        del user_data["password"]

        del user_data["role"]

        user_data["password_hashed"] = password_hashed

        user_post = Account(**user_data)
        db.add(user_post)

        role = await get_role_by_name(db, req.role)
        if role:
            user_post.role = role

        await db.commit()
        await db.refresh(user_post)
        return user_post

    except Exception as err:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=err,
        )


async def delete_account(db: DBSession, account: Account):
    try:
        if account:
            await db.delete(account)
            await db.commit()
            return True
        else:
            return False
    except Exception as err:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=err,
        )


async def update_account(
    db: DBSession, patch_config: AccountPatch, patch_account: Account
):
    try:
        user_data = patch_config.model_dump(exclude_none=True)
        for item in user_data:
            if item == "password":
                hashed_password = get_password_hash(user_data["password"])
                setattr(patch_account, "hashed_password", hashed_password)
            elif item == "role":
                role = await get_role_by_name(db, user_data[item])
                if role:
                    setattr(patch_account, item, role)
            else:
                setattr(patch_account, item, user_data[item])

        await db.commit()
        await db.refresh(patch_account)
        return patch_account
    except Exception as err:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=err,
        )


async def account_setting(
    db: DBSession, patch_config: AccountSetting, patch_account: Account
):
    if patch_config.role:
        role = await get_role_by_name(db, patch_config.role)
        if role:
            patch_account.role = role
    if patch_config.is_blocked is not None:
        patch_account.is_blocked = patch_config.is_blocked

    try:
        await db.commit()
        await db.refresh(patch_account)
        return patch_account
    except Exception as err:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=err,
        )


async def change_password(
    db: DBSession, new_password: AccountPassword, current_user: Account
):
    current_user.set_password(new_password.password)
    await db.commit()
    await db.refresh(current_user)
    return current_user


# TODO role -> udpate list
# def update_user_account_role(db: Session, role: int, patch_user: any):

#     try:
#         post_role = db.query(Role).filter_by(id=role).first()
#         patch_user.roles = post_role

#         db.commit()
#         db.refresh(patch_user)
#         return patch_user
#     except Exception as err:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=err,
#         )


async def set_api_token_to_blacklist(auth_rds, token):
    payload = AuthJWT.get_raw_jwt(token)
    if payload:
        await auth_rds.setex(
            payload["jti"],
            timedelta(seconds=payload["exp"] - datetime.now(timezone.utc).timestamp()),
            "true",
        )


async def create_api_token(user: Account, valid_days: int):
    access_token = AuthJWT.create_access_token(
        subject=user.id,
        user_claims={"scopes": ["api"]},
        expires_delta=timedelta(days=valid_days),
    )
    return access_token


async def create_api_account(db: DBSession, req: CreateAPIAccountIn):
    try:

        api_account = Account()
        api_account.username = req.username
        api_account.display_name = req.username
        api_account.password_hashed = ""
        api_account.desc = req.desc
        api_account.email = gen_uuid()
        api_account.role = await get_role_by_name(db, "api")
        api_account.user_type = "api"

        db.add(api_account)

        await db.commit()

        api_account.password_hashed = await create_api_token(
            api_account, req.valid_days
        )
        await db.commit()
        await db.refresh(api_account)

        return api_account

    except Exception as err:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=err,
        )
