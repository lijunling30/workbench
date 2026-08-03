"""M6/M7/M8/M9：关键帧、视频任务、配音、成片。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AudioAsset, FinalVideo, Keyframe, Shot, User, VideoTask
from ..schemas import FinalVideoOut, KeyframeOut, RenderIn, VideoTaskOut
from ..services.auth import get_current_user
from ..services import pipeline

router = APIRouter(prefix="/assets", tags=["关键帧/视频/音频/成片"])


# ---------- 关键帧 ----------
@router.get("/shots/{shot_id}/keyframes", response_model=list[KeyframeOut])
def list_keyframes(shot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Keyframe).filter(Keyframe.shot_id == shot_id).order_by(Keyframe.score.desc()).all()


@router.post("/keyframes/{kf_id}/approve")
def approve_keyframe(kf_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    kf = db.get(Keyframe, kf_id)
    if not kf:
        raise HTTPException(status_code=404, detail="关键帧不存在")
    # 取消该镜头其他候选的 approved，置当前为 approved
    db.query(Keyframe).filter(Keyframe.shot_id == kf.shot_id).update({"is_approved": False})
    kf.is_approved = True
    db.commit()
    return {"message": "已选定", "keyframe_id": kf.id}


# ---------- 视频任务 ----------
@router.get("/shots/{shot_id}/videos", response_model=list[VideoTaskOut])
def list_videos(shot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(VideoTask).filter(VideoTask.shot_id == shot_id).all()


# ---------- 音频 ----------
@router.get("/shots/{shot_id}/audio")
def list_audio(shot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(AudioAsset).filter(AudioAsset.shot_id == shot_id).all()


# ---------- 成片 ----------
@router.post("/render", response_model=FinalVideoOut)
def render(data: RenderIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """渲染成片：强制携带 AI 生成标识（ai_labeled=True 无开关）。"""
    return pipeline.execute_render(db, user, data.project_id, data.episode_no, data.enable_audit)


@router.get("/projects/{project_id}/final-videos", response_model=list[FinalVideoOut])
def list_final_videos(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(FinalVideo).filter(FinalVideo.project_id == project_id).all()


@router.get("/shots/{shot_id}", response_model=None)
def get_shot(shot_id: int, db: Session = Depends(get_db)):
    return db.get(Shot, shot_id)
