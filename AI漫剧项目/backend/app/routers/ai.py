"""确认闸口 + AI 生成统一入口（PRD 5.0.1 / A-4）。

流程：POST /ai/requests 创建 draft -> 前端展示确认卡 -> confirm/reject -> 执行生成。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AIRequest, User
from ..schemas import AIRequestCreate, AIRequestOut, ConfirmIn
from ..services import gate, pipeline
from ..services.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI 生成与确认闸口"])


@router.post("/requests", response_model=AIRequestOut)
def create_request(data: AIRequestCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """创建 AI 请求（确认闸口 draft 状态），不产生任何费用。"""
    req = gate.create_ai_request(db, user, data)
    if not gate.gate_required(user, data):
        # 闸口已关闭且非高成本/批量：自动 bypass 并立即执行
        req = gate.mark_bypassed(db, req)
        result = _execute(db, user, data.module, data.params)
        return req
    return req


def _execute(db: Session, user: User, module: str, params: dict):
    if module == "novel":
        return pipeline.execute_novel(db, user, int(params.get("project_id", 0)), params)
    if module == "script":
        return pipeline.execute_script(db, user, int(params.get("novel_id", 0)))
    if module == "shot":
        return pipeline.execute_shots(db, user, int(params.get("script_id", 0)))
    if module == "character":
        return pipeline.execute_character_images(db, user, int(params.get("character_id", 0)))
    if module == "keyframe":
        return pipeline.execute_keyframes(db, user, int(params.get("shot_id", 0)), int(params.get("count", 3)))
    if module == "video":
        return pipeline.execute_video(db, user, int(params.get("shot_id", 0)),
                                      params.get("keyframe_id"), params.get("vendor", "vidu"))
    if module == "audio":
        return pipeline.execute_audio(db, user, int(params.get("shot_id", 0)), params.get("type", "voice"))
    if module == "render":
        return pipeline.execute_render(db, user, int(params.get("project_id", 0)),
                                       int(params.get("episode_no", 1)), bool(params.get("enable_audit", False)))
    raise HTTPException(status_code=400, detail=f"未知模块: {module}")


@router.post("/requests/{req_id}/confirm", response_model=AIRequestOut)
def confirm(req_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """用户确认：执行对应模块的生成任务。"""
    req = db.get(AIRequest, req_id)
    if not req or req.user_id != user.id:
        raise HTTPException(status_code=404, detail="请求不存在")
    req = gate.confirm_request(db, req, user)
    try:
        _execute(db, user, req.module, req.params_json or {})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return req


@router.post("/requests/{req_id}/reject", response_model=AIRequestOut)
def reject(req_id: int, data: ConfirmIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    req = db.get(AIRequest, req_id)
    if not req or req.user_id != user.id:
        raise HTTPException(status_code=404, detail="请求不存在")
    return gate.reject_request(db, req, user, data.edit_note)


@router.post("/requests/{req_id}/cancel", response_model=AIRequestOut)
def cancel(req_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    req = db.get(AIRequest, req_id)
    if not req or req.user_id != user.id:
        raise HTTPException(status_code=404, detail="请求不存在")
    return gate.cancel_request(db, req)


@router.get("/requests", response_model=list[AIRequestOut])
def list_requests(status: str = "", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(AIRequest).filter(AIRequest.user_id == user.id)
    if status:
        q = q.filter(AIRequest.status == status)
    return q.order_by(AIRequest.id.desc()).limit(50).all()


@router.put("/settings/gate")
def update_gate_setting(data: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """闸口开关配置：{gate_disabled: bool, disabled_modules: [..]}。"""
    user.gate_setting = data
    db.commit()
    return {"gate_setting": user.gate_setting}
