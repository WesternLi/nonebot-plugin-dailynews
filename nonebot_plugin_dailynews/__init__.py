import base64
import nonebot
from datetime import datetime
from nonebot import get_plugin_config, logger, on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Bot, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Event

from .config import DailyNewsConfig
from .news_fetcher import NewsFetcher
from .image_generator import ImageGenerator


__plugin_meta__ = PluginMetadata(
    name="每日新闻",
    description="定时获取每日新闻并发送到QQ群",
    usage="配置后自动定时发送新闻图片到指定群",
    config=DailyNewsConfig,
)


scheduler: AsyncIOScheduler | None = None

news_cmd = on_command("news", block=True, priority=5)
test_cmd = on_command("news_test", block=True, priority=5)
init_cmd = on_command("news_init", block=True, priority=100)


@init_cmd.handle()
async def handle_init(bot: Bot, event: Event):
    global scheduler
    if scheduler is not None:
        await bot.send(event, f"定时任务已初始化，任务数: {len(scheduler.get_jobs())}")
        return
    
    try:
        config = get_plugin_config(DailyNewsConfig)
    except Exception as e:
        await bot.send(event, f"获取配置失败: {e}")
        return
    
    logger.info(f"正在设置定时任务，时间: {config.dailynews_time}")
    
    scheduler = AsyncIOScheduler()
    hour, minute = map(int, config.dailynews_time.split(":"))
    scheduler.add_job(
        send_news_to_groups,
        "cron",
        hour=hour,
        minute=minute,
        id="daily_news",
    )
    scheduler.start()
    logger.info(f"每日新闻定时任务已设置: {config.dailynews_time}")
    logger.info(f"当前时间: {datetime.now().strftime('%H:%M')}")
    await bot.send(event, f"定时任务初始化成功！时间: {config.dailynews_time}")


@test_cmd.handle()
async def handle_test(bot: Bot, event: GroupMessageEvent):
    global scheduler
    if scheduler:
        jobs = scheduler.get_jobs()
        await bot.send(event, f"定时任务数量: {len(jobs)}\n当前时间: {datetime.now().strftime('%H:%M')}")
    else:
        await bot.send(event, "定时任务未初始化，请发送 /news_init 初始化")


@news_cmd.handle()
async def handle_news(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    
    logger.info(f"群 {group_id} 手动请求新闻")
    
    await bot.send(event, "正在获取新闻，请稍候...")
    
    config = get_plugin_config(DailyNewsConfig)
    
    fetcher = NewsFetcher(
        rss_urls=config.dailynews_rss_urls,
        api_key=config.dailynews_api_key,
        country=config.dailynews_country,
        category=config.dailynews_category,
        count=config.dailynews_count,
    )

    try:
        news_items = await fetcher.fetch_news()
        if not news_items:
            await bot.send(event, "未获取到新闻内容")
            return
    except Exception as e:
        logger.error(f"获取新闻失败: {e}")
        await bot.send(event, f"获取新闻失败: {e}")
        return

    logger.info(f"获取到 {len(news_items)} 条新闻")

    generator = ImageGenerator()
    try:
        image_buffer = generator.generate_news_image(news_items)
    except Exception as e:
        logger.error(f"生成图片失败: {e}")
        await bot.send(event, f"生成图片失败: {e}")
        return

    try:
        image_data = base64.b64encode(image_buffer.getvalue()).decode()
        await bot.call_api(
            "send_group_msg",
            group_id=group_id,
            message=[
                {"type": "image", "data": {"file": f"base64://{image_data}"}}
            ]
        )
        logger.info(f"新闻已发送到群 {group_id}")
    except Exception as e:
        logger.error(f"发送新闻到群 {group_id} 失败: {e}")
        await bot.send(event, f"发送失败: {e}")


async def send_news_to_groups():
    logger.info("定时任务触发！")
    try:
        bot = nonebot.get_bot()
    except Exception as e:
        logger.error(f"获取Bot实例失败: {e}")
        return
    
    config = get_plugin_config(DailyNewsConfig)
    if not config.dailynews_groups:
        logger.warning("未配置接收新闻的QQ群")
        return

    logger.info("开始获取每日新闻...")
    fetcher = NewsFetcher(
        rss_urls=config.dailynews_rss_urls,
        api_key=config.dailynews_api_key,
        country=config.dailynews_country,
        category=config.dailynews_category,
        count=config.dailynews_count,
    )

    try:
        news_items = await fetcher.fetch_news()
        if not news_items:
            logger.warning("未获取到新闻内容")
            return
    except Exception as e:
        logger.error(f"获取新闻失败: {e}")
        return

    logger.info(f"获取到 {len(news_items)} 条新闻")

    generator = ImageGenerator()
    try:
        image_buffer = generator.generate_news_image(news_items)
    except Exception as e:
        logger.error(f"生成图片失败: {e}")
        return

    for group_id in config.dailynews_groups:
        try:
            image_data = base64.b64encode(image_buffer.getvalue()).decode()
            await bot.call_api(
                "send_group_msg",
                group_id=group_id,
                message=[
                    {"type": "image", "data": {"file": f"base64://{image_data}"}}
                ]
            )
            logger.info(f"新闻已发送到群 {group_id}")
        except Exception as e:
            logger.error(f"发送新闻到群 {group_id} 失败: {e}")


def _load():
    logger.info("每日新闻插件已加载，请发送 /news_init 初始化定时任务")


__all__ = ["_load"]
