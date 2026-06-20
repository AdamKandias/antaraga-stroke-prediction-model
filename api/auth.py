"""Our own auth: issues and verifies access tokens for the users we store in
api/models_db.py::User. No third-party auth provider involved.

In DEV_MODE, requests without an Authorization header are allowed through as
a fixed dev user — useful for curl/dashboard testing without registering.
"""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from api import models_db
from api.config import DEV_MODE, JWT_EXPIRE_DAYS, JWT_SECRET
from api.database import get_db

DEV_USER_ID = "dev-user"

ALGORITHM = "HS256"


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(days=JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def get_current_user_id(
    authorization: str | None = Header(None), db: Session = Depends(get_db)
) -> str:
    if authorization is None:
        if DEV_MODE:
            return DEV_USER_ID
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header must be 'Bearer <token>'")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {exc}") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing 'sub' claim")

    # Marks this user as "currently active" for the dev hardware simulator
    # (api/simulator.py) -- a real Bearer token means a real app session,
    # unlike the DEV_MODE no-header fallback above.
    db.query(models_db.User).filter(models_db.User.id == user_id).update(
        {"last_seen_at": datetime.now(timezone.utc)}
    )
    db.commit()

    return user_id
