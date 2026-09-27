import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.policy import PolicyCreate, PolicyResponse
from app.services.policy_service import create_policy, get_policy, list_policies

router = APIRouter(
    prefix="/api/v1/policies",
    tags=["policies"],
)


@router.post(
    "",
    response_model=PolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_policy(
    data: PolicyCreate,
    db: Session = Depends(get_db),
):
    return create_policy(db, data)


@router.get(
    "",
    response_model=list[PolicyResponse],
)
def get_policies(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    return list_policies(db, active_only=active_only)


@router.get(
    "/{policy_id}",
    response_model=PolicyResponse,
)
def get_policy_detail(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    policy = get_policy(db, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy
