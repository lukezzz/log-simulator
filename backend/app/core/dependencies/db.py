from fastapi import Depends
from core.db.session import get_db
from typing import Annotated
from sqlalchemy.orm import Session

DBSession = Annotated[Session, Depends(get_db)]