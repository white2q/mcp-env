from fastmcp import FastMCP, Context


# 创建FastMCP实例
mcp = FastMCP("Session Summary Server")


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
    session_info = {
        "session_id": ctx.session_id,
        "request_id": ctx.request_id,
        "client_id": ctx.client_id if hasattr(ctx, 'client_id') else "N/A"
    }
    
    return session_info


if __name__ == "__main__":
    # 运行MCP服务器
    mcp.run()