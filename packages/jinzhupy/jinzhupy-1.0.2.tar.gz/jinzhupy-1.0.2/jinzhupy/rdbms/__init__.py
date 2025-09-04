# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 10:18
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 10:18
# Thanks for your comments!

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from .pg import AsyncPostgreSQLConnection
from ..tools.singleton import singleton

logger = logging.getLogger(__name__)

DEFAULT_DB_KEY = ""


@singleton
class DatabaseManager:
    """多数据库连接管理器，通过key管理不同的数据库连接"""

    def __init__(self):
        self._connections: Dict[str, AsyncPostgreSQLConnection] = {}
        self._lock = asyncio.Lock()  # 确保线程安全的锁

    async def add_connection(
            self,
            key: str,
            host: str = None,
            port: int = 5432,
            database: str = None,
            user: str = None,
            password: str = None,
            connect_args: dict = None,
            echo_sql: bool = True,
            overwrite: bool = False
    ) -> AsyncPostgreSQLConnection:
        """
        添加一个数据库连接

        :param key: 连接的唯一标识
        :param connect_args: pool_size, max_overflow, pool_recycle, pool_timeout
        :param overwrite: 如果key已存在，是否覆盖
        :return: 创建的连接实例
        """
        async with self._lock:
            # 检查是否已存在该key的连接
            if key in self._connections and not overwrite:
                raise ValueError(f"Database connection with key '{key}' already exists")

            global DEFAULT_DB_KEY
            if not DEFAULT_DB_KEY:
                DEFAULT_DB_KEY = key

            # 从环境变量获取配置（优先于参数）
            host = host or os.getenv(f'POSTGRES_{key.upper()}_HOST', 'localhost')
            port = port or int(os.getenv(f'POSTGRES_{key.upper()}_PORT', 5432))
            database = database or os.getenv(f'POSTGRES_{key.upper()}_DB', 'postgres')
            user = user or os.getenv(f'POSTGRES_{key.upper()}_USER', 'postgres')
            password = password or os.getenv(f'POSTGRES_{key.upper()}_PASSWORD', '')

            default_connect_args = {"pool_timeout": 15, "pool_size": 5, "pool_recycle": 3600, "max_overflow": 20}
            if connect_args:
                default_connect_args.update(connect_args)
            # 创建连接实例
            conn = AsyncPostgreSQLConnection(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                connect_args=default_connect_args,
                echo_sql=echo_sql
            )

            # 初始化连接
            await conn.initialize()

            # 存储连接
            self._connections[key] = conn
            logger.info(f"Added database connection: {key}")
            return conn

    async def set_dbs(self, configs: list):
        """通过配置对象添加连接"""
        for key, conf in configs:
            await self.add_connection(
                key=key,
                host=conf.get("host"),
                port=conf.get("port"),
                database=conf.get("database"),
                user=conf.get("user"),
                password=conf.get("password"),
                connect_args=conf.get("connect_args"),
                echo_sql=conf.get("echo_sql"),
                overwrite=conf.get("overwrite")
            )

    async def set_model_base(self, model_base, key=DEFAULT_DB_KEY):
        conn = await self.get_connection(key)
        await conn.set_model_base(model_base)

    async def get_connection(self, key=DEFAULT_DB_KEY) -> AsyncPostgreSQLConnection:
        """
        获取指定key的数据库连接

        :param key: 连接的唯一标识
        :return: 数据库连接实例
        """
        async with self._lock:
            if key not in self._connections:
                raise KeyError(f"No database connection found with key '{key}'")
            return self._connections[key]

    async def remove_connection(self, key=DEFAULT_DB_KEY) -> None:
        """
        移除并关闭指定key的数据库连接

        :param key: 连接的唯一标识
        """
        async with self._lock:
            if key in self._connections:
                conn = self._connections.pop(key)
                await conn.close()
                logger.info(f"Removed database connection: {key}")

    async def close_all_connections(self) -> None:
        """关闭所有数据库连接"""
        async with self._lock:
            # 关闭所有连接
            for key, conn in list(self._connections.items()):
                try:
                    await conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection {key}: {e}")
                finally:
                    del self._connections[key]

            logger.info("All database connections closed")

    def get_all_connection_keys(self) -> List[str]:
        """获取所有已注册的连接key"""
        return list(self._connections.keys())

    async def check_all_connections_health(self) -> Dict[str, bool]:
        """检查所有连接的健康状态"""
        results = {}
        for key in self.get_all_connection_keys():
            try:
                conn = await self.get_connection(key)
                results[key] = await conn.check_connection_health()
            except Exception as e:
                logger.error(f"Error checking health for connection {key}: {e}")
                results[key] = False
        return results

    # 以下方法提供便捷访问，避免显式调用get_connection
    async def execute_sql_with_return(self, sql: str, key=DEFAULT_DB_KEY, params: Optional[Dict] = None) -> List[
        Dict[str, Any]]:
        conn = await self.get_connection(key)
        return await conn.execute_sql_with_return(sql, params)

    async def execute_sql_with_noreturn(self, sql: str, key=DEFAULT_DB_KEY):
        conn = await self.get_connection(key)
        return await conn.execute_sql_with_noreturn(sql)

    async def query_one_orm(self, model, filters=None, joins=None, options=None, key=DEFAULT_DB_KEY):
        conn = await self.get_connection(key)
        return await conn.query_one_orm(model, filters, joins, options)

    async def query_all_orm(self, model, filters: Optional[Dict] = None, order_by=None,
                            direction: Optional[str] = 'asc', joins: Optional[List] = None,
                            options: Optional[List] = None, limit: Optional[int] = None, offset: Optional[int] = None,
                            key=DEFAULT_DB_KEY):
        conn = await self.get_connection(key)
        return await conn.query_all_orm(model, filters, order_by, direction, joins, options, limit, offset)

    async def insert_orm(self, item, key=DEFAULT_DB_KEY):
        conn = await self.get_connection(key)
        return await conn.insert_orm(item)

    async def bulk_insert_orm(self, items, key=DEFAULT_DB_KEY):
        conn = await self.get_connection(key)
        return await conn.bulk_insert_orm(items)

    async def create_tables(self, key=DEFAULT_DB_KEY) -> None:
        conn = await self.get_connection(key)
        await conn.create_tables()

    async def get_pool_stats(self, key=DEFAULT_DB_KEY) -> Dict[str, Any]:
        """获取指定连接的连接池统计信息"""
        conn = await self.get_connection(key)
        return await conn.get_pool_stats()
