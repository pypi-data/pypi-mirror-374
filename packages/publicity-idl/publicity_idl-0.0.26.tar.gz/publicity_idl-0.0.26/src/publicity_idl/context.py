from .enum import SourceEnum, ContextField, MysqlTable
from .domain import Batch, Keyword, Event, Record, User, PushConfig, SourceKeywordOffset, PushConfigKeyword

class Context:
    def __init__(self, parent: 'Context' = None, key: ContextField = None, value: any = None):
        """
        初始化Context（类似Go的valueCtx）
        :param parent: 父Context引用（而非拷贝）
        :param key: 当前Context持有的字段键（仅一个）
        :param value: 当前Context持有的字段值
        """
        self._parent = parent  # 父Context引用，无拷贝
        self._key = key        # 当前节点的键
        self._value = value    # 当前节点的值

    @classmethod
    def background(cls) -> 'Context':
        """创建根Context（类似Go的context.Background()）"""
        return cls(parent=None, key=None, value=None)

    def _get_from_chain(self, field: ContextField) -> any:
        """沿引用链查找字段（当前没有则查父级）"""
        # 先检查当前节点是否持有该字段
        if self._key == field:
            return self._value
        # 递归查找父节点
        if self._parent is not None:
            return self._parent._get_from_chain(field)
        # 整条链都没有找到
        return None

    def _must_get(self, field: ContextField) -> any:
        """查找字段，不存在则抛出异常（类似原逻辑）"""
        value = self._get_from_chain(field)
        if value is None:
            raise KeyError(f"Field {field} not found in context chain")
        return value

    def must_get_batch(self) -> Batch:
        return self._must_get(ContextField.Batch)

    def must_get_source(self) -> SourceEnum:
        return self._must_get(ContextField.Source)

    def must_get_keyword(self) -> Keyword:
        return self._must_get(ContextField.Keyword)

    def must_get_event(self) -> Event:
        return self._must_get(ContextField.Event)

    def must_get_record(self) -> Record:
        return self._must_get(ContextField.Record)

    def must_get_user(self) -> User:
        return self._must_get(ContextField.User)

    def must_get_push_config(self) -> PushConfig:
        return self._must_get(ContextField.PushConfig)

    def must_get_push_config_keyword(self) -> PushConfigKeyword:
        return self._must_get(ContextField.PushConfigKeyword)

    def must_get_source_keyword_offset(self) -> SourceKeywordOffset:
        return self._must_get(ContextField.SourceKeywordOffset)

    def _with(self, key: ContextField, value: any) -> 'Context':
        """创建新的Context（持有当前Context为父节点），不拷贝原有数据"""
        return Context(parent=self, key=key, value=value)

    def with_source(self, source: SourceEnum) -> 'Context':
        return self._with(key=ContextField.Source, value=source)

    def with_batch(self, batch: Batch) -> 'Context':
        return self._with(key=ContextField.Batch, value=batch)

    def with_keyword(self, keyword: Keyword) -> 'Context':
        return self._with(key=ContextField.Keyword, value=keyword)

    def with_event(self, event: Event) -> 'Context':
        return self._with(key=ContextField.Event, value=event)

    def with_user(self, user: User) -> 'Context':
        return self._with(key=ContextField.User, value=user)

    def with_record(self, record: Record) -> 'Context':
        return self._with(key=ContextField.Record, value=record)

    def with_push_config(self, push_config: PushConfig) -> 'Context':
        return self._with(key=ContextField.PushConfig, value=push_config)

    def with_push_config_keyword(self, push_config_keyword: PushConfigKeyword) -> 'Context':
        return self._with(key=ContextField.PushConfigKeyword, value=push_config_keyword)

    def with_source_keyword_offset(self, source_keyword_offset: SourceKeywordOffset) -> 'Context':
        return self._with(key=ContextField.SourceKeywordOffset, value=source_keyword_offset)

    def with_mysql_table(self, table: MysqlTable) -> 'Context':
        return self._with(key=ContextField.MysqlTable, value=table)

    def __str__(self) -> str:
        """自定义字符串表示，遍历引用链收集所有字段并格式化输出"""
        # 收集所有字段（注意去重：子节点字段会覆盖父节点同名字段）
        fields = {}
        current = self
        while current is not None:
            if current._key is not None:  # 跳过根节点（background()）
                # 子节点字段覆盖父节点，所以从当前节点向根节点遍历，后添加的会被覆盖
                fields[current._key] = current._value
            current = current._parent

        # 格式化字段字符串
        field_strings = []
        for key, value in fields.items():
            # 处理值中可能包含的换行符，避免破坏整体格式
            value_str = str(value).replace('\n', '\\n')
            field_strings.append(f"  {key}: {value_str}")

        fields_str = ",\n".join(field_strings)
        return f"Context(fields: {{\n{fields_str}\n}})"

