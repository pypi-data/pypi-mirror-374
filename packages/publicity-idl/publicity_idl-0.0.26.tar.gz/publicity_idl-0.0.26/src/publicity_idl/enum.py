import enum

class SourceEnum(enum.Enum):
    Douyin = "douyin"
    Toutiao = "toutiao"
    Weibo = "weibo"
    Wechat = "wechat"
    SouthWeekend = "south_weekend"

class ContextField(enum.Enum):
    Batch = "batch"
    Source = "source"
    Keyword = "keyword"
    Event = "event"
    Record = "record"
    User = "user"
    PushConfig = "push_config"
    PushConfigKeyword = "push_config_keyword"
    SourceKeywordOffset = "source_keyword_offset"
    MysqlTable = "mysql_table"

class MysqlTable(enum.Enum):
    Batch = "batch"
    Source = "source"
    Keyword = "keyword"
    Event = "event"
    Record = "record"
    User = "user"
    PushConfig = "push_config"
    PushConfigKeyword = "push_config_keyword"
    SourceKeywordOffset = "source_keyword_offset"
    ProxyUsage = "proxy_usage"

class WebDriverType(enum.Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
