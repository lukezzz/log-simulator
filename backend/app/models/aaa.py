from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped
from core.db.base import BaseModel
from core.security import get_password_hash
from sqlalchemy.ext.mutable import MutableList


role_permission_association = Table(
    "aaa_role_permission",
    BaseModel.metadata,
    Column("role_id", String(64), ForeignKey("aaa_roles.id")),
    Column("permission_id", String(64), ForeignKey("aaa_permissions.id")),
)


class Role(BaseModel):
    __tablename__ = "aaa_roles"
    name = Column(String(64), unique=True, index=True)
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permission_association, back_populates="role", lazy="selectin"
    )
    accounts: Mapped[list["Account"]] = relationship(back_populates="role")


class Permission(BaseModel):
    __tablename__ = "aaa_permissions"
    name = Column(String(64), unique=True, index=True)

    role: Mapped[list[Role]] = relationship(
        secondary=role_permission_association,
        back_populates="permissions",
        lazy="selectin",
    )


class Account(BaseModel):
    __tablename__ = "aaa_accounts"

    username = Column(String(64), unique=True, index=True)
    display_name = Column(String(128), unique=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    password_hashed = Column(String, nullable=False)
    email = Column(String(64), unique=True, index=True, nullable=False)
    address = Column(String(128))
    phone = Column(String(32))

    desc = Column(String(256))

    is_blocked = Column(Boolean, default=False, nullable=False)

    role_id = Column(String(64), ForeignKey("aaa_roles.id"))
    role: Mapped[Role] = relationship(
        back_populates="accounts",
        lazy="selectin",
    )

    last_login = Column(DateTime)

    user_type = Column(String(64), default="local")  # local | saml | api
    # foreign key

    def set_password(self, password):
        self.password_hashed = get_password_hash(password)
