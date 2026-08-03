"""Pydantic 模式定义（API 请求/响应）。"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


# ---------- Auth ----------
class RegisterIn(BaseModel):
    phone: str
    password: str
    plan: str = "personal"


class LoginIn(BaseModel):
    phone: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    phone: str
    role: str
    plan: str
    budget_limit: float
    gate_setting: dict = {}
    class Config:
        from_attributes = True


# ---------- 通用 ----------
class Msg(BaseModel):
    message: str


class CostEstimate(BaseModel):
    min: float = 0.0
    max: float = 0.0
    desc: str = ""


# ---------- 确认闸口 ----------
class AIRequestCreate(BaseModel):
    module: str
    project_id: int = 0
    intent: str
    params: dict = {}
    cost_estimate: CostEstimate = CostEstimate()


class AIRequestOut(BaseModel):
    id: int
    module: str
    intent: str
    params_json: dict = {}
    cost_estimate: dict = {}
    status: str
    confirm_round: int = 0
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True


class ConfirmIn(BaseModel):
    action: str  # confirm / reject
    edit_note: str = ""


# ---------- 项目 ----------
class ProjectIn(BaseModel):
    name: str
    genre: str = ""
    style_desc: str = ""
    target_platform: str = "douyin"
    budget_limit: float = 5000.0
    ip_source: str = ""


class ProjectOut(BaseModel):
    id: int
    name: str
    genre: str
    style_id: str
    style_desc: str
    target_platform: str
    status: str
    budget_limit: float
    ip_source: str
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ---------- 小说 ----------
class NovelGenerateIn(BaseModel):
    genre: str
    premise: str = ""
    hero: str = ""          # 主角人设
    chapter_count: int = 3
    title: str = ""


class NovelOut(BaseModel):
    id: int
    project_id: int
    title: str
    genre: str
    outline: list = []
    chapters: list = []
    characters: list = []
    settings: list = []
    status: str
    class Config:
        from_attributes = True


# ---------- 剧本 ----------
class ScriptConvertIn(BaseModel):
    novel_id: int


class ScriptOut(BaseModel):
    id: int
    novel_id: int
    project_id: int
    scenes: list = []
    emotion_curve: list = []
    status: str
    class Config:
        from_attributes = True


# ---------- 分镜 ----------
class ShotOut(BaseModel):
    id: int
    script_id: int
    project_id: int
    shot_no: int
    shot_type: str
    camera_move: str
    duration: float
    scene_desc: str
    prompt_zh: str
    dialogue: str
    narration: str
    transition: str
    char_ref_ids: list = []
    style_id: str
    status: str
    class Config:
        from_attributes = True


class ShotUpdateIn(BaseModel):
    shot_type: str = ""
    camera_move: str = ""
    duration: float = 0
    scene_desc: str = ""
    prompt_zh: str = ""
    dialogue: str = ""
    narration: str = ""
    transition: str = ""
    shot_no: int = 0


# ---------- 角色 ----------
class LibraryIn(BaseModel):
    name: str
    desc: str = ""
    project_ids: list = []


class CharacterIn(BaseModel):
    library_id: int
    name: str
    desc: str = ""


class CharacterOut(BaseModel):
    id: int
    library_id: int
    name: str
    desc: str
    ref_images: list = []
    expression_set: list = []
    lora_version: str
    class Config:
        from_attributes = True


class LibraryOut(BaseModel):
    id: int
    name: str
    desc: str
    project_ids: list = []
    is_shared: bool
    class Config:
        from_attributes = True


# ---------- 关键帧 ----------
class KeyframeOut(BaseModel):
    id: int
    shot_id: int
    image_url: str
    score: float
    is_approved: bool
    class Config:
        from_attributes = True


# ---------- 视频 ----------
class VideoTaskOut(BaseModel):
    id: int
    shot_id: int
    vendor: str
    model: str
    status: str
    result_url: str
    cost: float
    retry_count: int
    class Config:
        from_attributes = True


# ---------- 成片 ----------
class RenderIn(BaseModel):
    project_id: int
    episode_no: int = 1
    enable_audit: bool = False   # M13 合规检验（用户可选）


class FinalVideoOut(BaseModel):
    id: int
    project_id: int
    episode_no: int
    url: str
    platform_versions: list = []
    ai_labeled: bool
    audit_status: str
    cost_total: float
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ---------- 成本 ----------
class CostLogOut(BaseModel):
    id: int
    project_id: int
    module: str
    vendor: str
    model: str
    tokens: int
    duration: float
    amount: float
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True
