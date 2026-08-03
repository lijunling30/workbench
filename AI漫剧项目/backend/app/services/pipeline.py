"""生成流水线执行器：确认闸口确认后，按模块执行真实/Mock 生成并记账。"""
from datetime import datetime

from sqlalchemy.orm import Session

from ..models import (
    AudioAsset, Character, FinalVideo, Keyframe, Novel, Script, Shot, User, VideoTask,
)
from . import ai_gateway, cost


def execute_novel(db: Session, user: User, project_id: int, params: dict) -> Novel:
    genre = params.get("genre", "")
    premise = params.get("premise", "")
    hero = params.get("hero", "")
    chapter_count = int(params.get("chapter_count", 3) or 3)
    title = params.get("title", f"{genre or '漫剧'}·未命名作品")

    import asyncio
    result = asyncio.run(ai_gateway.generate_novel(genre, premise, hero, chapter_count))

    novel = Novel(
        project_id=project_id, title=title, genre=genre, premise=premise,
        outline=result.get("outline", []), chapters=result.get("chapters", []),
        characters=result.get("characters", []), settings=result.get("settings", []),
        status="done",
    )
    db.add(novel)
    db.commit()
    db.refresh(novel)

    # 记账
    tokens = 0
    for ch in novel.chapters:
        tokens += len(ch.get("content", ""))
    cost.record_cost(db, user, project_id, "novel", "deepseek", "deepseek-chat",
                     tokens=tokens, amount=cost.text_cost(tokens))
    return novel


def execute_script(db: Session, user: User, novel_id: int) -> Script:
    novel = db.get(Novel, novel_id)
    if not novel:
        raise ValueError("小说不存在")

    import asyncio
    result = asyncio.run(ai_gateway.generate_script({
        "chapters": novel.chapters, "characters": novel.characters, "settings": novel.settings,
    }))

    script = Script(
        novel_id=novel.id, project_id=novel.project_id,
        scenes=result.get("scenes", []), emotion_curve=result.get("emotion_curve", []),
        status="done",
    )
    db.add(script)
    db.commit()
    db.refresh(script)

    tokens = len(str(result))
    cost.record_cost(db, user, novel.project_id, "script", "deepseek", "deepseek-chat",
                     tokens=tokens, amount=cost.text_cost(tokens))
    return script


def execute_shots(db: Session, user: User, script_id: int) -> list[Shot]:
    script = db.get(Script, script_id)
    if not script:
        raise ValueError("剧本不存在")

    import asyncio
    style = ""
    from ..models import Project
    p = db.get(Project, script.project_id)
    if p:
        style = p.style_desc
    raw_shots = asyncio.run(ai_gateway.generate_shots(
        {"scenes": script.scenes, "emotion_curve": script.emotion_curve}, style))

    shots = []
    for i, s in enumerate(raw_shots):
        shot = Shot(
            script_id=script.id, project_id=script.project_id,
            shot_no=s.get("shot_no", i + 1),
            shot_type=s.get("shot_type", "中景"),
            camera_move=s.get("camera_move", "固定"),
            duration=float(s.get("duration", 5.0)),
            scene_desc=s.get("scene_desc", ""),
            prompt_zh=s.get("prompt_zh", ""),
            dialogue=s.get("dialogue", ""),
            narration=s.get("narration", ""),
            transition=s.get("transition", "硬切"),
            char_ref_ids=s.get("char_ref_ids", []),
            style_id=s.get("style_id", "style-01"),
            status="draft",
        )
        db.add(shot)
        shots.append(shot)
    db.commit()
    for s in shots:
        db.refresh(s)

    tokens = len(str(raw_shots))
    cost.record_cost(db, user, script.project_id, "shot", "deepseek", "deepseek-chat",
                     tokens=tokens, amount=cost.text_cost(tokens))
    return shots


def execute_character_images(db: Session, user: User, character_id: int) -> Character:
    ch = db.get(Character, character_id)
    if not ch:
        raise ValueError("角色不存在")

    import asyncio
    images = asyncio.run(ai_gateway.generate_character_images(ch.desc, 3))
    ch.ref_images = images
    db.commit()
    db.refresh(ch)

    cost.record_cost(db, user, 0, "character", "mock", "wanzhi", amount=cost.image_cost(3))
    return ch


def execute_keyframes(db: Session, user: User, shot_id: int, n: int = 3) -> list[Keyframe]:
    shot = db.get(Shot, shot_id)
    if not shot:
        raise ValueError("分镜不存在")

    import asyncio
    candidates = asyncio.run(ai_gateway.generate_keyframes(shot.prompt_zh, n))

    kfs = []
    for c in candidates:
        kf = Keyframe(shot_id=shot.id, image_url=c["image_url"],
                      prompt=c.get("prompt", ""), score=c.get("score", 0), is_approved=False)
        db.add(kf)
        kfs.append(kf)
    db.commit()
    for k in kfs:
        db.refresh(k)

    shot.status = "keyframed"
    db.commit()

    cost.record_cost(db, user, shot.project_id, "keyframe", "mock", "wanzhi",
                     amount=cost.image_cost(len(kfs)))
    return kfs


def execute_video(db: Session, user: User, shot_id: int, keyframe_id: int | None = None,
                  vendor: str = "vidu") -> VideoTask:
    shot = db.get(Shot, shot_id)
    if not shot:
        raise ValueError("分镜不存在")

    task = VideoTask(
        shot_id=shot.id, keyframe_id=keyframe_id or 0, vendor=vendor, model="Q3",
        status="queued", cost=0.0,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # 演示：同步模拟完成（真实环境为异步任务）
    url = ai_gateway._mock_video({}, shot.duration)
    task.status = "success"
    task.result_url = url
    task.cost = cost.video_cost(shot.duration)
    db.commit()
    db.refresh(task)

    shot.status = "video_ready"
    db.commit()

    cost.record_cost(db, user, shot.project_id, "video", vendor, "Q3",
                     duration=shot.duration, amount=task.cost)
    return task


def execute_audio(db: Session, user: User, shot_id: int, type_: str = "voice") -> AudioAsset:
    shot = db.get(Shot, shot_id)
    if not shot:
        raise ValueError("分镜不存在")
    asset = AudioAsset(shot_id=shot.id, type=type_, status="done",
                       asset_url=f"/assets/mock_audio_{type_}_{shot.id}.mp3")
    db.add(asset)
    db.commit()
    db.refresh(asset)
    cost.record_cost(db, user, shot.project_id, "audio", "volcengine", "tts", amount=0.1)
    return asset


def execute_render(db: Session, user: User, project_id: int, episode_no: int = 1,
                   enable_audit: bool = False) -> FinalVideo:
    from ..services.cost import project_cost
    total = project_cost(db, project_id)
    fv = FinalVideo(
        project_id=project_id, episode_no=episode_no, ai_labeled=True,
        url=f"/assets/final_video_p{project_id}_e{episode_no}.mp4",
        platform_versions=[
            {"platform": "douyin", "resolution": "1080x1920", "url": f"/assets/final_douyin_p{project_id}.mp4"},
            {"platform": "bilibili", "resolution": "1920x1080", "url": f"/assets/final_bili_p{project_id}.mp4"},
        ],
        audit_status="passed" if enable_audit else "skipped",
        cost_total=total,
    )
    db.add(fv)
    db.commit()
    db.refresh(fv)

    cost.record_cost(db, user, project_id, "render", "ffmpeg", "ffmpeg", amount=0.5)
    return fv
