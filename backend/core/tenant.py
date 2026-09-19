from fastapi import Depends, HTTPException, status

from auth.dependencies import get_current_user
from models.user import User


def get_tenant_id(
    current_user: User = Depends(get_current_user)
) -> int:

    if current_user.hospital_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a hospital"
        )

    return current_user.hospital_id
