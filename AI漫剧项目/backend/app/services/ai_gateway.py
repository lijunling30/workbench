"""L4 AI 模型网关：统一封装大模型调用。

- ai_mode=mock：本地生成示例内容，零成本演示全流程；
- ai_mode=real：调用 DeepSeek（OpenAI 兼容接口）真实生成。
禁止业务层直连厂商，一切 AI 调用经过本网关。
"""
import json
import time
from typing import Any

import httpx

from ..config import settings


class AIError(Exception):
    pass


# ---------------------------------------------------------------- DeepSeek
async def deepseek_chat(messages: list, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """调用 DeepSeek，返回文本。"""
    url = f"{settings.deepseek_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(url, json=payload, headers=headers)
    if resp.status_code != 200:
        raise AIError(f"DeepSeek 调用失败: {resp.status_code} {resp.text[:200]}")
    data = resp.json()
    return data["choices"][0]["message"]["content"]


async def deepseek_json(messages: list, temperature: float = 0.4) -> dict:
    """调用 DeepSeek 并要求返回 JSON（JSON Schema 约束）。"""
    content = await deepseek_chat(messages + [{"role": "system", "content": "你只输出合法的 JSON，不要输出任何其他文字。"}],
                                  temperature=temperature)
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(content)


# ---------------------------------------------------------------- Mock 生成
def _mock_novel(genre: str, premise: str, hero: str, chapter_count: int) -> dict:
    """本地生成示例小说（结构完整，便于演示）。"""
    g = genre or "都市异能"
    p = premise or f"少年意外觉醒{g}能力，卷入城市暗流，在对抗与成长中揭开身世之谜。"
    h = hero or "林默，20 岁，外表冷静内心炽热，拥有读取记忆的异能"
    chapters = []
    for i in range(1, chapter_count + 1):
        chapters.append({
            "no": i,
            "title": f"第{i}章 · 命运的开端",
            "content": f"（{g}题材示例章节 {i}）{h}。{p}\n\n夜色笼罩城市，林默站在天台边缘，指尖闪过一缕微光。他深吸一口气，踏入了这场本不属于他的风暴……",
        })
    return {
        "outline": [{"no": i, "title": f"第{i}章 · 命运的开端", "summary": f"推进主线：{p}"} for i in range(1, chapter_count + 1)],
        "chapters": chapters,
        "characters": [
            {"name": "林默", "role": "主角", "desc": "20 岁，冷静寡言，拥有记忆读取异能，背负身世谜团"},
            {"name": "苏晚", "role": "女主", "desc": "19 岁，活泼直率，隐藏身份的组织成员"},
        ],
        "settings": [
            {"name": f"{g}世界观", "desc": "现代都市背景，异能者与普通人类共存，暗处存在监管组织"},
        ],
    }


def _mock_script(novel: dict) -> dict:
    """小说 -> 剧本（场景/对白/情绪）。"""
    scenes = []
    for ch in novel.get("chapters", [])[:3]:
        scenes.append({
            "no": len(scenes) + 1,
            "location": "城市天台·夜",
            "emotion": "紧张",
            "narration": ch.get("content", "")[:120],
            "action": "林默抬手，掌心微光浮现",
            "dialogue": [
                {"character": "林默", "line": "苏晚，这一切究竟是怎么回事？"},
                {"character": "苏晚", "line": "你还不明白吗？你根本不是普通人。"},
            ],
        })
    return {
        "scenes": scenes,
        "emotion_curve": [{"scene_no": s["no"], "emotion": s["emotion"]} for s in scenes],
    }


def _mock_shots(script: dict) -> list:
    """剧本 -> 分镜（纯中文提示词 + 角色引用 ID）。"""
    shots = []
    shot_types = ["特写", "近景", "中景", "远景"]
    moves = ["推", "拉", "摇", "移", "固定"]
    for si, scene in enumerate(script.get("scenes", []), start=1):
        for j in range(1, 4):  # 每场 3 个镜头
            st = shot_types[(si + j) % 4]
            mv = moves[(si * j) % 5]
            dialogue = scene["dialogue"][j - 1]["line"] if j <= len(scene.get("dialogue", [])) else ""
            shots.append({
                "shot_no": len(shots) + 1,
                "shot_type": st,
                "camera_move": mv,
                "duration": 5.0,
                "scene_desc": scene["location"],
                "dialogue": dialogue,
                "narration": scene["narration"][:40],
                "transition": "硬切",
                "prompt_zh": f"【{st}·{mv}】{scene['location']}，{dialogue or scene['action']}，画风为日系赛璐璐漫剧风格，构图精致，光影电影感。[CHAR:01]",
                "char_ref_ids": ["CHAR:01"],
                "style_id": "style-01",
            })
    return shots


def _mock_keyframe(shot_prompt: str, n: int = 3) -> list:
    """关键帧候选（生成 SVG 占位图，浏览器可直接显示）。"""
    imgs = []
    for i in range(n):
        svg = _svg_frame(shot_prompt[:24], i + 1)
        imgs.append({
            "image_url": f"data:image/svg+xml;utf8,{svg}",
            "score": round(80 + (i * 7) % 19, 1),
            "prompt": shot_prompt,
        })
    return imgs


def _svg_frame(label: str, idx: int) -> str:
    """生成一张暗色影院感的 SVG 占位关键帧。"""
    colors = ["#1f2937", "#111827", "#312e81"]
    c = colors[idx % 3]
    import urllib.parse
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640">
  <rect width="360" height="640" fill="{c}"/>
  <rect x="18" y="18" width="324" height="604" rx="12" fill="none" stroke="rgba(127,119,221,0.6)" stroke-width="2"/>
  <circle cx="180" cy="220" r="70" fill="rgba(127,119,221,0.25)"/>
  <rect x="130" y="300" width="100" height="120" rx="14" fill="rgba(29,158,117,0.35)"/>
  <circle cx="300" cy="120" r="28" fill="rgba(255,255,255,0.15)"/>
  <text x="180" y="500" text-anchor="middle" fill="rgba(255,255,255,0.85)" font-size="18" font-family="sans-serif">{label}</text>
  <text x="180" y="530" text-anchor="middle" fill="rgba(127,119,221,0.9)" font-size="14" font-family="monospace">候选 {idx} · KEYFRAME</text>
</svg>'''
    return urllib.parse.quote(svg)


def _mock_video(keyframe: dict, duration: float) -> str:
    """视频任务占位结果（返回一段黑场 mp4 链接占位）。"""
    return f"/assets/mock_video_{int(time.time())}.mp4"


# ---------------------------------------------------------------- 统一入口
def use_mock() -> bool:
    return settings.ai_mode == "mock" or not settings.deepseek_api_key


async def generate_novel(genre: str, premise: str, hero: str, chapter_count: int) -> dict:
    """生成小说。"""
    if use_mock():
        return _mock_novel(genre, premise, hero, chapter_count)
    prompt = (
        f"请创作一部{genre or '都市'}题材的短篇小说，主角：{hero or '林默'}。\n"
        f"设定：{premise or '少年觉醒异能，卷入城市暗流。'}\n"
        f"共 {chapter_count} 章。输出 JSON：{{outline:[{{no,title,summary}}],chapters:[{{no,title,content}}],characters:[{{name,role,desc}}],settings:[{{name,desc}}]}}"
    )
    return await deepseek_json([{"role": "user", "content": prompt}])


async def generate_script(novel: dict) -> dict:
    """小说 -> 剧本。"""
    if use_mock():
        return _mock_script(novel)
    text = json.dumps(novel, ensure_ascii=False)
    prompt = (
        f"将以下小说转为剧本 JSON：{{scenes:[{{no,location,emotion,narration,action,dialogue:[{{character,line}}]}}],emotion_curve:[{{scene_no,emotion}}]}}\n"
        f"小说：{text[:8000]}"
    )
    return await deepseek_json([{"role": "user", "content": prompt}])


async def generate_shots(script: dict, style_desc: str = "") -> list:
    """剧本 -> 分镜表（纯中文提示词，强制角色引用 ID）。"""
    if use_mock():
        return _mock_shots(script)
    text = json.dumps(script, ensure_ascii=False)
    prompt = (
        f"将剧本拆解为分镜镜头 JSON 数组：[{{shot_no,shot_type,camera_move,duration,scene_desc,prompt_zh,dialogue,narration,transition,char_ref_ids,style_id}}]。\n"
        f"要求：prompt_zh 用纯中文画面提示词并强制携带角色引用 [CHAR:01]；景别含特写/近景/中景/远景；运镜含推/拉/摇/移。\n"
        f"画风参考：{style_desc or '日系赛璐璐漫剧风格，电影感光影'}。\n剧本：{text[:8000]}"
    )
    return await deepseek_json([{"role": "user", "content": prompt}])


async def generate_character_images(character_desc: str, n: int = 3) -> list:
    """角色形象（三视图占位/接入真实文生图）。"""
    if use_mock():
        return _svg_frames(f"角色: {character_desc[:16]}", n)
    raise AIError("角色文生图需配置即梦/通义万相 API（当前仅支持 Mock）")


def _svg_frames(label: str, n: int) -> list:
    return [f"data:image/svg+xml;utf8,{_svg_frame(label, i + 1)}" for i in range(n)]


async def generate_keyframes(shot_prompt: str, n: int = 3) -> list:
    """关键帧抽卡（候选生成 + AI 评分）。"""
    if use_mock():
        return _mock_keyframe(shot_prompt, n)
    raise AIError("关键帧生图需配置即梦/通义万相 API（当前仅支持 Mock）")


async def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 2)
