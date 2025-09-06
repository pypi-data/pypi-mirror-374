from mcp.server.fastmcp import FastMCP

# 创建⼀个 FastMCP 实例
mcp = FastMCP("Demo")


# 注册⼀个加法⼯具
@mcp.tool()
def add(a: int, b: int) -> int:


    """计算两个数的和"""
    return a + b


# 注册⼀个乘法⼯具
@mcp.tool()
def mul(a: int, b: int) -> int:


    """计算两个数的积"""
    return a * b
def main() -> None:
    mcp.run("stdio")
