# sync_mcp_client.py
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from mcp import ClientSession, ReadResourceResult, Tool
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Prompt
from pydantic import AnyUrl


class SyncMCPClient:
	"""
	同步风格的 MCP 客户端封装
	支持两种传输层：stdio / streamable-http
	"""

	def __init__(
		self,
		*,
		command: Optional[List[str]] = None,
		url: Optional[str] = None,
	):
		"""
		二选一初始化：
		1) command: 启动本地服务器的命令列表，如 ["python", "server.py"]
		2) url: 远程 streamable-http 地址，如 "http://localhost:8000/mcp"
		"""
		if bool(command) == bool(url):
			raise ValueError('必须且只能指定 command 或 url 之一')
		self._command = command
		self._url = url
		self._session: Optional[ClientSession] = None
		self._exit_stack = None

	# -------------------- 生命周期 --------------------
	def connect(self) -> None:
		"""建立连接并完成初始化"""
		if self._session is not None:
			return
		self._exit_stack = asynccontextmanager(self._acquire)()
		self._session = asyncio.run(self._exit_stack.__aenter__())

	def close(self) -> None:
		"""关闭连接"""
		if self._session is None:
			return
		asyncio.run(self._exit_stack.__aexit__(None, None, None))
		self._session = None

	def __enter__(self) -> 'SyncMCPClient':
		self.connect()
		return self

	def __exit__(self, *_: Any) -> None:
		self.close()

	# -------------------- 异步上下文实现 --------------------
	async def _acquire(self):
		if self._command:
			params = StdioServerParameters(
				command=self._command[0],
				args=self._command[1:],
			)
			async with stdio_client(params) as (read, write):
				async with ClientSession(read, write) as session:
					await session.initialize()
					yield session
		else:
			async with streamablehttp_client(self._url) as (read, write, _):
				async with ClientSession(read, write) as session:
					await session.initialize()
					yield session

	# -------------------- 同步 API --------------------
	def list_tools(self) -> List[Tool]:
		"""返回所有可用工具"""
		return asyncio.run(self._session.list_tools()).tools

	def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
		"""调用指定工具"""
		return asyncio.run(self._session.call_tool(name, arguments))

	def list_prompts(self) -> List[Prompt]:
		"""返回所有提示模板"""
		return asyncio.run(self._session.list_prompts()).prompts

	def read_resource(self, uri: AnyUrl) -> ReadResourceResult:
		"""读取资源内容（文本）"""
		return asyncio.run(self._session.read_resource(uri))

	# -------------------- 便捷方法 --------------------
	def tool_names(self) -> List[str]:
		return [t.name for t in self.list_tools()]

	def prompt_names(self) -> List[str]:
		return [p.name for p in self.list_prompts()]
