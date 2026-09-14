# MCP 调试接口

> 2026-09-14 实现。游戏运行时内嵌一个 MCP 服务器，AI 客户端（ZCode / Claude 等）可以
> **读取游戏渲染前的文本输出、读取状态快照、向游戏注入输入**——不截图、不人肉复述，
> 实现"AI 写口上 → AI 自己跑游戏验证"的闭环。

---

## 架构

```
AI 客户端 (ZCode / Claude / 测试脚本)
   │  MCP streamable-http（无会话状态，纯 JSON 应答）
   │  http://127.0.0.1:7310/mcp
   ▼
MCP 服务线程（daemon，mcp 2.x MCPServer + uvicorn）
   │  工具调用 → 签名复制的包装函数 → event_manager.trigger_event(事件名, this, silent=True)
   ▼
Pera 事件系统（events/调试相关/MCP接口.py 中的 event_* 函数）
   │  读取：console.loader.history（渲染前文本，每条带单调 seq 序号）
   │  注入：console.mcp_input_queue → INPUT() 循环每帧轮询 → _commit_input()
   ▼
游戏主线程（pygame 渲染全程不被 MCP 线程触碰）
```

**线程安全铁律**：MCP 工具事件在 MCP 线程里被调用，因此：
1. 绝不 PRINT / 绘制 / 播放音乐（pygame 非线程安全）；
2. 只允许：读取数据（CPython 下 list/dict 拷贝边写边读安全）或入队（queue.Queue 线程安全）；
3. 异常返回错误字符串，不外抛。

---

## 配置（config.json）

```json
{
    "mcp_enabled": true,       // 总开关；发布 exe 时设 false 即完全关闭（无线程无端口）
    "mcp_host": "127.0.0.1",   // 只绑本机，不做认证
    "mcp_port": 7310
}
```

启动方式：随游戏自动启动（main.py 在 EventManager 创建后静默触发 `mcp_启动服务` 事件）。
依赖：`pip install mcp uvicorn`（已加入 requirements.txt）。

---

## 三个内置工具

| 工具名 | 事件名 | 参数 | 说明 |
|---|---|---|---|
| `pera_read_output` | mcp_读取输出 | `lines`(1-1000,默认50)、`cursor`(可选) | 读取渲染前文本。不传 cursor=尾部 N 行(tail)；传上次返回的 next_cursor=只读新增行(Go 管道消费语义)。图片行显示为 `[图] 名称` / `[立绘叠加] a + b`。游标用每条记录的单调 seq，history 万条截断后依然正确 |
| `pera_get_state` | mcp_读取状态 | 无 | 场景/时间/天气/主角位置与数值摘要/输出缓冲行数 |
| `pera_send_input` | mcp_发送输入 | `text` | 等价于玩家键入后回车；传可点击文本的 click 值等价于点击选项。在游戏下一次 INPUT 等待时生效（通常毫秒级） |

返回值统一为 JSON（AI 客户端直接可读）。

---

## 如何暴露新的 MCP 工具（框架扩展点）

**写一个普通 Pera 事件，挂三个属性即可**，服务启动时会自动扫描注册：

```python
def event_mcp_读取存档列表(this, 存档数=3):
    """这里写工具描述（会展示给 AI 客户端）"""
    # 铁律：不 PRINT，只读数据，异常转字符串返回
    return ["save_1.json", "save_2.json"]

event_mcp_读取存档列表.is_mcp_tool = True                              # 标记为 MCP 工具
event_mcp_读取存档列表.mcp_name = "pera_list_saves"                    # ASCII 工具名（MCP 规范要求）
event_mcp_读取存档列表.mcp_description = "读取存档列表，参数 存档数=数量"  # 展示给 AI 的说明
```

- 事件第一个参数 `this` 由框架自动传入，**其余参数会成为 MCP 工具的参数**（名字+默认值被复制成工具 schema，中文参数名可用但建议英文）；
- `mcp_name` 必须是 `[a-zA-Z0-9_-]`（中文事件名不能直接当工具名）；
- 注册机制在 `Eventmanger.py` 的 load_events 循环（与 `is_main_event` 同一模式），工具枚举在 `events/调试相关/MCP接口.py` 的 `_register_event_tools`。

---

## AI 客户端接入示例

ZCode / Claude 等支持 HTTP MCP 的客户端，添加服务器地址：

```
http://127.0.0.1:7310/mcp
```

命令行验证（项目自带测试客户端，覆盖三个工具的完整闭环）：

```shell
python main.py                          # 终端1：启动游戏
.venv/Scripts/python tools/mcp测试客户端.py   # 终端2：跑验证
```

---

## 设计备注

- **为什么是 HTTP 不是 stdio**：游戏运行时 stdout 有约 50 处 print 污染（配置回显、异常 traceback、pygame greeting），stdio JSON-RPC 会被搅乱。
- **为什么 stateless + json_response**：无会话状态，多个客户端（测试脚本 + AI 客户端）可随意并发连接；纯 JSON 应答兼容性最好。
- **为什么游标用 seq 而不是数组下标**：loader.history 有 10000 条截断，绝对下标会漂移；seq 是 `_append_history` 统一写入时打的单调序号，截断不影响。
- **输入注入的覆盖面**：游戏所有阻塞点最终都是 `console.INPUT()`，INPUT 循环顶部每帧轮询注入队列（60fps），一处钩子全覆盖；游戏连续 PRINT 不在 INPUT 时指令排队等待（毫秒级）。
- **热重载**：`reload` 事件重载后再次触发 `mcp_启动服务` 不会重复起服务（模块级 `_MCP_STATE` 守护），但新增的 MCP 工具要重启游戏才会注册。
- **已知边界**：`mcp<2`（1.x FastMCP）API 不同，本项目按 mcp 2.x（MCPServer）编写，requirements 已钉 `mcp>=2.0`。
