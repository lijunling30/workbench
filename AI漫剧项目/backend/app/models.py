"""数据模型：对齐 PRD 7.1 / 技术栈说明书 2.5 核心数据表（v1.3）。"""
from datetime import datetime
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="creator")  # creator/admin
    plan: Mapped[str] = mapped_column(String(16), default="personal")  # personal/team/enterprise
    budget_limit: Mapped[float] = mapped_column(Float, default=2000.0)
    gate_setting: Mapped[dict] = mapped_column(JSON, default=dict)  # 确认闸口偏好（会话/模块/全局）
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    genre: Mapped[str] = mapped_column(String(64), default="")
    style_id: Mapped[str] = mapped_column(String(64), default="style-01")
    style_desc: Mapped[str] = mapped_column(Text, default="")
    target_platform: Mapped[str] = mapped_column(String(32), default="douyin")  # douyin/bilibili
    status: Mapped[str] = mapped_column(String(16), default="active")
    budget_limit: Mapped[float] = mapped_column(Float, default=5000.0)
    ip_source: Mapped[str] = mapped_column(Text, default="")  # 版权/IP 授权来源声明
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Novel(Base):
    __tablename__ = "novel"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project.id"), index=True)
    title: Mapped[str] = mapped_column(String(128))
    genre: Mapped[str] = mapped_column(String(64), default="")
    premise: Mapped[str] = mapped_column(Text, default="")
    outline: Mapped[list] = mapped_column(JSON, default=list)      # 章节大纲
    chapters: Mapped[list] = mapped_column(JSON, default=list)     # 正文 [{no,title,content}]
    characters: Mapped[list] = mapped_column(JSON, default=list)   # 角色表
    settings: Mapped[list] = mapped_column(JSON, default=list)     # 设定集
    status: Mapped[str] = mapped_column(String(16), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Script(Base):
    __tablename__ = "script"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    novel_id: Mapped[int] = mapped_column(Integer, ForeignKey("novel.id"), index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project.id"), index=True)
    scenes: Mapped[list] = mapped_column(JSON, default=list)       # [{no,location,emotion,dialogue[],narration,action}]
    emotion_curve: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(16), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Shot(Base):
    __tablename__ = "shot"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    script_id: Mapped[int] = mapped_column(Integer, ForeignKey("script.id"), index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project.id"), index=True)
    shot_no: Mapped[int] = mapped_column(Integer)
    shot_type: Mapped[str] = mapped_column(String(16), default="中景")  # 特写/近景/中景/远景
    camera_move: Mapped[str] = mapped_column(String(16), default="固定")  # 推/拉/摇/移/固定
    duration: Mapped[float] = mapped_column(Float, default=5.0)
    scene_desc: Mapped[str] = mapped_column(Text, default="")
    prompt_zh: Mapped[str] = mapped_column(Text, default="")          # 纯中文画面提示词
    dialogue: Mapped[str] = mapped_column(Text, default="")
    narration: Mapped[str] = mapped_column(Text, default="")
    transition: Mapped[str] = mapped_column(String(16), default="硬切")
    char_ref_ids: Mapped[list] = mapped_column(JSON, default=list)     # [CHAR:01]
    style_id: Mapped[str] = mapped_column(String(64), default="style-01")
    status: Mapped[str] = mapped_column(String(16), default="draft")   # draft/keyframed/video_ready
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CharacterLibrary(Base):
    """人物子库（M5）：按项目管理的一组角色资产。"""
    __tablename__ = "character_library"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    desc: Mapped[str] = mapped_column(Text, default="")
    project_ids: Mapped[list] = mapped_column(JSON, default=list)
    is_shared: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String(16), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Character(Base):
    __tablename__ = "character"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    library_id: Mapped[int] = mapped_column(Integer, ForeignKey("character_library.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    desc: Mapped[str] = mapped_column(Text, default="")           # 外貌/服饰/性格
    ref_images: Mapped[list] = mapped_column(JSON, default=list)   # 三视图 url
    expression_set: Mapped[list] = mapped_column(JSON, default=list)  # 喜怒哀乐
    lora_version: Mapped[str] = mapped_column(String(32), default="")
    status: Mapped[str] = mapped_column(String(16), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Keyframe(Base):
    __tablename__ = "keyframe"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shot_id: Mapped[int] = mapped_column(Integer, ForeignKey("shot.id"), index=True)
    image_url: Mapped[str] = mapped_column(Text, default="")
    prompt: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[float] = mapped_column(Float, default=0.0)   # AI 评分
    is_approved: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class VideoTask(Base):
    __tablename__ = "video_task"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shot_id: Mapped[int] = mapped_column(Integer, ForeignKey("shot.id"), index=True)
    keyframe_id: Mapped[int] = mapped_column(Integer, ForeignKey("keyframe.id"))
    vendor: Mapped[str] = mapped_column(String(32), default="vidu")   # vidu/seedance/kling
    model: Mapped[str] = mapped_column(String(64), default="Q3")
    status: Mapped[str] = mapped_column(String(24), default="queued")  # queued/running/success/failed/retrying/manual_review/cancelled
    result_url: Mapped[str] = mapped_column(Text, default="")
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AudioAsset(Base):
    __tablename__ = "audio_asset"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shot_id: Mapped[int] = mapped_column(Integer, ForeignKey("shot.id"), index=True)
    type: Mapped[str] = mapped_column(String(16), default="voice")  # voice/bgm/sfx
    character_id: Mapped[int] = mapped_column(Integer, default=0)
    asset_url: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FinalVideo(Base):
    __tablename__ = "final_video"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project.id"), index=True)
    episode_no: Mapped[int] = mapped_column(Integer, default=1)
    url: Mapped[str] = mapped_column(Text, default="")
    platform_versions: Mapped[list] = mapped_column(JSON, default=list)
    ai_labeled: Mapped[bool] = mapped_column(default=True)   # AI 生成标识（强制）
    audit_status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/pass/reject/skipped
    cost_total: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CostLog(Base):
    __tablename__ = "cost_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project.id"), index=True)
    module: Mapped[str] = mapped_column(String(32))       # novel/script/shot/character/keyframe/video/audio/render
    vendor: Mapped[str] = mapped_column(String(32), default="")
    model: Mapped[str] = mapped_column(String(64), default="")
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AIRequest(Base):
    """确认闸口（5.0.1 / 6.2）：所有 AI 请求先复述需求 + 成本预估，确认后才执行。"""
    __tablename__ = "ai_request"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project.id"), index=True, default=0)
    module: Mapped[str] = mapped_column(String(32))        # novel/script/shot/character/keyframe/video/audio
    intent: Mapped[str] = mapped_column(Text, default="")  # 意图复述
    params_json: Mapped[dict] = mapped_column(JSON, default=dict)  # 参数摘要
    cost_estimate: Mapped[dict] = mapped_column(JSON, default=dict)  # 成本预估 {min,max,desc}
    status: Mapped[str] = mapped_column(String(16), default="draft")  # draft/confirmed/rejected/bypassed/timeout/cancelled
    confirm_round: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
