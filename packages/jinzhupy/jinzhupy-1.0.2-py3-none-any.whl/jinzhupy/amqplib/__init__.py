# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 10:18
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 10:18
# Thanks for your comments!

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable

from .defs import BindingConfig, ExchangeConfig, ExchangeTypeStr, QueueConfig, RabbitMQConnectionConfig
from .rabbitmq import AsyncRabbitMQClient
from ..tools.singleton import singleton

logger = logging.getLogger(__name__)

DEFAULT_MQ_KEY = ""


@singleton
class RabbitMQManager:
    """多 RabbitMQ 连接管理器"""

    def __init__(self):
        self._clients: Dict[str, AsyncRabbitMQClient] = {}
        self._lock = asyncio.Lock()

    async def connect(
            self,
            key: str,
            conn_conf: Dict[str, Any],
            mq_confs: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncRabbitMQClient:
        """
        添加 RabbitMQ 连接

        :param key: 连接的唯一标识
        :param conn_conf: 连接配置字典
        :param mq_confs: 基础设施配置
        :return: RabbitMQ 客户端实例
        """
        async with self._lock:
            if key in self._clients:
                raise ValueError(f"RabbitMQ connection with key '{key}' already exists")

            global DEFAULT_MQ_KEY
            if not DEFAULT_MQ_KEY:
                DEFAULT_MQ_KEY = key

            # 转换连接配置
            connection_config = RabbitMQConnectionConfig(
                host=conn_conf.get("host", "localhost"),
                port=conn_conf.get("port", 5672),
                username=conn_conf.get("username", "guest"),
                password=conn_conf.get("password", "guest"),
                virtual_host=conn_conf.get("virtual_host", "/"),
                heartbeat=conn_conf.get("heartbeat", 600),
                timeout=conn_conf.get("timeout", 10)
            )

            # 如果有基础设施配置，设置交换机和队列
            if mq_confs:
                for mq_conf in mq_confs:
                    # 处理交换机配置
                    if "exchange" in mq_conf:
                        exchange_config = mq_conf["exchange"]
                        connection_config.exchanges.append(ExchangeConfig(
                            name=exchange_config["name"],
                            type=ExchangeTypeStr(exchange_config["type"]),
                            durable=exchange_config.get("durable", True)
                        ))

                    # 处理队列配置
                    if "queue" in mq_conf:
                        queue_name = mq_conf["queue"]
                        connection_config.queues.append(QueueConfig(
                            name=queue_name,
                            durable=mq_conf.get("durable", True)
                        ))

                    # 处理绑定配置
                    if "exchange" in mq_conf and "queue" in mq_conf:
                        exchange_name = mq_conf["exchange"]["name"]
                        queue_name = mq_conf["queue"]

                        # 处理路由键绑定
                        if "routing_keys" in mq_conf:
                            # 多个特定路由键
                            for routing_key in mq_conf["routing_keys"].values():
                                connection_config.bindings.append(BindingConfig(
                                    queue=queue_name,
                                    exchange=exchange_name,
                                    routing_key=routing_key
                                ))

                        # 处理通配符绑定
                        if "binding_keys" in mq_conf:
                            connection_config.bindings.append(BindingConfig(
                                queue=queue_name,
                                exchange=exchange_name,
                                routing_key=mq_conf["binding_keys"]
                            ))

            # 创建客户端
            client = AsyncRabbitMQClient(connection_config)
            await client.initialize()

            self._clients[key] = client
            logger.info(f"Added RabbitMQ connection: {key}")
            return client

    async def get_client(self, key=DEFAULT_MQ_KEY) -> AsyncRabbitMQClient:
        """
        获取指定key的RabbitMQ客户端

        :param key: 连接的唯一标识
        :return: RabbitMQ客户端实例
        """
        async with self._lock:
            if key not in self._clients:
                raise KeyError(f"No RabbitMQ connection found with key '{key}'")
            return self._clients[key]

    async def remove_connection(self, key=DEFAULT_MQ_KEY) -> None:
        """
        移除并关闭指定key的RabbitMQ连接

        :param key: 连接的唯一标识
        """
        async with self._lock:
            if key in self._clients:
                client = self._clients.pop(key)
                await client.close()
                logger.info(f"Removed RabbitMQ connection: {key}")

    async def close_all_connections(self) -> None:
        """关闭所有RabbitMQ连接"""
        async with self._lock:
            for key, client in list(self._clients.items()):
                try:
                    await client.close()
                except Exception as e:
                    logger.error(f"Error closing connection {key}: {e}")
                finally:
                    del self._clients[key]

            logger.info("All RabbitMQ connections closed")

    def get_all_connection_keys(self) -> List[str]:
        """获取所有已注册的连接key"""
        return list(self._clients.keys())

    # 以下方法提供便捷访问，避免显式调用get_client
    async def publish(
            self,
            exchange_name: str,
            routing_key: str,
            message: Union[Dict, str, bytes],
            persistent: bool = True,
            headers: Optional[Dict] = None,
            key=DEFAULT_MQ_KEY
    ) -> None:
        """发布消息"""
        client = await self.get_client(key)
        await client.publish(exchange_name, routing_key, message, persistent, headers)

    async def consume(
            self,
            queue_name: str,
            callback: Callable[[Dict, Any], Awaitable[None]],
            auto_ack: bool = False,
            prefetch_count: int = 20,
            key=DEFAULT_MQ_KEY
    ) -> None:
        """消费消息"""
        client = await self.get_client(key)
        await client.consume(queue_name, callback, auto_ack, prefetch_count)

    async def rpc_call(
            self,
            exchange_name: str,
            routing_key: str,
            message: Union[Dict, str, bytes],
            timeout: int = 30,
            key=DEFAULT_MQ_KEY
    ) -> Any:
        """RPC调用"""
        client = await self.get_client(key)
        return await client.rpc_call(exchange_name, routing_key, message, timeout)

    async def query_mq(
            self,
            exchange_name: str,
            rk: str,
            message: Union[Dict, str, bytes],
            timeout: int = 30,
            key=DEFAULT_MQ_KEY
    ) -> Any:
        """查询MQ（RPC简化封装）"""
        client = await self.get_client(key)
        return await client.query_mq(exchange_name, rk, message, timeout)
