# -*- coding: utf-8 -*-
"""
MCP 测试客户端：连接游戏内嵌 MCP 调试服务，验证三个工具的闭环。

用法：先启动游戏（python main.py），另开终端运行：
    .venv/Scripts/python tools/mcp测试客户端.py
可用环境变量 PERA_MCP_URL 覆盖服务地址。
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

URL = os.environ.get("PERA_MCP_URL", "http://127.0.0.1:7310/mcp")


def extract_text(result):
    """从 CallToolResult 提取可读内容（优先结构化数据，退回纯文本块）"""
    for attr in ("structuredContent", "structured_content"):
        data = getattr(result, attr, None)
        if data:
            return data
    parts = []
    for block in getattr(result, "content", None) or []:
        text = getattr(block, "text", None)
        if text is None and isinstance(block, dict):
            text = block.get("text")
        parts.append(str(text) if text is not None else repr(block))
    return "\n".join(parts)


async def read_output(session, lines=5, cursor=None):
    """调用 pera_read_output 并返回结构化 dict（服务端可能以 JSON 字符串返回，此处兜底解析）"""
    args = {"lines": lines}
    if cursor is not None:
        args["cursor"] = cursor
    result = await session.call_tool("pera_read_output", args)
    data = extract_text(result)
    if isinstance(data, str):
        import json as _json
        try:
            data = _json.loads(data)
        except ValueError:
            pass
    return data


async def main():
    print(f"连接 {URL} ...")
    async with streamable_http_client(URL) as transport:
        # 兼容不同版本：mcp 1.x 返回 (read, write, ctx) 三元组，2.x 返回 (read, write) 二元组
        read, write = transport[0], transport[1]
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. 工具列表
            tools = await session.list_tools()
            print("== 工具列表 ==")
            for t in tools.tools:
                desc = (t.description or "").splitlines()[0] if t.description else ""
                print(f"  - {t.name}: {desc}")

            # 2. 状态快照
            print("\n== pera_get_state ==")
            print(" ", extract_text(await session.call_tool("pera_get_state", {})))

            # 3. 尾部读取
            print("\n== pera_read_output（尾部 5 行）==")
            data = await read_output(session, lines=5)
            next_cursor = None
            if isinstance(data, dict):
                for line in data.get("lines", []):
                    print(" ", line)
                next_cursor = data.get("next_cursor")
            else:
                print(" ", data)

            # 4. 增量读取（此刻游戏在等输入，应为 0 行）
            data2 = await read_output(session, lines=50, cursor=next_cursor)
            if isinstance(data2, dict):
                print(f"\n== 增量读取（cursor={next_cursor}）: 新增 {len(data2.get('lines', []))} 行 ==")

            # 5. 注入输入：主菜单对未知输入只回显，但回显本身会出现在输出里——足以证明注入生效
            print("\n== pera_send_input 注入 'ping_from_mcp' ==")
            print(" ", extract_text(await session.call_tool("pera_send_input", {"text": "ping_from_mcp"})))

            await asyncio.sleep(2)  # 给游戏一点时间消化注入（INPUT 循环每帧轮询）

            # 6. 再读输出，确认回显行出现（注入后会追加约7条：回显、空行、菜单重渲染等）
            data3 = await read_output(session, lines=12)
            print("\n== 注入后的输出（应能看到 ping_from_mcp 回显）==")
            if isinstance(data3, dict):
                for line in data3.get("lines", []):
                    print(" ", line)
                ok = any("ping_from_mcp" in ln for ln in data3.get("lines", []))
                print(f"\n{'✅ 输入注入闭环验证通过' if ok else '❌ 未在输出中找到注入的回显'}")
            else:
                print(" ", data3)

            print("=== 测试完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
