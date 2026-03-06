# 此插件代码完全使用Opencode的Minimax M2.5模型AI生成

# NoneBot2 每日新闻插件

定时获取每日新闻并以图片形式发送到指定QQ群，支持 OneBot V11 协议。

## 功能特性

- 定时自动推送每日新闻
- 支持 RSS 订阅源和 NewsAPI
- 自动生成新闻图片
- 支持多个QQ群推送
- 支持配置新闻数量、分类、国家

## 安装

### 源码安装

请先创建好python虚拟环境

```bash
git clone https://github.com/WesternLi/nonebot-plugin-dailynews.git
cd nonebot-plugin-dailynews
pip install nonebot2[fastapi]
nb adapter install nonebot-adapter-onebot
pip install -e .
```

## 配置

在 `.env` 文件中修改以下配置：

```env
# 必填：接收新闻的QQ群号列表，用逗号分隔
DAILYNEWS_GROUPS=[123456789, 987654321]

# 发送时间，格式：HH:MM（24小时制）
DAILYNEWS_TIME=08:00

# 每日新闻条数
DAILYNEWS_COUNT=10

# 新闻国家代码：cn（中国）、us（美国）、jp（日本）等
DAILYNEWS_COUNTRY=cn

# 新闻分类：general（综合）、business（商业）、technology（科技）、
#          sports（体育）、entertainment（娱乐）、health（健康）、
#          science（科学）
DAILYNEWS_CATEGORY=general

# 可选：NewsAPI 密钥
# 免费版每天 100 次请求
# 申请地址：https://newsapi.org/register
DAILYNEWS_API_KEY=

# 注意：由于谷歌新闻RSS可能访问不稳定，如需自定义新闻RSS源请在 config.py 中修改 DEFAULT_RSS_URLS
```

## 使用

1. 配置完成后，重启 NoneBot
2. 插件会在启动时自动创建定时任务
3. 每天在指定时间自动发送新闻图片到配置的QQ群

### 使用命令

```
/news - 手动获取新闻
/news_test - 查看定时任务状态
/news_init - 初始化定时任务（首次使用需发送指令开启定时推送）
```

发送后会先回复"正在获取新闻，请稍候..."，然后发送新闻图片。

## 依赖

- nonebot2 >= 2.0.0
- httpx >= 0.27.0
- pillow >= 10.0.0
- apscheduler >= 3.10.0
- pydantic >= 2.0.0

## 注意事项

1. 群号需要在 `DAILYNEWS_GROUPS` 中正确配置
2. 如使用 NewsAPI，请申请密钥以获得更好的体验
3. 默认使用 Google News RSS 源

## 许可证

MIT License
