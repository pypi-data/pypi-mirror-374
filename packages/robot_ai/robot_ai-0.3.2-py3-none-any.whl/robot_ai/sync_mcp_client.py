import asyncio
import threading
from contextlib import AsyncExitStack
from typing import Any, Dict, Iterable, Optional, Tuple

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client


class SyncMCPClient:
	"""
	基于 modelcontextprotocol/python-sdk 的同步 MCP 客户端封装，支持 stdio 与 streamable_http。

	使用示例：
		# 1) Streamable HTTP
		client = SyncMCPClient(url="https://your-mcp-server/mcp")
		client.connect()
		result = client.call_tool("echo", {"message": "hello"})
		client.close()

		# 2) stdio（本地可执行）
		client = SyncMCPClient(command=["python", "server.py"])  # 或可执行命令 + 参数
		with client:
			tools = client.list_tools()
			print([t.name for t in tools.tools])
	"""

	def __init__(
		self,
		*,
		url: Optional[str] = None,
		command: Optional[Iterable[str]] = None,
		timeout: float = 60.0,
		http_headers: Optional[Dict[str, str]] = None,
	):
		# 传输选项
		self._url = url
		self._command = list(command) if command is not None else None
		self._http_headers = http_headers or {}

		# 同步封装相关
		self._timeout = timeout
		self._loop: Optional[asyncio.AbstractEventLoop] = None
		self._loop_thread: Optional[threading.Thread] = None
		self._exit_stack: Optional[AsyncExitStack] = None
		self._session: Optional[ClientSession] = None
		self._connected = False

		# 记录底层传输（read, write, close）
		self._transport: Optional[Tuple[Any, Any, Any]] = None

	def __enter__(self):
		self.connect()
		return self

	def __exit__(self, exc_type, exc, tb):
		self.close()

	# ---------------- Internal helpers ----------------
	def _ensure_loop(self) -> None:
		if self._loop and self._loop.is_running():
			return

		def _run_loop(loop: asyncio.AbstractEventLoop):
			asyncio.set_event_loop(loop)
			loop.run_forever()

		self._loop = asyncio.new_event_loop()
		self._loop_thread = threading.Thread(target=_run_loop, args=(self._loop,), daemon=True)
		self._loop_thread.start()

	def _run_coro(self, coro):
		if not self._loop or not self._loop.is_running():
			raise RuntimeError("Event loop not running. Did you call connect()?")
		future = asyncio.run_coroutine_threadsafe(coro, self._loop)
		return future.result(timeout=self._timeout)

	# ---------------- Connect / Close ----------------
	async def _async_connect(self):
		if self._connected:
			return
		self._exit_stack = AsyncExitStack()

		# 创建传输并连接
		if self._command is not None:
			# stdio 传输
			params = StdioServerParameters(
				command=self._command[0],
				args=self._command[1:],
				env=None,
			)
			read, write = await self._exit_stack.enter_async_context(stdio_client(params))
			self._transport = (read, write, None)
		elif self._url is not None:
			# streamable_http 传输
			read, write, _close = await self._exit_stack.enter_async_context(
				streamablehttp_client(self._url, headers=self._http_headers)
			)
			self._transport = (read, write, _close)
		else:
			raise ValueError("必须提供 url (streamable_http) 或 command (stdio) 其一")

		# 创建会话并初始化
		assert self._transport is not None
		read, write, _ = self._transport
		session = await self._exit_stack.enter_async_context(ClientSession(read, write))
		await session.initialize()
		self._session = session
		self._connected = True

	async def _async_close(self):
		if not self._connected:
			return
		try:
			if self._exit_stack is not None:
				await self._exit_stack.aclose()
		finally:
			self._exit_stack = None
			self._session = None
			self._transport = None
			self._connected = False

	def connect(self) -> None:
		"""建立到 MCP 服务器的连接。"""
		self._ensure_loop()
		self._run_coro(self._async_connect())

	def close(self) -> None:
		"""关闭连接并清理资源。"""
		if self._loop and self._loop.is_running():
			# 先在事件循环中关闭异步资源
			try:
				self._run_coro(self._async_close())
			except Exception:
				# 忽略关闭过程中的异常，尽量释放后续资源
				pass

			# 停止事件循环线程
			self._loop.call_soon_threadsafe(self._loop.stop)
			if self._loop_thread is not None:
				self._loop_thread.join(timeout=5)

		# 彻底清理
		self._loop = None
		self._loop_thread = None

	# ---------------- Sync wrappers for ClientSession ----------------
	def list_tools(self):
		"""同步列出工具。返回 mcp.types.ListToolsResult。"""
		if not self._session:
			raise RuntimeError("Not connected")
		return self._run_coro(self._session.list_tools())

	def list_resources(self):
		"""同步列出资源。返回 mcp.types.ListResourcesResult。"""
		if not self._session:
			raise RuntimeError("Not connected")
		return self._run_coro(self._session.list_resources())

	def list_prompts(self):
		"""同步列出 Prompts。返回 mcp.types.ListPromptsResult。"""
		if not self._session:
			raise RuntimeError("Not connected")
		return self._run_coro(self._session.list_prompts())

	def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None):
		"""同步调用 MCP 工具。返回 mcp.types.CallToolResult。"""
		if not self._session:
			raise RuntimeError("Not connected")
		arguments = arguments or {}
		return self._run_coro(self._session.call_tool(name, arguments))

	def read_resource(self, uri: str):
		"""同步读取资源。返回 mcp.types.ReadResourceResult。"""
		if not self._session:
			raise RuntimeError("Not connected")
		return self._run_coro(self._session.read_resource(uri))