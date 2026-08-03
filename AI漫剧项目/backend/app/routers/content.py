"""内容查询：小说 / 剧本 / 分镜。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Novel, Script, Shot, User
from ..schemas import NovelOut, ScriptOut, ShotOut, ShotUpdateIn
from ..services.auth import get_current_user

router = APIRouter(prefix="/content", tags=["内容管理"])


def _check_user(db: Session, user: User, owner_id: int):
    if owner_id != user.id:
        raise HTTPException(status_code=404, detail="内容不存在")


# ---------- 小说 ----------
@router.get("/projects/{project_id}/novels", response_model=list[NovelOut])
def list_novels(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Novel).filter(Novel.project_id == project_id).all()


@router.get("/novels/{novel_id}", response_model=NovelOut)
def get_novel(novel_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = db.get(Novel, novel_id)
    if not n:
        raise HTTPException(status_code=404, detail="小说不存在")
    return n


# ---------- 剧本 ----------
@router.get("/novels/{novel_id}/scripts", response_model=list[ScriptOut])
def list_scripts(novel_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Script).filter(Script.novel_id == novel_id).all()


# ---------- 分镜 ----------
@router.get("/scripts/{script_id}/shots", response_model=list[ShotOut])
def list_shots(script_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Shot).filter(Shot.script_id == script_id).order_by(Shot.shot_no).all()


@router.put("/shots/{shot_id}", response_model=ShotOut)
def update_shot(shot_id: int, data: ShotUpdateIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    shot = db.get(Shot, shot_id)
    if not shot:
        raise HTTPException(status_code=404, detail="分镜不存在")
    for k, v in data.model_dump().items():
        if v not in ("", 0) or k == "duration":
            setattr(shot, k, v)
    db.commit()
    db.refresh(shot)
    return shot
