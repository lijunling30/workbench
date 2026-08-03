"""全局配置：读取 .env，支持 DeepSeek 真实调用与 Mock 演示两种模式。"""
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "漫镜工场 ManJu Studio API"
    api_prefix: str = "/api"

    # 数据库
    database_url: str = f"sqlite:///{BASE_DIR / 'manju.db'}"

    # JWT
    jwt_secret: str = "manju-studio-dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    # AI 模型网关
    # ai_mode: real=真实调用 DeepSeek；mock=本地模拟（无 key 时演示全流程）
    ai_mode: str = "mock"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    # 成本模型（单位：元）
    cost_per_1k_tokens: float = 0.001  # 文本 token 单价
    cost_per_image: float = 0.30       # 关键帧单张
    cost_per_second_video: float = 0.50  # 视频每秒

    # 确认闸口
    gate_high_cost_threshold: float = 50.0   # 单次 >=50 元强制确认
    gate_batch_threshold: int = 20            # 批量 >=20 镜头强制确认

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"


settings = Settings()
