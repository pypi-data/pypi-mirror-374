#!/usr/bin/python
# -*- coding:UTF-8 -*-

PROJECT_NAME = 'baidu_spider'

CONCURRENCY = 30

MAX_RUNNING_SPIDERS = 8

USE_SESSION = True

# 下载延迟
DOWNLOAD_DELAY = 0.1
RANDOMNESS = False

# --------------------------------------------------- 公共MySQL配置 -----------------------------------------------------
MYSQL_HOST = '43.139.14.225'
MYSQL_PORT = 3306
MYSQL_USER = 'picker'
MYSQL_PASSWORD = 'kmcNbbz6TbSihttZ'
MYSQL_DB = 'stock_pro'
MYSQL_TABLE = 'articles'  # 可选，默认使用spider名称
MYSQL_BATCH_SIZE = 500

# asyncmy专属配置
MYSQL_POOL_MIN = 5  # 连接池最小连接数
MYSQL_POOL_MAX = 20  # 连接池最大连接数

# 选择下载器
DOWNLOADER = "crawlo.downloader.httpx_downloader.HttpXDownloader"
# DOWNLOADER = "crawlo.downloader.cffi_downloader.CurlCffiDownloader"

# MIDDLEWARES = [
#     'crawlo.middleware.download_delay.DownloadDelayMiddleware',
#     'crawlo.middleware.default_header.DefaultHeaderMiddleware',
#     'crawlo.middleware.response_filter.ResponseFilterMiddleware',
#     'crawlo.middleware.retry.RetryMiddleware',
#     'crawlo.middleware.response_code.ResponseCodeMiddleware',
#     'crawlo.middleware.request_ignore.RequestIgnoreMiddleware',
# ]

EXTENSIONS = [
    'crawlo.extension.log_interval.LogIntervalExtension',
    'crawlo.extension.log_stats.LogStats',
]

PIPELINES = [
    'crawlo.pipelines.console_pipeline.ConsolePipeline',
    # 'crawlo.pipelines.mysql_pipeline.AsyncmyMySQLPipeline',  # 或 AiomysqlMySQLPipeline
    # 'crawlo.pipelines.mysql_batch_pipline.AsyncmyMySQLPipeline',  # 或 AiomysqlMySQLPipeline
    # 'baidu_spider.pipeline.TestPipeline',
    # 'baidu_spider.pipeline.MongoPipeline',
]

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
DEFAULT_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

# --------------------------------------DB ---------------------------------------------
Mongo_Params = ''
MONGODB_DB = 'news'

REDIS_TTL = 0
CLEANUP_FP = False

LOG_LEVEL = 'DEBUG'

FILTER_CLASS = 'crawlo.filters.aioredis_filter.AioRedisFilter'
# FILTER_CLASS = 'crawlo.filters.redis_filter.RedisFilter'
# FILTER_CLASS = 'crawlo.filters.memory_filter.MemoryFileFilter'

# PROXY_POOL_API = 'http://123.56.42.142:5000/proxy/getitem/'
#
# PROXY_FETCH_FUNC = "crawlo.utils.proxy.get_proxies"


# PROXY_ENABLED = True
#
# # 使用 API 提供者
# PROXY_PROVIDERS = [
#     {
#         'class': 'crawlo.proxy.providers.APIProxyProvider',
#         'config': {
#             'url': 'http://123.56.42.142:5000/proxy/getitem/',
#             'method': 'GET',
#             'timeout': 10.0
#         }
#     }
# ]
#
# # 代理选择策略：使用最少的代理（避免单 IP 过载）
# PROXY_SELECTION_STRATEGY = 'least_used'
#
# # 请求延迟：0.5~1.5 秒，避免请求过快
# PROXY_REQUEST_DELAY_ENABLED = True
# PROXY_REQUEST_DELAY = 1.0
#
# # 健康检查
# PROXY_HEALTH_CHECK_ENABLED = True
# PROXY_HEALTH_CHECK_INTERVAL = 10  # 每 5 分钟检查一次
#
# # 代理池更新
# PROXY_POOL_UPDATE_INTERVAL = 5  # 每 5 分钟从 API 拉取新代理
#
# # 失败处理
# PROXY_MAX_FAILURES = 3  # 失败 3 次后禁用代理
# PROXY_COOLDOWN_PERIOD = 600  # 禁用 10 分钟后恢复
# PROXY_MAX_RETRY_COUNT = 2  # 每个请求最多重试 2 次