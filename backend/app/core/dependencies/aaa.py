from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_decorators import depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas.account import Permissions
from core.security import verify_password
from models.aaa import Account
from core.auth_jwt import AuthJWT

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# aaa section


def authenticate_user(db: Session, username: str, password: str):
    user: Account = db.query(Account).filter(Account.username == username).first()
    if not user or not verify_password(password, user.password_hashed):
        raise HTTPException(status_code=401, detail="Bad username or password")
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session,
) -> Account:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    await AuthJWT.jwt_required(token)

    payload = AuthJWT.get_raw_jwt(token)
    uid = payload.get("sub")
    if not uid:
        raise credentials_exception
    # user = db.query(Account).filter(Account.id == uid).first()
    mgmt = await db.scalars(select(Account).filter(Account.id == uid))
    user = mgmt.first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    user: Annotated[Account, Depends(get_current_user)],
):
    if user.is_blocked:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def require_permissions(*required_permissions: list[Permissions]):
    def dependency(user: Account = Depends(get_current_active_user)):
        user_permissions = [i.name for i in user.role.permissions]
        for permission in required_permissions:
            p = permission.value if isinstance(permission, Permissions) else permission
            if p not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                )
        return user

    return depends(Depends(dependency))


async def is_admin(
    user: Annotated[Account, Depends(get_current_user)],
) -> bool:
    if user.role.name != "admin":
        return False
    return True


AuthUser = Annotated[Account, Depends(get_current_active_user)]
