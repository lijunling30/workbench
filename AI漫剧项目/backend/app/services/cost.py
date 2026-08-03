"""成本记账服务（A-2 成本模型）：镜头级记账，汇总到项目级/用户级。"""
from sqlalchemy.orm import Session

from ..config import settings
from ..models import CostLog, Project, User


def record_cost(
    db: Session,
    user: User,
    project_id: int,
    module: str,
    vendor: str = "",
    model: str = "",
    tokens: int = 0,
    duration: float = 0.0,
    amount: float = 0.0,
) -> CostLog:
    log = CostLog(
        user_id=user.id,
        project_id=project_id,
        module=module,
        vendor=vendor,
        model=model,
        tokens=tokens,
        duration=duration,
        amount=round(amount, 4),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def text_cost(tokens: int) -> float:
    return round(tokens / 1000 * settings.cost_per_1k_tokens, 4)


def image_cost(n: int) -> float:
    return round(n * settings.cost_per_image, 4)


def video_cost(seconds: float) -> float:
    return round(seconds * settings.cost_per_second_video, 4)


def project_cost(db: Session, project_id: int) -> float:
    total = db.query(CostLog).filter(CostLog.project_id == project_id)
    return round(sum(c.amount for c in total.all()), 4)


def user_cost(db: Session, user_id: int) -> float:
    total = db.query(CostLog).filter(CostLog.user_id == user_id)
    return round(sum(c.amount for c in total.all()), 4)


def check_budget(db: Session, project: Project) -> dict:
    """预算检查：<80% 正常；80-100% 预警；>=100% 拦截。"""
    spent = project_cost(db, project.id)
    limit = project.budget_limit or 1
    ratio = spent / limit
    if ratio >= 1.0:
        status = "blocked"
    elif ratio >= 0.8:
        status = "warning"
    else:
        status = "ok"
    return {"spent": spent, "limit": project.budget_limit, "ratio": round(ratio * 100, 1), "status": status}
