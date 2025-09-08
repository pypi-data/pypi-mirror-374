import json
import time

from robot_ai.sync_mcp_client import SyncMCPClient
from robot_base import ParamException, func_decorator, log_decorator


@log_decorator
@func_decorator
def init_mcp_server(select_mcp_server, **kwargs):
	mcp_server_config = json.loads(select_mcp_server)
	client = SyncMCPClient(
		command=[mcp_server_config['command']] + mcp_server_config['parameter'].split(' ', -1)
		if mcp_server_config['type'] == 'stdio'
		else None,
		url=mcp_server_config['url'] if mcp_server_config['type'] != 'stdio' else None,
	)
	client.connect()
	time.sleep(0.1)
	return client


@log_decorator
@func_decorator
def disconnect_mcp_server(mcp_server: SyncMCPClient, **kwargs):
	mcp_server.close()


@log_decorator
@func_decorator
def request_mcp(mcp_server: SyncMCPClient, **kwargs):
	code_block_extra_data = kwargs.get('code_block_extra_data', {})
	tool_name = code_block_extra_data.get('code_block_name', '')
	if not tool_name:
		raise ParamException('参数异常,工具名称为空')
	arguments = {}
	for key, value in kwargs.items():
		if key != 'code_block_extra_data':
			arguments[key] = value
	return mcp_server.call_tool(tool_name, arguments).content
