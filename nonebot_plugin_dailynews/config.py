from pydantic import BaseModel, Field
from typing import List


DEFAULT_RSS_URLS = [
    "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=zh-CN&gl=CN&ceid=CN%3Azh-CN",
]


class DailyNewsConfig(BaseModel):
    dailynews_groups: List[int] = Field(
        default_factory=list,
        description="接收每日新闻的QQ群号列表",
    )
    dailynews_time: str = Field(
        default="08:00",
        description="每日发送时间，格式: HH:MM",
    )
    dailynews_count: int = Field(
        default=10,
        description="每日新闻条数",
    )
    dailynews_country: str = Field(
        default="cn",
        description="新闻国家代码: cn, us, jp, etc.",
    )
    dailynews_category: str = Field(
        default="general",
        description="新闻分类: general, business, technology, sports, entertainment, health, science, etc.",
    )
    dailynews_api_key: str = Field(
        default="",
        description="新闻API密钥，为空则使用免费RSS源",
    )
    dailynews_rss_urls: List[str] = Field(
        default_factory=lambda: DEFAULT_RSS_URLS,
        description="RSS订阅源列表",
    )
