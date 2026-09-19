from fastapi import APIRouter, Depends

from auth.authorization import require_roles
from auth.roles import UserRole
from core.tenant import get_tenant_id
from models.user import User


router = APIRouter(
    prefix="/security-test",
    tags=["Security Test"]
)


@router.get("/hospital-admin")
def hospital_admin_test(
    current_user: User = Depends(
        require_roles(UserRole.HOSPITAL_ADMIN)
    ),
    hospital_id: int = Depends(get_tenant_id)
):
    return {
        "message": "Hospital Admin access granted",
        "user_id": current_user.id,
        "hospital_id": hospital_id,
        "role": current_user.role
    }
