from fastmcp import FastMCP, Context
from typing import Dict, List
import json
import os
from datetime import datetime


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
        "timestamp": datetime.now().isoformat()
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


# 新增功能：将会话历史导出到桌面
@mcp.tool
async def export_session_history_to_desktop(ctx: Context, session_id: str = None) -> dict:
    """
    导出会话历史记录到桌面
    
    Args:
        ctx: 上下文对象
        session_id: 特定会话ID，如果未提供则导出所有会话
    
    Returns:
        dict: 导出结果信息
    """
    try:
        # 获取桌面路径
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop_path):
            # Windows系统可能使用不同的路径
            desktop_path = os.path.join(os.path.expanduser("~"), "桌面")
            if not os.path.exists(desktop_path):
                return {"error": "无法找到桌面路径"}
        
        # 确定要导出的会话
        sessions_to_export = {}
        if session_id:
            if session_id in session_histories:
                sessions_to_export[session_id] = session_histories[session_id]
            else:
                return {"error": f"未找到会话ID: {session_id}"}
        else:
            sessions_to_export = session_histories
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if session_id:
            filename = f"session_history_{session_id[:8]}_{timestamp}.json"
        else:
            filename = f"all_session_histories_{timestamp}.json"
        
        # 创建导出数据
        export_data = {
            "export_timestamp": timestamp,
            "session_count": len(sessions_to_export),
            "sessions": {}
        }
        
        # 处理会话数据
        for sid, history in sessions_to_export.items():
            # 为每个会话生成摘要
            session_summary = _generate_session_summary(sid, history)
            
            export_data["sessions"][sid] = {
                "summary": session_summary,
                "history_count": len(history),
                "history": history
            }
        
        # 写入文件
        file_path = os.path.join(desktop_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "file_path": file_path,
            "session_count": len(sessions_to_export),
            "message": f"成功导出会话历史到: {file_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"导出过程中发生错误: {str(e)}"
        }


def _generate_session_summary(session_id: str, history: List[Dict]) -> dict:
    """
    为会话生成摘要信息
    
    Args:
        session_id: 会话ID
        history: 会话历史记录列表
    
    Returns:
        dict: 会话摘要信息
    """
    if not history:
        return {
            "session_id": session_id,
            "total_actions": 0,
            "summary": "空会话"
        }
    
    # 统计操作类型
    action_counts = {}
    for entry in history:
        action = entry.get("action", "unknown")
        action_counts[action] = action_counts.get(action, 0) + 1
    
    # 获取时间范围
    timestamps = [entry.get("timestamp", "") for entry in history if entry.get("timestamp")]
    first_time = min(timestamps) if timestamps else "未知"
    last_time = max(timestamps) if timestamps else "未知"
    
    return {
        "session_id": session_id,
        "total_actions": len(history),
        "action_types": action_counts,
        "first_action_time": first_time,
        "last_action_time": last_time,
        "summary": f"会话包含 {len(history)} 个操作，主要操作类型: {list(action_counts.keys())}"
    }


@mcp.tool
async def get_session_summary_report(ctx: Context) -> dict:
    """
    获取所有会话的摘要报告
    
    Args:
        ctx: 上下文对象
    
    Returns:
        dict: 会话摘要报告
    """
    if not session_histories:
        return {
            "total_sessions": 0,
            "message": "没有会话历史记录"
        }
    
    report = {
        "total_sessions": len(session_histories),
        "sessions": []
    }
    
    for session_id, history in session_histories.items():
        summary = _generate_session_summary(session_id, history)
        report["sessions"].append(summary)
    
    return report


@mcp.tool
async def clear_all_session_histories(ctx: Context) -> dict:
    """
    清除所有会话历史记录
    
    Args:
        ctx: 上下文对象
    
    Returns:
        dict: 操作结果
    """
    session_count = len(session_histories)
    session_histories.clear()
    
    return {
        "success": True,
        "cleared_sessions": session_count,
        "message": f"已清除 {session_count} 个会话的历史记录"
    }


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