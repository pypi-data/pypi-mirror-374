import traceback
from typing import List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from dataclasses import dataclass

from .context import Context
from .domain import (PushConfigKeywordDO, PushConfigKeyword, KeywordDO,
                     Keyword, RecordDO, Record, SourceKeywordOffset, SourceKeywordOffsetDO, Event, EventDO)
from .exception import (MySQLException_Connection, MySQLException_Delete,
                        MySQLException_Insert, MySQLException_Select,
                        MySQLException_Update, MySQLException_Unknown,
                        MySQLException_IDNotExist, MySQLException_IDAlreadyExist)
from .idgen import gen_id

@dataclass
class DBConfig:
    def __init__(self, host: str = "localhost", port: int = 3306,
                 database: str = "publicity_eye", user: str = None, password: str = None):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.charset = "utf8mb4"
        self.collation = "utf8mb4_general_ci"


conf: DBConfig

class Repo:
    def __init__(self, do_cls, en_cls):
        # conf = DBConfig()

        self.do_cls = do_cls
        self.en_cls = en_cls
        self.engine = create_engine(f'mysql+mysqlconnector://'
                                    f'{conf.user}:{conf.password}@'
                                    f'{conf.host}:{conf.port}'
                                    f'/{conf.database}')
        self._session_factory = sessionmaker(bind=self.engine)

    def create(self, ctx: Context, instance=None):
        try:
            if instance.id is not None:
                raise MySQLException_IDAlreadyExist()
            instance.id = gen_id()
            do = instance.to_orm()

            def operation(session):
                session.add(do)
                session.commit()
                return instance.from_orm(do)

            return self._with_rollback(operation)
        except Exception as e:
            raise (MySQLException_Insert.
                   with_msg(f"create failed, instance: {instance}").
                   with_cause(e).
                   with_context(ctx.with_mysql_table(self.do_cls.__tablename__)))

    def create_batch(self, ctx: Context, instances):
        try:
            dos = [instance.to_orm() for instance in instances]
            for do in dos:
                if do.id is not None:
                    raise MySQLException_IDAlreadyExist()

            def operation(session):
                session.bulk_save_objects(dos, return_defaults=True)
                session.commit()
                for i in range(len(instances)):
                    instances[i] = instances[i].from_orm(dos[i])
                return instances

            return self._with_rollback(operation)
        except Exception as e:
            raise (MySQLException_Insert.
                   with_msg(f"create batch failed, instances: {instances}").
                   with_cause(e).
                   with_context(ctx.with_mysql_table(self.do_cls.__tablename__)))

    def get(self, ctx: Context, id: int):
        """根据ID获取单个记录，返回业务实体或None"""
        try:
            do = self._with_rollback(lambda s: s.get(self.do_cls, id))
            return self.en_cls.from_orm(do) if do else None
        except Exception as e:
            raise (MySQLException_Select.
                   with_msg(f"get by id failed, id: {id}").
                   with_cause(e).
                   with_context(ctx.with_mysql_table(self.do_cls.__tablename__)))

    def _get_by_condition(self, ctx: Context, **kwargs):
        try:
            def operation(session):
                query = session.query(self.do_cls)
                for key, value in kwargs.items():
                    query = query.filter(getattr(self.do_cls, key) == value)
                orm_obj = query.first()
                if orm_obj is None:
                    self._log(f"警告: 根据条件{kwargs}未找到event")
                    return None
                return self.en_cls.from_orm(orm_obj)

            return self._with_rollback(operation)

        except Exception as e:
            raise (MySQLException_Select.
                   with_msg(f"get by condition failed, args: {kwargs}").
                   with_cause(e).
                   with_context(ctx.with_mysql_table(self.do_cls.__tablename__)))

    def get_all(self, ctx: Context, limit: int = None, offset: int = 0):
        """获取所有记录，支持分页"""
        try:
            def operation(session):
                query = session.query(self.do_cls)
                if limit is not None:
                    query = query.limit(limit)
                if offset > 0:
                    query = query.offset(offset)
                orm_objs = query.all()
                return [self.en_cls.from_orm(obj) for obj in orm_objs]

            return self._with_rollback(operation)
        except Exception as e:
            raise (MySQLException_Select.
                   with_msg(f"get all failed, offset: {offset}, limit: {limit}").
                   with_cause(e).
                   with_context(ctx.with_mysql_table(self.do_cls.__tablename__)))

    def update(self, ctx: Context, instance):
        """更新记录并返回更新后的业务实体"""
        try:
            if instance.id is None:
                raise MySQLException_IDNotExist

            def operation(session):
                do = instance.to_orm()
                merged_obj = session.merge(do)
                session.commit()
                return self.en_cls.from_orm(merged_obj)

            return self._with_rollback(operation)

        except Exception as e:
            raise (MySQLException_Update.
                   with_msg(f"update failed, instance: {instance}").
                   with_cause(e).
                   with_context(ctx.with_mysql_table(self.do_cls.__tablename__)))

    def update_batch(self, ctx: Context, instances):
        """批量更新记录，返回更新后的业务实体列表"""
        try:
            def operation(session):
                updated_orms = []
                for instance in instances:
                    if instance.id is None:
                        self._log(f"警告: 记录 ID 缺失，跳过更新: {instance}")
                        continue
                    orm_obj = instance.to_orm()
                    merged_obj = session.merge(orm_obj)
                    updated_orms.append(merged_obj)
                session.commit()
                return [self.en_cls.from_orm(obj) for obj in updated_orms]

            return self._with_rollback(operation)

        except Exception as e:
            raise (MySQLException_Update.
                   with_msg(f"update batch failed, instance: {instances}").
                   with_cause(e).
                   with_context(ctx.with_mysql_table(self.do_cls.__tablename__)))

    def delete_by_id(self, ctx: Context, id: int) -> bool:
        """根据ID删除记录，返回是否删除成功"""
        try:
            def operation(session):
                rows_deleted = session.query(self.do_cls).filter_by(id=id).delete()
                session.commit()
                return rows_deleted > 0

            result = self._with_rollback(operation)
            if not result:
                self._log(f"警告: ID为{id}的记录不存在")
            return result

        except Exception as e:
            raise (MySQLException_Delete.
                   with_msg(f"delete by id failed, id: {id}").
                   with_cause(e).
                   with_context(ctx.with_mysql_table(self.do_cls.__tablename__)))

    def delete(self, ctx: Context, instance) -> None:
        """删除指定业务实体对应的记录"""
        try:
            def operation(session):
                do = instance.to_orm()
                do = session.merge(do)
                session.delete(do)
                session.commit()

            self._with_rollback(operation)

        except Exception as e:
            raise (MySQLException_Delete.
                   with_msg(f"delete failed, instance: {instance}").
                   with_cause(e).
                   with_context(ctx.with_mysql_table(self.do_cls.__tablename__)))

    def delete_batch(self, ctx: Context, ids: List[int]) -> int:
        """批量删除记录，返回实际删除的数量"""
        try:
            def operation(session):
                query = session.query(self.do_cls).filter(self.do_cls.id.in_(ids))
                deleted_count = query.delete(synchronize_session=False)
                session.commit()
                return deleted_count

            result = self._with_rollback(operation)
            if result < len(ids):
                self._log(f"部分删除: 请求预期删除{len(ids)}条记录，实际删除{result}条")
            return result

        except Exception as e:
            raise (MySQLException_Delete.
                   with_msg(f"delete batch failed, ids: {ids}").
                   with_cause(e).
                   with_context(ctx.with_mysql_table(self.do_cls.__tablename__)))

    def _log(self, msg):
        print(f"[{self.do_cls.__tablename__}_repo]: {msg}")

    def _with_rollback(self, func):
        session = self._session_factory()
        try:
            return func(session)
        except Exception as e:
            traceback.print_exc()
            session.rollback()
            raise e  # 让调用者处理异常
        finally:
            session.close()

class EventRepo(Repo):
    def __init__(self):
        super().__init__(EventDO, Event)

    def get_by_name(self, ctx: Context, name) -> Optional[Event]:
        return self._get_by_condition(ctx, name=name)


class SourceKeywordOffsetRepo(Repo):
    def __init__(self):
        super().__init__(SourceKeywordOffsetDO, SourceKeywordOffset)

    def get_by_keyword_and_source(self, ctx: Context, keyword_id, source) -> Optional[SourceKeywordOffset]:
        offset = self._get_by_condition(ctx, keyword_id=keyword_id, source=source)
        if offset is None:
            offset = self.create(ctx, SourceKeywordOffset(keyword_id=keyword_id, source=source))
        return offset


push_config_keyword_repo: Repo
keyword_repo: Repo
event_repo: Repo
record_repo: EventRepo
offset_repo: SourceKeywordOffsetRepo

def must_init(c: DBConfig):
    global conf, push_config_keyword_repo, keyword_repo, event_repo, record_repo, offset_repo  # 声明使用全局变量
    conf = c
    # 测试连接有效性
    engine = create_engine(f'mysql+mysqlconnector://'
                           f'{conf.user}:{conf.password}@'
                           f'{conf.host}:{conf.port}'
                           f'/{conf.database}')

    # 执行简单查询验证连接
    try:
        with engine.connect() as conn:
            # 查询数据库版本
            result = conn.execute(text("SELECT VERSION()"))
            db_version = result.scalar()
            print(f"数据库连接成功, 版本: {db_version}")
        push_config_keyword_repo = Repo(PushConfigKeywordDO, PushConfigKeyword)
        keyword_repo = Repo(KeywordDO, Keyword)
        record_repo = Repo(RecordDO, Record)
        event_repo = EventRepo()
        offset_repo = SourceKeywordOffsetRepo()
        print(f"初始化仓库成功")
        return True

    except Exception as e:
        print("数据库连接无效, 请检查配置")
        raise MySQLException_Connection.raise_with_cause(e)
