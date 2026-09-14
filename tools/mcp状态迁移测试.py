# -*- coding: utf-8 -*-
"""
allstate 加冕迁移验证脚本：通过 MCP 驱动游戏验证 System/positions 新家与旧档加载。
前置：游戏已运行（python main.py），MCP 服务在 127.0.0.1:7310。
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

URL = "http://127.0.0.1:7310/mcp"


async def call(session, name, args=None):
    result = await session.call_tool(name, args or {})
    data = None
    for attr in ("structuredContent", "structured_content"):
        data = getattr(result, attr, None)
        if data:
            break
    if data is None:
        parts = [getattr(b, "text", "") for b in getattr(result, "content", None) or []]
        data = "\n".join(parts)
        try:
            data = json.loads(data)
        except (ValueError, TypeError):
            pass
    return data


async def tail(session, n=15, cursor=None):
    args = {"lines": n}
    if cursor is not None:
        args["cursor"] = cursor
    return await call(session, "pera_read_output", args)


async def main():
    print("连接 MCP ...")
    async with streamable_http_client(URL) as t:
        async with ClientSession(t[0], t[1]) as session:
            await session.initialize()

            print("\n===== 阶段1：启动后初始状态（主菜单）=====")
            state = await call(session, "pera_get_state")
            print(json.dumps(state, ensure_ascii=False, indent=1))

            # 走 start 流程：'0' → 立绘检查提问 → '2' 跳过 → 观察后续
            print("\n===== 阶段2：进入 start 流程 =====")
            print(" ", await call(session, "pera_send_input", {"text": "0"}))
            await asyncio.sleep(1.5)
            data = await tail(session, 8)
            print("\n".join("  " + ln for ln in data.get("lines", []) if ln))
            cursor = data.get("next_cursor")

            print("\n  -- 注入 '2' 跳过立绘检查 --")
            await call(session, "pera_send_input", {"text": "2"})
            await asyncio.sleep(1.5)
            data = await tail(session, 12)
            print("\n".join("  " + ln for ln in data.get("lines", []) if ln))

            state = await call(session, "pera_get_state")
            print("\n  start流程后的状态: scene={} time={}-{}-{} {}:{} weather={}".format(
                state["scene"], state["time"].split(" ")[0].split("-")[0],
                state["time"].split(" ")[0].split("-")[1], state["time"].split(" ")[0].split("-")[2],
                state["time"].split(" ")[1].split(":")[0], state["time"].split(" ")[1].split(":")[1],
                state["weather"]))

            print("\n===== 完成 =====")


if __name__ == "__main__":
    asyncio.run(main())
