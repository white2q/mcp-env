# server.py
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool(
    name="summary",
    description="总结会话历史记录，支持总结当前会话或全部会话历史",
    parameters={
        "type": "object",
        "properties": {
            "summaryHistory": {
                "type": "string",
                "description": "会话历史记录内容。可以是当前会话历史或完整的会话历史，取决于用户的请求。",
            },
            "historyType": {
                "type": "string",
                "enum": ["current", "all"],
                "description": "指定要总结的会话历史类型: 'current' 表示仅当前会话, 'all' 表示全部会话历史",
                "default": "current"
            }
        },
        "required": ["summaryHistory"],
    },
)
def summary(summaryHistory: str, historyType: str = "all") -> str:
    """summary history"""
    prefix = "全部会话历史记录：" if historyType == "all" else "当前会话历史记录："
    return prefix + summaryHistory

if __name__ == "__main__":
    mcp.run()