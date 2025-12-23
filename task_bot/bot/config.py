import os
from dataclasses import dataclass

from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)

dotenv_path = os.path.join(current_dir, "..", ".env")

load_dotenv(dotenv_path=dotenv_path)


@dataclass
class BotConfig:
    token: str


@dataclass
class ApiConfig:
    base_url: str


@dataclass
class RedisConfig:
    dsn: str


@dataclass
class Config:
    bot: BotConfig
    api: ApiConfig
    redis: RedisConfig


config = Config(
    bot=BotConfig(token=os.getenv("BOT_TOKEN")),
    api=ApiConfig(base_url="http://backend:8000/api/"),
    redis=RedisConfig(dsn=os.getenv("REDIS_DSN")),
)
