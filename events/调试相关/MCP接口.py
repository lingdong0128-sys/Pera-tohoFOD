# -*- coding: utf-8 -*-
"""
MCP 调试接口 —— 框架内嵌 MCP 服务器
====================================

以事件形式向外暴露工具：任何事件函数挂上 is_mcp_tool 属性，即自动注册为 MCP 工具，
由本文件的启动事件在游戏启动时统一拉起服务（HTTP 传输，daemon 线程）。

【铁律】MCP 工具事件在 MCP 线程里被调用：
  1. 绝不 PRINT / 绘制 / 播放音乐（pygame 非线程安全）
  2. 只做：读取数据（list/dict 拷贝在 CPython 下边写边读是安全的）或 入队（queue.Queue 线程安全）
  3. 异常不要往外抛，返回错误字符串即可（包装层也有兜底）
"""
import inspect
import threading

# 模块级状态：防止重复启动（热重载后再触发启动事件也只会有一份服务）
_MCP_STATE = {"started": False, "url": ""}


def event_mcp_启动服务(this):
    """
    启动 MCP 调试服务
    trigger: mcp_启动服务
    由 main.py 在 EventManager 创建后静默触发；config.json 的 mcp_enabled 控制总开关。
    本事件在主线程执行，可以 PRINT。
    """
    if _MCP_STATE["started"]:
        this.console.PRINT(f"MCP 调试服务已在运行: {_MCP_STATE['url']}", colors=(150, 150, 150))
        return

    config = getattr(this.console, 'config', {}) or {}
    if not config.get('mcp_enabled', False):
        return

    try:
        from mcp.server.mcpserver import MCPServer
    except ImportError:
        this.console.PRINT("MCP 依赖未安装（pip install mcp uvicorn），调试服务未启动", colors=(255, 200, 100))
        return

    host = str(config.get('mcp_host', '127.0.0.1'))
    try:
        port = int(config.get('mcp_port', 7310))
    except (TypeError, ValueError):
        port = 7310

    server = MCPServer(name="PeraGame")
    event_manager = this.event_manager
    registered = _register_event_tools(server, event_manager, this)

    if not registered:
        this.console.PRINT("MCP：没有找到任何挂 is_mcp_tool 属性的事件，服务未启动", colors=(255, 200, 100))
        return

    def _run():
        try:
            # stateless_http：无会话状态，多个客户端可随意并发连；json_response：纯 JSON 应答，兼容性最好
            server.run(transport="streamable-http",
                       host=host, port=port,
                       stateless_http=True, json_response=True)
        except (ValueError, TypeError):
            # 旧版 SDK 不支持这些参数时退回最简形式
            try:
                server.run(transport="streamable-http")
            except Exception as e:
                print(f"[MCP] 服务线程异常: {e}")
        except Exception as e:
            print(f"[MCP] 服务线程异常: {e}")

    threading.Thread(target=_run, daemon=True, name="pera-mcp").start()

    _MCP_STATE["started"] = True
    _MCP_STATE["url"] = f"http://{host}:{port}/mcp"
    this.console.PRINT(
        f"MCP 调试服务已启动: {_MCP_STATE['url']}  （已注册 {len(registered)} 个工具: {', '.join(registered)}）",
        colors=(100, 255, 100))

event_mcp_启动服务.event_trigger = "mcp_启动服务"


def _register_event_tools(server, event_manager, this_ref):
    """
    扫描 events_meta 中所有 is_mcp_tool 事件，为每个生成签名兼容的包装函数并注册为 MCP 工具。
    返回注册成功的工具名列表。
    """
    registered = []
    for event_key, meta in event_manager.events_meta.items():
        if not meta.get('is_mcp_tool'):
            continue
        event_func = event_manager.events.get(event_key)
        if event_func is None:
            continue

        # MCP 规范的工具名只允许 [a-zA-Z0-9_-]，中文事件名必须提供 ASCII 的 mcp_name
        tool_name = meta.get('mcp_name') or event_key
        description = meta.get('mcp_description', '') or (event_func.__doc__ or event_key)

        wrapper = _build_tool_wrapper(event_manager, this_ref, event_key, event_func)
        server.add_tool(wrapper, name=tool_name, description=description)
        registered.append(tool_name)
    return registered


def _build_tool_wrapper(event_manager, this_ref, event_key, event_func):
    """
    为事件函数生成 MCP 工具包装函数。

    事件签名是 def event_xxx(this, a=1, b="x")，MCP 客户端看到的是 tool(a=1, b="x")——
    去掉 this、复制参数名与默认值，重建一个签名干净的同形函数（FastMCP 依据签名生成 schema）。
    只复制名字和默认值、不复制类型注解，避免注解里出现 exec 命名空间解析不了的类型。
    """
    sig = inspect.signature(event_func)
    # 第一个参数固定是 this，跳过
    remaining = list(sig.parameters.values())[1:]

    parts = []
    names = []
    for p in remaining:
        if p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue  # *args/**kwargs 无法映射为工具参数，忽略
        if p.default is inspect.Parameter.empty:
            parts.append(p.name)
        else:
            parts.append(f"{p.name}={p.default!r}")
        names.append(p.name)

    param_src = ", ".join(parts)
    call_args = ", ".join(f"{n}={n}" for n in names)

    def _dispatch(**kwargs):
        # 所有工具调用的唯一入口：异常一律转字符串，绝不触发 trigger_event 的报错打印路径
        try:
            result = event_manager.trigger_event(event_key, this_ref, silent=True, **kwargs)
            if result is None:
                return f"[{event_key}] 无返回值"
            return result
        except Exception as e:
            return f"[{event_key}] 执行异常: {e}"

    namespace = {"_dispatch": _dispatch}
    source = f"def _tool({param_src}):\n    return _dispatch({call_args})\n"
    exec(source, namespace)
    return namespace["_tool"]


# ============================================================
# 以下是具体的 MCP 工具事件（挂 is_mcp_tool 属性即自动注册）
# ============================================================

def event_mcp_读取输出(this, lines=50, cursor=None):
    """
    读取游戏渲染前的文本输出（Go 管道式读取）。
    cursor 不传：返回最近 lines 行（tail 语义）；
    传入上次返回的 next_cursor：返回该位置之后的新增行（消费语义）。
    返回 {lines: ["#序号 文本", ...], next_cursor: 最新序号, total_in_buffer: 缓冲区总行数}。
    """
    try:
        lines = max(1, min(int(lines or 50), 1000))
    except (TypeError, ValueError):
        lines = 50
    try:
        cursor = int(cursor) if cursor is not None else None
    except (TypeError, ValueError):
        cursor = None

    # CPython 下 list() 拷贝期间主线程 append 是安全的；item 创建后不再被改写
    history = list(this.console.loader.history)

    if cursor is None:
        window = history[-lines:]
    else:
        window = [item for item in history if item.metadata.get('seq', 0) > cursor][-lines:]

    result_lines = []
    next_cursor = cursor or 0
    for item in window:
        seq = item.metadata.get('seq', 0)
        text = _item_to_text(item)
        if text:
            result_lines.append(f"#{seq} {text}")
        next_cursor = max(next_cursor, seq)

    return {
        "lines": result_lines,
        "next_cursor": next_cursor,
        "total_in_buffer": len(history),
    }


def _item_to_text(item):
    """把一条 ConsoleContent 转成人类可读的单行文本"""
    from dynamic_loader import ContentType
    if item.type == ContentType.IMAGE_MARK:
        return f"[图] {item.metadata.get('img_url', item.data)}"
    if item.type == ContentType.IMAGE_STACK:
        names = [e.get('name', '?') for e in item.metadata.get('img_elements', [])]
        return "[立绘叠加] " + " + ".join(names)
    return item.get_full_text()


def event_mcp_读取状态(this):
    """
    读取游戏状态快照：场景、时间、天气、主角位置与数值摘要、输出缓冲行数。
    用于排查事件逻辑问题（配合读取输出对照）。
    """
    # [allstate加冕] 运行时状态统一从 allstate 读取（System/positions 是唯一家）
    allstate = this.console.allstate if isinstance(this.console.allstate, dict) else {}
    system_state = allstate.get('System', {})
    positions = allstate.get('positions', {})
    master_pos = positions.get('0', {})

    master_allstate = allstate.get('0', {}) if isinstance(allstate.get('0', {}), dict) else {}
    master_summary = {}
    for k, v in master_allstate.items():
        if isinstance(v, (str, int, float, bool)) and len(master_summary) < 30:
            master_summary[k] = v

    return {
        "scene": system_state.get('SCENE', '日常'),
        "time": "{y}-{m}-{d} {h:02d}:{min:02d}".format(
            y=system_state.get('YEAR', 1), m=system_state.get('MONTH', 1), d=system_state.get('DAY', 1),
            h=_as_int(system_state.get('HOUR', 0)), min=_as_int(system_state.get('MINUTE', 0))),
        "total_minutes": _as_int(system_state.get('TOTAL_MINUTES', 0)),
        "weather": system_state.get('WEATHER', '未知'),
        "master": {
            "name": master_allstate.get('name', '0'),
            "小地图": master_pos.get('小地图', '?'),
            "大地图": master_pos.get('大地图', '?'),
            "地牢位置": master_pos.get('地牢位置', ''),
            "选择对象": system_state.get('选择对象', '0'),
            "allstate摘要": master_summary,
        },
        "history_lines": len(this.console.loader.history),
    }


def _as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def event_mcp_发送输入(this, text=""):
    """
    向游戏注入一条输入（等价于玩家键入后回车；传可点击文本的 click 值等价于点击）。
    注入后在下一次 INPUT 等待时生效（通常毫秒级延迟）。
    """
    text = str(text)
    if not text:
        return "错误: text 不能为空"
    this.console.mcp_input_queue.put(text)
    return f"已注入输入: {text!r}（将在游戏下一次 INPUT 等待时生效）"


# --- 工具属性注册（Eventmanger 会读取这些属性自动注册 MCP 工具） ---
event_mcp_读取输出.is_mcp_tool = True
event_mcp_读取输出.mcp_name = "pera_read_output"
event_mcp_读取输出.mcp_description = (
    "读取游戏渲染前的文本输出。参数 lines=读取行数(1-1000,默认50)；"
    "cursor=上次返回的next_cursor则只读新增行(增量模式)。返回含 next_cursor 供下次增量读取。")

event_mcp_读取状态.is_mcp_tool = True
event_mcp_读取状态.mcp_name = "pera_get_state"
event_mcp_读取状态.mcp_description = "读取游戏状态快照：场景/时间/天气/主角位置与数值摘要/输出缓冲行数。"

event_mcp_发送输入.is_mcp_tool = True
event_mcp_发送输入.mcp_name = "pera_send_input"
event_mcp_发送输入.mcp_description = "向游戏注入一条输入（等价于玩家回车提交；传选项click值等价于点击选项）。"
