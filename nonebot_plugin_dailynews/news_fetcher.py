import httpx
from xml.etree import ElementTree
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


DEFAULT_RSS_URLS = [
    "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=zh-CN&gl=CN&ceid=CN%3Azh-CN",
]


@dataclass
class NewsItem:
    title: str
    link: str
    source: str
    pub_date: Optional[str] = None
    description: Optional[str] = None


class NewsFetcher:
    def __init__(
        self,
        rss_urls: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        country: str = "cn",
        category: str = "general",
        count: int = 10,
    ):
        self.rss_urls = rss_urls if rss_urls else DEFAULT_RSS_URLS
        self.api_key = api_key
        self.country = country
        self.category = category
        self.count = count

    async def fetch_from_rss(self, url: str) -> List[NewsItem]:
        news_items = []
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                logger.info(f"正在获取RSS: {url}")
                response = await client.get(url)
                response.raise_for_status()
                content = response.content
                logger.info(f"RSS响应: {response.status_code}, 内容长度: {len(content)}")
                
                root = ElementTree.fromstring(content)
                ns = {"atom": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}
                entries = root.findall(".//item")
                logger.info(f"找到 {len(entries)} 个item")
                
                for entry in entries:
                    title = entry.findtext("title", "")
                    link = entry.findtext("link", "")
                    source = entry.findtext("dc:creator", "") or entry.findtext("source", "")
                    pub_date = entry.findtext("pubDate", "")
                    description = entry.findtext("description", "")
                    logger.info(f"解析: title={title[:20]}..., link={link[:30]}...")
                    if title and link:
                        news_items.append(NewsItem(
                            title=self._clean_html(title),
                            link=link,
                            source=source or "Unknown",
                            pub_date=pub_date,
                            description=self._clean_html(description) if description else None,
                        ))
                logger.info(f"成功解析 {len(news_items)} 条新闻")
        except Exception as e:
            logger.error(f"获取RSS失败 {url}: {e}")
        return news_items

    async def fetch_from_newsapi(self) -> List[NewsItem]:
        if not self.api_key:
            return []
        url = f"https://newsapi.org/v2/top-headlines?country={self.country}&category={self.category}&pageSize={self.count}&apiKey={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return [
                    NewsItem(
                        title=article.get("title", ""),
                        link=article.get("url", ""),
                        source=article.get("source", {}).get("name", "Unknown"),
                        description=article.get("description"),
                    )
                    for article in data.get("articles", [])
                ]
        except Exception:
            return []

    async def fetch_news(self) -> List[NewsItem]:
        logger.info(f"开始获取新闻，RSS URL数量: {len(self.rss_urls)}")
        all_news = []
        if self.api_key:
            api_news = await self.fetch_from_newsapi()
            all_news.extend(api_news)
        for rss_url in self.rss_urls:
            logger.info(f"处理RSS: {rss_url}")
            rss_news = await self.fetch_from_rss(rss_url)
            logger.info(f"从 {rss_url} 获取到 {len(rss_news)} 条")
            all_news.extend(rss_news)
        logger.info(f"共获取 {len(all_news)} 条新闻")
        seen = set()
        unique_news = []
        for news in all_news:
            if news.title not in seen:
                seen.add(news.title)
                unique_news.append(news)
        logger.info(f"去重后 {len(unique_news)} 条")
        return unique_news[:self.count]

    def _clean_html(self, text: str) -> str:
        import re
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"&lt;", "<", text)
        text = re.sub(r"&gt;", ">", text)
        text = re.sub(r"&quot;", '"', text)
        return text.strip()
