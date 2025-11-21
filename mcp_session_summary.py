from fastmcp import FastMCP, Context
from typing import Dict, List
import json


# 创建FastMCP实例
mcp = FastMCP("Session Summary Server")

# 存储会话历史的字典
session_histories: Dict[str, List[Dict]] = {}


@mcp.tool
async def get_session_summary(ctx: Context) -> str:
    """
    获取当前会话信息并生成一段50字的总结
    """
    # 获取会话信息
    session_id = ctx.session_id
    request_id = ctx.request_id
    
    # 生成50字总结
    summary = f"当前会话ID: {session_id[:8]}... 请求ID: {request_id[:8]}... 此会话正在处理用户请求，包含完整的上下文信息和状态管理。"
    
    # 确保总结是50字
    if len(summary) > 50:
        summary = summary[:47] + "..."
    
    return summary


@mcp.tool
async def get_detailed_session_info(ctx: Context) -> dict:
    """
    获取详细的会话信息
    """
    # 获取基本会话信息
    session_info = {
        "session_id": ctx.session_id,
        "request_id": ctx.request_id,
        "client_id": ctx.client_id if hasattr(ctx, 'client_id') else "N/A"
    }
    
    # 尝试获取更多上下文信息
    try:
        # 获取可用的工具、资源和提示
        tools = await ctx.list_tools() if hasattr(ctx, 'list_tools') else "N/A"
        resources = await ctx.list_resources() if hasattr(ctx, 'list_resources') else "N/A"
        prompts = await ctx.list_prompts() if hasattr(ctx, 'list_prompts') else "N/A"
        
        session_info.update({
            "available_tools": [tool.name for tool in tools] if tools != "N/A" else "N/A",
            "available_resources": [resource.uri for resource in resources] if resources != "N/A" else "N/A",
            "available_prompts": [prompt.name for prompt in prompts] if prompts != "N/A" else "N/A"
        })
    except Exception as e:
        session_info["error"] = f"获取详细信息时出错: {str(e)}"
    
    return session_info


@mcp.tool
async def get_session_content(ctx: Context) -> dict:
    """
    获取会话中的具体内容，包括工具、资源和提示信息的详细内容
    """
    content = {
        "session_id": ctx.session_id,
        "request_id": ctx.request_id,
        "tools_details": {},
        "resources_details": {},
        "prompts_details": {}
    }
    
    try:
        # 获取工具详情
        tools = await ctx.list_tools() if hasattr(ctx, 'list_tools') else []
        content["tools_details"] = {
            "count": len(tools),
            "tools": [tool.dict() for tool in tools] if tools else []
        }
        
        # 获取资源详情
        resources = await ctx.list_resources() if hasattr(ctx, 'list_resources') else []
        content["resources_details"] = {
            "count": len(resources),
            "resources": [resource.dict() for resource in resources] if resources else []
        }
        
        # 获取提示详情
        prompts = await ctx.list_prompts() if hasattr(ctx, 'list_prompts') else []
        content["prompts_details"] = {
            "count": len(prompts),
            "prompts": [prompt.dict() for prompt in prompts] if prompts else []
        }
        
        # 获取状态信息
        content["state"] = getattr(ctx, '_state', {})
        
    except Exception as e:
        content["error"] = f"获取会话内容时出错: {str(e)}"
    
    return content


@mcp.tool
async def record_session_history(ctx: Context, action: str, details: dict = None) -> str:
    """
    记录会话历史
    
    Args:
        ctx: 上下文对象
        action: 执行的操作
        details: 操作详情
    """
    session_id = ctx.session_id
    
    # 初始化会话历史列表
    if session_id not in session_histories:
        session_histories[session_id] = []
    
    # 记录历史条目
    history_entry = {
        "request_id": ctx.request_id,
        "action": action,
        "details": details or {},
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    
    session_histories[session_id].append(history_entry)
    
    return f"已记录会话历史: {action}"


@mcp.tool
async def get_session_history(ctx: Context) -> dict:
    """
    获取当前会话的历史记录
    """
    session_id = ctx.session_id
    
    # 获取会话历史
    history = session_histories.get(session_id, [])
    
    return {
        "session_id": session_id,
        "history_count": len(history),
        "history": history
    }


@mcp.tool
async def clear_session_history(ctx: Context) -> str:
    """
    清除当前会话的历史记录
    """
    session_id = ctx.session_id
    
    if session_id in session_histories:
        del session_histories[session_id]
    
    return "会话历史已清除"


if __name__ == "__main__":
    # 添加一些示例工具和资源以便更好地演示
    @mcp.tool
    def example_tool(param: str) -> str:
        return f"Example tool called with param: {param}"
    
    @mcp.resource("resource://example")
    def example_resource() -> dict:
        return {"data": "example resource data"}
    
    @mcp.prompt(name="example_prompt")
    def example_prompt() -> str:
        return "This is an example prompt"
    
    # 运行MCP服务器
    mcp.run()