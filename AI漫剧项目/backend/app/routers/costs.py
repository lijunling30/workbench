"""A-2 成本模型：成本明细查询与对账。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CostLog, User
from ..schemas import CostLogOut
from ..services.auth import get_current_user
from ..services.cost import project_cost, user_cost

router = APIRouter(prefix="/costs", tags=["成本对账"])


@router.get("", response_model=list[CostLogOut])
def my_costs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(CostLog).filter(CostLog.user_id == user.id).order_by(CostLog.id.desc()).limit(100).all()


@router.get("/summary")
def cost_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {
        "total": user_cost(db, user.id),
        "budget_limit": user.budget_limit,
    }


@router.get("/projects/{project_id}/logs", response_model=list[CostLogOut])
def project_cost_logs(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(CostLog).filter(CostLog.project_id == project_id).order_by(CostLog.id.desc()).all()
