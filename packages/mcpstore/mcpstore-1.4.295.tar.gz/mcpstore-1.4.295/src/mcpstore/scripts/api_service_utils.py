"""
MCPStore API Service Utilities
公共服务操作工具模块，用于消除重复代码
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime

from mcpstore import MCPStore
from mcpstore.core.models.common import APIResponse
from .api_dependencies import get_global_store
from .api_exceptions import (
    MCPStoreException, ConfigurationException, 
    ErrorCode, error_monitor
)
from .api_concurrency import safe_file_operation

logger = logging.getLogger(__name__)


class ServiceOperationHelper:
    """服务操作辅助类，提供通用的服务操作方法"""
    
    @staticmethod
    async def reset_client_services_file(
        store: MCPStore,
        context_type: str = "store",
        agent_id: Optional[str] = None
    ) -> APIResponse:
        """
        重置 client_services 文件的通用方法
        
        Args:
            store: MCPStore 实例
            context_type: 上下文类型 ("store" 或 "agent")
            agent_id: Agent ID（仅在 context_type 为 "agent" 时需要）
        """
        try:
            # 获取上下文
            if context_type == "store":
                context = store.for_store()
                context_name = "Store"
            elif context_type == "agent":
                if not agent_id:
                    raise ValueError("agent_id is required for agent context")
                context = store.for_agent(agent_id)
                context_name = f"Agent '{agent_id}'"
            else:
                raise ValueError(f"Invalid context_type: {context_type}")
            
            # 获取文件路径
            client_services_path = context._client_services_path
            
            # 检查文件是否存在
            if not os.path.exists(client_services_path):
                return APIResponse(
                    success=False,
                    data={"path": client_services_path},
                    message=f"{context_name} client_services file does not exist"
                )
            
            # 使用安全文件操作（带锁和速率限制）
            async with safe_file_operation(
                client_services_path,
                operation_type="reset_client_services",
                enable_rate_limit=True,
                rate_limit_max=3,
                rate_limit_window=60.0
            ):
                # 备份原文件
                backup_path = f"{client_services_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    import shutil
                    shutil.copy2(client_services_path, backup_path)
                    logger.info(f"Backup created at: {backup_path}")
                except Exception as backup_error:
                    logger.warning(f"Failed to create backup: {backup_error}")
                
                # 删除文件
                try:
                    os.remove(client_services_path)
                    logger.info(f"Removed client_services file: {client_services_path}")
                    
                    return APIResponse(
                        success=True,
                        data={
                            "path": client_services_path,
                            "backup_path": backup_path,
                            "context_type": context_type,
                            "agent_id": agent_id
                        },
                        message=f"{context_name} client_services file reset successfully"
                    )
                except Exception as e:
                    return APIResponse(
                        success=False,
                        data={"path": client_services_path, "error": str(e)},
                        message=f"Failed to remove {context_name} client_services file: {str(e)}"
                    )
                
        except Exception as e:
            error_monitor.record_error(e, {
                "operation": "reset_client_services_file",
                "context_type": context_type,
                "agent_id": agent_id
            })
            raise MCPStoreException(
                message=f"Failed to reset client_services file: {str(e)}",
                error_code=ErrorCode.CONFIG_UPDATE_FAILED,
                details={
                    "context_type": context_type,
                    "agent_id": agent_id,
                    "operation": "reset_client_services_file"
                }
            )
    
    @staticmethod
    async def reset_agent_clients_file(
        store: MCPStore,
        context_type: str = "store",
        agent_id: Optional[str] = None
    ) -> APIResponse:
        """
        重置 agent_clients 文件的通用方法
        
        Args:
            store: MCPStore 实例
            context_type: 上下文类型 ("store" 或 "agent")
            agent_id: Agent ID（仅在 context_type 为 "agent" 时需要）
        """
        try:
            # 获取上下文
            if context_type == "store":
                context = store.for_store()
                context_name = "Store"
            elif context_type == "agent":
                if not agent_id:
                    raise ValueError("agent_id is required for agent context")
                context = store.for_agent(agent_id)
                context_name = f"Agent '{agent_id}'"
            else:
                raise ValueError(f"Invalid context_type: {context_type}")
            
            # 获取文件路径
            agent_clients_path = context._agent_clients_path
            
            # 检查文件是否存在
            if not os.path.exists(agent_clients_path):
                return APIResponse(
                    success=False,
                    data={"path": agent_clients_path},
                    message=f"{context_name} agent_clients file does not exist"
                )
            
            # 备份原文件
            backup_path = f"{agent_clients_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(agent_clients_path, backup_path)
                logger.info(f"Backup created at: {backup_path}")
            except Exception as backup_error:
                logger.warning(f"Failed to create backup: {backup_error}")
            
            # 删除文件
            try:
                os.remove(agent_clients_path)
                logger.info(f"Removed agent_clients file: {agent_clients_path}")
                
                return APIResponse(
                    success=True,
                    data={
                        "path": agent_clients_path,
                        "backup_path": backup_path,
                        "context_type": context_type,
                        "agent_id": agent_id
                    },
                    message=f"{context_name} agent_clients file reset successfully"
                )
            except Exception as e:
                return APIResponse(
                    success=False,
                    data={"path": agent_clients_path, "error": str(e)},
                    message=f"Failed to remove {context_name} agent_clients file: {str(e)}"
                )
                
        except Exception as e:
            error_monitor.record_error(e, {
                "operation": "reset_agent_clients_file",
                "context_type": context_type,
                "agent_id": agent_id
            })
            raise MCPStoreException(
                message=f"Failed to reset agent_clients file: {str(e)}",
                error_code=ErrorCode.CONFIG_UPDATE_FAILED,
                details={
                    "context_type": context_type,
                    "agent_id": agent_id,
                    "operation": "reset_agent_clients_file"
                }
            )
    
    @staticmethod
    async def get_service_details(
        store: MCPStore,
        service_name: str,
        context_type: str = "store",
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取服务详细信息的通用方法
        
        Args:
            store: MCPStore 实例
            service_name: 服务名称
            context_type: 上下文类型 ("store" 或 "agent")
            agent_id: Agent ID（仅在 context_type 为 "agent" 时需要）
        """
        try:
            # 获取上下文
            if context_type == "store":
                context = store.for_store()
            elif context_type == "agent":
                if not agent_id:
                    raise ValueError("agent_id is required for agent context")
                context = store.for_agent(agent_id)
            else:
                raise ValueError(f"Invalid context_type: {context_type}")
            
            # 获取服务配置
            service_config = None
            for service in context.services:
                if service.name == service_name:
                    service_config = service
                    break
            
            if not service_config:
                raise MCPStoreException(
                    message=f"Service '{service_name}' not found",
                    error_code=ErrorCode.SERVICE_NOT_FOUND,
                    details={"service_name": service_name, "context_type": context_type}
                )
            
            # 获取工具列表
            tools_info = []
            if hasattr(context, '_tools') and context._tools:
                for tool_name, tool_def in context._tools.items():
                    if tool_def.get('service') == service_name:
                        tools_info.append({
                            "name": tool_name,
                            "description": tool_def.get("description", ""),
                            "input_schema": tool_def.get("inputSchema", {})
                        })
            
            # 构建服务详情
            service_details = {
                "name": service_config.name,
                "status": "active" if hasattr(service_config, 'client') and service_config.client else "inactive",
                "transport": service_config.config.get("transport", "unknown"),
                "client_id": getattr(service_config, 'client_id', None),
                "url": service_config.config.get("url"),
                "command": service_config.config.get("command"),
                "args": service_config.config.get("args"),
                "env": service_config.config.get("env"),
                "tool_count": len(tools_info),
                "is_active": hasattr(service_config, 'client') and service_config.client is not None,
                "config": service_config.config,
                "tools": tools_info
            }
            
            # 添加生命周期信息
            if hasattr(store, 'orchestrator') and store.orchestrator:
                lifecycle_manager = store.orchestrator.lifecycle_manager
                target_agent_id = agent_id or store.orchestrator.client_manager.global_agent_store_id
                
                state = lifecycle_manager.get_service_state(target_agent_id, service_name)
                metadata = lifecycle_manager.get_service_metadata(target_agent_id, service_name)
                
                if state:
                    service_details["lifecycle"] = {
                        "consecutive_successes": metadata.consecutive_successes if metadata else 0,
                        "consecutive_failures": metadata.consecutive_failures if metadata else 0,
                        "last_ping_time": metadata.last_success_time.isoformat() if metadata and metadata.last_success_time else None,
                        "error_message": metadata.error_message if metadata else None,
                        "reconnect_attempts": metadata.reconnect_attempts if metadata else 0,
                        "state_entered_time": metadata.state_entered_time.isoformat() if metadata and metadata.state_entered_time else None
                    }
            
            return service_details
            
        except Exception as e:
            error_monitor.record_error(e, {
                "operation": "get_service_details",
                "service_name": service_name,
                "context_type": context_type,
                "agent_id": agent_id
            })
            raise
    
    @staticmethod
    async def get_config_with_timeout(
        context,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        带超时的配置获取方法
        
        Args:
            context: 上下文对象
            timeout: 超时时间（秒）
        """
        try:
            # 使用 asyncio.wait_for 实现超时控制
            return await asyncio.wait_for(
                context.get_config_async(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise MCPStoreException(
                message="Configuration retrieval timed out",
                error_code=ErrorCode.CONFIG_ERROR,
                details={"timeout": timeout, "operation": "get_config_async"}
            )
        except Exception as e:
            raise MCPStoreException(
                message=f"Failed to retrieve configuration: {str(e)}",
                error_code=ErrorCode.CONFIG_ERROR,
                details={"error": str(e)}
            )
    
    @staticmethod
    async def update_config_with_timeout(
        context,
        config_data: Dict[str, Any],
        timeout: float = 30.0
    ) -> bool:
        """
        带超时的配置更新方法
        
        Args:
            context: 上下文对象
            config_data: 配置数据
            timeout: 超时时间（秒）
        """
        try:
            # 使用 asyncio.wait_for 实现超时控制
            return await asyncio.wait_for(
                context.update_config_async(config_data),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise MCPStoreException(
                message="Configuration update timed out",
                error_code=ErrorCode.CONFIG_UPDATE_FAILED,
                details={"timeout": timeout, "operation": "update_config_async"}
            )
        except Exception as e:
            raise MCPStoreException(
                message=f"Failed to update configuration: {str(e)}",
                error_code=ErrorCode.CONFIG_UPDATE_FAILED,
                details={"error": str(e)}
            )


# 便捷函数
async def reset_store_client_services(store: MCPStore) -> APIResponse:
    """Store 级别重置 client_services 文件"""
    return await ServiceOperationHelper.reset_client_services_file(
        store, context_type="store"
    )


async def reset_agent_client_services(store: MCPStore, agent_id: str) -> APIResponse:
    """Agent 级别重置 client_services 文件"""
    return await ServiceOperationHelper.reset_client_services_file(
        store, context_type="agent", agent_id=agent_id
    )


async def reset_store_agent_clients(store: MCPStore) -> APIResponse:
    """Store 级别重置 agent_clients 文件"""
    return await ServiceOperationHelper.reset_agent_clients_file(
        store, context_type="store"
    )


async def reset_agent_agent_clients(store: MCPStore, agent_id: str) -> APIResponse:
    """Agent 级别重置 agent_clients 文件"""
    return await ServiceOperationHelper.reset_agent_clients_file(
        store, context_type="agent", agent_id=agent_id
    )