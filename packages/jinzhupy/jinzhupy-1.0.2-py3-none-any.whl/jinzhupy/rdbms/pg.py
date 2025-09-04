# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 9:51
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 9:51
# Thanks for your comments!

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Tuple, Optional, AsyncGenerator, Union

from sqlalchemy import text, select, and_, insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncConnection
from sqlalchemy.orm import sessionmaker, InstrumentedAttribute

logger = logging.getLogger(__name__)


class AsyncPostgreSQLConnection:
    """单个PostgreSQL数据库的异步连接封装（使用单一连接池）"""

    def __init__(
            self,
            host: str,
            port: int,
            database: str,
            user: str,
            password: str,
            connect_args: dict,
            echo_sql: bool = True
    ):
        """初始化单个数据库连接配置"""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.pool_size = connect_args.get("pool_size", 5)
        self.max_overflow = connect_args.get("max_overflow", 20)
        self.pool_recycle = connect_args.get("pool_recycle", 3600)
        self.pool_timeout = connect_args.get("pool_timeout", 15)
        self.echo_sql = echo_sql

        self.base = None  # 允许不同数据库使用不同的模型基类

        # 连接池和引擎初始化标志
        self._pool_initialized = False
        self._async_engine = None
        self._async_session_factory = None

        # 初始化锁
        self._init_lock = asyncio.Lock()

    async def set_model_base(self, model_base):
        if not self.base:
            self.base = model_base

    async def initialize(self):
        """异步初始化连接池（必须在使用前调用）"""
        # 使用锁避免竞争条件
        async with self._init_lock:
            if self._pool_initialized:
                return

            try:
                # 初始化SQLAlchemy异步引擎和会话工厂
                conn_str = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
                self._async_engine = create_async_engine(
                    conn_str,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_recycle=self.pool_recycle,
                    pool_pre_ping=True,  # 连接前ping检查
                    pool_timeout=self.pool_timeout,  # 连接池超时
                    echo=self.echo_sql
                )

                # 创建异步会话工厂
                self._async_session_factory = sessionmaker(
                    self._async_engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autoflush=False
                )

                # 测试连接
                async with self._async_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))

                self._pool_initialized = True
                logger.info(f"Database connection pool initialized for {self.database}")
            except Exception as e:
                logger.error(f"Failed to initialize database connection: {e}")
                raise

    async def close(self):
        """关闭连接池"""
        async with self._init_lock:
            if self._async_engine:
                try:
                    await self._async_engine.dispose()
                except Exception as e:
                    logger.warning(f"Error disposing SQLAlchemy engine: {e}")
                finally:
                    self._async_engine = None

            self._pool_initialized = False
            logger.info(f"Database connection pool closed for {self.database}")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, None]:
        """获取原始数据库连接（异步上下文管理器）"""
        if not self._pool_initialized:
            await self.initialize()

        conn = None
        try:
            conn = await self._async_engine.connect()
            yield conn
        except Exception as e:
            if conn:
                await conn.rollback()
            logger.error(f"Error getting database connection: {e}")
            raise
        finally:
            if conn:
                await conn.close()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取ORM会话（异步上下文管理器）"""
        if not self._pool_initialized:
            await self.initialize()

        session: AsyncSession = self._async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"ORM session error: {e}")
            raise
        finally:
            await session.close()

    async def execute_sql_with_return(self, sql: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """执行原生SQL查询（异步）"""
        async with self.get_connection() as conn:
            try:
                result = await conn.execute(text(sql), params or {})

                # 处理返回结果
                if result.returns_rows:
                    rows = await result.fetchall()
                    return [dict(row._mapping) for row in rows]
                else:
                    return []
            except Exception as e:
                logger.error(f"Error executing native SQL: {sql}, params: {params}, error: {e}")
                raise

    async def execute_sql_with_noreturn(self, sql: str) -> None:
        """执行原生SQL脚本"""
        async with self.get_connection() as conn:
            try:
                await conn.execute(text(sql))
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                logger.error(f"Error executing SQL script: {sql}, error: {e}")
                raise

    async def bulk_insert_native(self, table: str, columns: List[str], data: List[Tuple]) -> int:
        """批量插入数据（原生方式）"""
        if not data:
            return 0

        # 构建INSERT语句
        stmt = insert(self.base.metadata.tables[table]).values([
            {col: val for col, val in zip(columns, row)} for row in data
        ])

        async with self.get_session() as session:
            try:
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount
            except Exception as e:
                await session.rollback()
                logger.error(f"Error in bulk insert: {e}")
                raise

    async def query_one_orm(
            self,
            model,
            filters: Optional[Union[Dict, List]] = None,
            joins: Optional[List] = None,
            options: Optional[List] = None
    ):
        """
        使用ORM查询单条数据（异步）

        :param model: 要查询的模型类
        :param filters: 过滤条件，可以是字典或SQLAlchemy表达式列表
        :param joins: 关联查询列表，格式为 [(关联模型, 关联条件)]
        :param options: SQLAlchemy加载选项，如 joinedload, selectinload 等
        :return: 查询到的单条记录，如果没有则返回None
        """
        async with self.get_session() as session:
            try:
                query = select(model)

                # 处理关联查询
                if joins:
                    for join_model, join_condition in joins:
                        query = query.join(join_model, join_condition)

                # 处理过滤条件
                if filters:
                    if isinstance(filters, dict):
                        conditions = []
                        for key, value in filters.items():
                            if hasattr(model, key):
                                conditions.append(getattr(model, key) == value)
                        if conditions:
                            query = query.where(and_(*conditions))
                    elif isinstance(filters, list):
                        # 支持SQLAlchemy表达式列表
                        query = query.where(and_(*filters))

                # 处理加载选项
                if options:
                    for option in options:
                        query = query.options(option)

                result = await session.execute(query)
                return result.scalars().first()
            except Exception as e:
                logger.error(f"Error in ORM query_one: {e}")
                raise

    async def query_all_orm(
            self,
            model,
            filters: Optional[Union[Dict, List]] = None,
            order_by: Optional[Union[str, List, InstrumentedAttribute]] = None,
            direction: Optional[str] = 'asc',
            joins: Optional[List] = None,
            options: Optional[List] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ):
        """使用ORM查询数据（异步）"""
        async with self.get_session() as session:
            try:
                query = select(model)

                # 处理关联查询
                if joins:
                    for join_model, join_condition in joins:
                        query = query.join(join_model, join_condition)

                # 支持更复杂的过滤条件
                if filters:
                    if isinstance(filters, dict):
                        conditions = []
                        for key, value in filters.items():
                            if hasattr(model, key):
                                conditions.append(getattr(model, key) == value)
                        if conditions:
                            query = query.where(and_(*conditions))
                    elif isinstance(filters, list):
                        # 支持SQLAlchemy表达式列表
                        query = query.where(and_(*filters))

                # 支持多字段排序
                if order_by:
                    if isinstance(order_by, str):
                        if hasattr(model, order_by):
                            if direction == "desc":
                                query = query.order_by(getattr(model, order_by)).desc()
                            else:
                                query = query.order_by(getattr(model, order_by))
                    elif isinstance(order_by, list):
                        order_clauses = []
                        for field in order_by:
                            if isinstance(field, str) and hasattr(model, field):
                                order_clauses.append(getattr(model, field))
                            elif hasattr(field, 'name'):  # InstrumentedAttribute
                                order_clauses.append(field)
                        if order_clauses:
                            if direction == "desc":
                                query = query.order_by(*order_clauses).desc()
                            else:
                                query = query.order_by(*order_clauses)
                    elif hasattr(order_by, 'name'):  # InstrumentedAttribute
                        if direction == "desc":
                            query = query.order_by(order_by).desc()
                        else:
                            query = query.order_by(order_by)

                # 处理加载选项
                if options:
                    for option in options:
                        query = query.options(option)

                # 添加分页支持
                if limit:
                    query = query.limit(limit)
                if offset:
                    query = query.offset(offset)

                result = await session.execute(query)
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Error in ORM query: {e}")
                raise

    async def insert_orm(self, item):
        """使用ORM插入数据（异步）"""
        async with self.get_session() as session:
            try:
                session.add(item)
                await session.flush()
                await session.refresh(item)
                return item
            except Exception as e:
                await session.rollback()
                logger.error(f"Error inserting ORM instance: {e}")
                raise

    async def bulk_insert_orm(self, items) -> int:
        """批量插入数据（ORM方式）"""
        if not items:
            return 0

        async with self.get_session() as session:
            try:
                session.add_all(items)
                await session.flush()
                return len(items)
            except Exception as e:
                await session.rollback()
                logger.error(f"Error in bulk ORM insert: {e}")
                raise

    async def create_tables(self):
        """创建所有模型对应的数据库表"""
        if not self._pool_initialized:
            await self.initialize()

        try:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(self.base.metadata.create_all)
            logger.info(f"Tables created for {self.database}")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    async def drop_tables(self):
        """删除所有模型对应的数据库表"""
        if not self._pool_initialized:
            await self.initialize()

        try:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(self.base.metadata.drop_all)
            logger.info(f"Tables dropped for {self.database}")
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise

    async def check_connection_health(self) -> bool:
        """检查连接健康状态"""
        try:
            async with self.get_connection() as conn:
                # 执行简单查询测试连接
                result = await conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.warning(f"Connection health check failed: {e}")
            return False

    async def reconnect_if_needed(self) -> bool:
        """如果需要则重新连接"""
        if not await self.check_connection_health():
            logger.info("Connection unhealthy, attempting to reconnect...")
            await self.close()
            await self.initialize()
            return True
        return False

    async def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        if not self._pool_initialized:
            return {}

        stats = {}
        try:
            if self._async_engine:
                stats = {
                    "checkedin": self._async_engine.pool.checkedin(),
                    "checkedout": self._async_engine.pool.checkedout(),
                    "overflow": self._async_engine.pool.overflow(),
                    "size": self._async_engine.pool.size(),
                }
        except Exception as e:
            logger.warning(f"Error getting pool stats: {e}")

        return stats
