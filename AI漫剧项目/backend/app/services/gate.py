"""确认闸口服务（PRD 5.0.1 / 6.2）。

规则：
- 所有 AI 请求先创建 draft（意图复述 + 成本预估），确认后才执行；
- 用户 confirm -> 执行；reject -> 重新复述（≤3 轮）；超时/放弃 -> cancelled 零费用；
- 闸口关闭时：单次成本 >=50 元或批量 >=20 镜头仍强制确认（成本护栏）。
"""
from datetime import datetime

from sqlalchemy.orm import Session

from ..models import AIRequest, User
from ..schemas import AIRequestCreate, CostEstimate


def create_ai_request(db: Session, user: User, data: AIRequestCreate) -> AIRequest:
    req = AIRequest(
        user_id=user.id,
        project_id=data.project_id,
        module=data.module,
        intent=data.intent,
        params_json=data.params,
        cost_estimate=data.cost_estimate.model_dump() if data.cost_estimate else {},
        status="draft",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def gate_required(user: User, data: AIRequestCreate) -> bool:
    """判断该请求是否必须经过确认闸口。

    返回 True = 需要确认；False = 可绕过（闸口已关闭且非高成本/批量）。
    """
    gate_setting = user.gate_setting or {}
    disabled = gate_setting.get("gate_disabled", False)

    ce: CostEstimate = data.cost_estimate
    est_max = ce.max if ce else 0.0
    batch_count = int(data.params.get("count", 0) or data.params.get("chapter_count", 0) or 0)

    # 成本护栏：高成本/批量任务即使关闭闸口也强制确认
    if est_max >= 50.0 or batch_count >= 20:
        return True

    # 模块级关闭
    module_off = gate_setting.get("disabled_modules", [])
    if data.module in module_off:
        return False

    # 全局/会话关闭
    if disabled:
        return False

    return True


def confirm_request(db: Session, req: AIRequest, user: User) -> AIRequest:
    if req.status != "draft":
        return req
    req.status = "confirmed"
    req.confirmed_at = datetime.utcnow()
    db.commit()
    db.refresh(req)
    return req


def reject_request(db: Session, req: AIRequest, user: User, note: str = "") -> AIRequest:
    """用户修改/驳回：重新复述（最多 3 轮），超过则转 cancelled。"""
    req.confirm_round += 1
    if req.confirm_round >= 3:
        req.status = "cancelled"
    else:
        req.status = "draft"
        req.intent = note or req.intent
    db.commit()
    db.refresh(req)
    return req


def cancel_request(db: Session, req: AIRequest) -> AIRequest:
    req.status = "cancelled"
    db.commit()
    db.refresh(req)
    return req


def mark_bypassed(db: Session, req: AIRequest) -> AIRequest:
    req.status = "bypassed"
    req.confirmed_at = datetime.utcnow()
    db.commit()
    db.refresh(req)
    return req
