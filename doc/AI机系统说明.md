# Pera幻想FOD - AI机系统完整说明文档

## 目录

1. [系统概述](#系统概述)
2. [设计理念](#设计理念)
3. [系统架构](#系统架构)
4. [核心组件详解](#核心组件详解)
5. [事件接口文档](#事件接口文档)
6. [使用指南](#使用指南)
7. [配置和自定义](#配置和自定义)
8. [实际应用案例](#实际应用案例)
9. [测试和调试](#测试和调试)
10. [扩展开发](#扩展开发)

---

## 系统概述

AI机系统是Pera幻想FOD中的角色AI决策系统，实现了基于花销计算的角色行为决策功能。每个角色都能根据当前状态、时间、天气、位置等因素，自主决定最优的行为策略。

### 主要功能

- **花销计算**：精确计算角色执行各种行为的资源消耗
- **行为决策**：基于多因素评分，为角色选择最优行为
- **时间同步**：与游戏时间系统同步，自动处理其他角色的行动
- **动态调整**：根据状态、天气、能力等因素动态调整花销和决策
- **扩展性强**：易于添加新行为、新修正规则和新的决策因素

### 适用场景

- 主角执行操作时，同步处理其他角色的行动
- 角色在空闲时自主决定行为
- 计算角色每日基础花销
- 检查角色是否能执行特定行为
- 获取角色可执行的所有行为列表

---

## 设计理念

### 核心原则

根据Pera幻想FOD设计思路文档，AI机系统遵循以下核心原则：

#### 1. 花销制度

```
每日花销 = 基础花销 × (1 + 负重系数) × (1 + 天气系数)
行为花销 = 基础花销 × (1 + 状态修正) × (1 + 天气修正) × (1 + 能力修正)
```

- 每个角色根据基础值计算每天的基础花销
- 行为花销包含时间消耗和三类资源消耗（体力、精力、灵力）

#### 2. 行为决策机制

```
决策评分 = 花销权重 × (1/总花销) + 时间权重 × (1/时间消耗) + 状态权重 × 状态适配度 + 偏好权重 × 行为偏好
```

每次Master执行操作时，角色们也会进行行动计算，选择当前花销最小的行为。

#### 3. 最优选择

角色总是选择当前条件下花销最低、时间最短、状态最适配的行为。

#### 4. 动态变化

花销会根据以下因素动态变化：
- 角色当前状态（正常、要睡觉、异常等）
- 当前天气（晴、阴、雨、雪）
- 角色能力等级
- 所在位置（房间、地牢等）

#### 5. 时间同步

```
一个时间单位的消耗 = 一次时间迭代 = Master操作消耗时间
```

把时间拆分成基础时间单位（分钟），一个时间单位的消耗看作是一次时间迭代。

---

## 系统架构

### 文件结构

```
events/角色AI机/
├── __init__.py              # 模块初始化，导出核心组件
├── cost_calculator.py       # 花销计算器模块
└── ai_core.py              # AI核心决策模块
```

### 模块关系图

```
┌─────────────────────────────────────────────────────────┐
│                     游戏主循环                            │
│                     (Game Main)                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ 触发事件
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Event Manager                          │
│                  (事件管理器)                             │
└──┬──────────────────────────────────────────┬───────────┘
   │                                          │
   │ trigger: cost_calculator                │ trigger: ai_core
   ▼                                          ▼
┌─────────────────────┐           ┌─────────────────────┐
│  CostCalculator     │           │     AICore          │
│  (花销计算器)        │           │   (AI核心决策)       │
├─────────────────────┤           ├─────────────────────┤
│ • 行为花销计算       │           │ • 行为决策评分       │
│ • 每日花销计算       │           │ • 角色状态评估       │
│ • 花销修正           │           │ • 最优行为选择       │
│ • 可执行行为查询     │           │ • 行为执行处理       │
└─────────────────────┘           └─────────────────────┘
```

### 数据流向

```
角色数据 → CostCalculator → 花销信息 → AICore → 行为决策 → 游戏系统
   ↓           ↓                ↓          ↓           ↓
基础值      修正因子          成本计算    评分计算    行为执行
当前状态    天气/状态          可执行性    最优选择    资源更新
能力等级    能力等级                                         
```

---

## 核心组件详解

### 1. 花销计算器 (CostCalculator)

#### 类结构

```python
class CostCalculator:
    """花销计算器 - 负责计算角色行为的资源消耗"""
    
    def __init__(self, event_manager):
        """初始化花销计算器"""
        
    def calculate(self, chara_id: str, action_id: str, context: dict = None) -> dict:
        """计算特定行为的详细花销"""
        
    def calculate_daily(self, chara_id: str) -> dict:
        """计算角色每日基础花销"""
        
    def get_available_actions(self, chara_id: str, location: str = None) -> list:
        """获取角色当前可执行的所有行为"""
        
    def apply_cost(self, chara_id: str, action_id: str) -> dict:
        """应用行为花销到角色（更新角色状态）"""
        
    def _apply_state_modifiers(...) -> tuple:
        """应用状态修正"""
        
    def _apply_weather_modifiers(...) -> tuple:
        """应用天气修正"""
        
    def _apply_ability_modifiers(...) -> tuple:
        """应用能力修正"""
        
    def _check_can_execute(...) -> bool:
        """检查角色是否能执行行为"""
```

#### 核心数据结构

**ActionCost（行为花销配置）**

```python
ActionCost = {
    '行为ID': {
        'name': '行为名称',           # 显示名称
        'time_cost': 时间消耗,        # 单位：分钟
        '体力消耗': 体力消耗值,        # 正数=消耗，负数=恢复
        '精力消耗': 精力消耗值,
        '灵力消耗': 灵力消耗值,
        'required_stats': {           # 需要的能力要求
            '能力名': 最小值
        },
        'required_location': ['位置1', '位置2'],  # 可选：限制位置
        'effects': ['效果1', '效果2'] # 行为效果描述
    }
}
```

**示例配置**

```python
ActionCost = {
    'rest': {
        'name': '休息',
        'time_cost': 30,
        '体力消耗': -50,      # 恢复体力
        '精力消耗': -30,
        '灵力消耗': 0,
        'effects': ['恢复体力', '恢复精力']
    },
    'explore': {
        'name': '探索',
        'time_cost': 15,
        '体力消耗': 20,
        '精力消耗': 10,
        '灵力消耗': 5,
        'effects': ['获得经验', '可能发现物品']
    }
}
```

#### 修正机制详解

**1. 状态修正**

- **要睡觉状态**（CFLAG:1 = 1）：所有行动花销 × 2
- **疲劳状态**：体力和精力消耗 + 20%
- **异常状态**：根据具体异常状态额外修正

**实现代码**：
```python
def _apply_state_modifiers(self, stamina_cost, energy_cost, spirit_cost, chara_state):
    """
    应用状态修正
    Args:
        stamina_cost: 原始体力消耗
        energy_cost: 原始精力消耗
        spirit_cost: 原始灵力消耗
        chara_state: 角色状态字典
    Returns:
        修正后的 (stamina_cost, energy_cost, spirit_cost)
    """
    # 检查是否要睡觉
    need_sleep = chara_state.get('CFLAG', {}).get('1', 0) == 1
    if need_sleep:
        stamina_cost *= 2
        energy_cost *= 2
        spirit_cost *= 2
    
    # 其他状态修正...
    
    return stamina_cost, energy_cost, spirit_cost
```

**2. 天气修正**

| 天气 | 体力消耗 | 精力消耗 | 灵力消耗 |
|------|----------|----------|----------|
| 晴 | 100% | 100% | 100% |
| 阴 | 110% | 110% | 110% |
| 雨 | 120% | 120% | 120% |
| 雪 | 130% | 130% | 130% |

**3. 能力修正**

能力等级越高，对应资源消耗越少：
```
消耗系数 = max(0.5, 1.0 - 能力等级 × 0.05)
```

例如：
- 能力等级 0：系数 = 1.0（无减免）
- 能力等级 5：系数 = 0.75（减免25%）
- 能力等级 10：系数 = 0.5（减免50%，最大减免）

#### 默认行为列表

| 行为ID | 行为名称 | 时间消耗 | 体力消耗 | 精力消耗 | 灵力消耗 | 位置限制 |
|--------|----------|----------|----------|----------|----------|----------|
| rest | 休息 | 30分钟 | -50 | -30 | 0 | 无 |
| explore | 探索 | 15分钟 | 20 | 10 | 5 | 非地牢 |
| combat | 战斗 | 10分钟 | 40 | 30 | 20 | 非地牢 |
| social | 社交 | 20分钟 | 5 | 10 | 5 | 无 |
| dungeon_explore | 地牢探索 | 20分钟 | 30 | 25 | 15 | 地牢 |
| dungeon_combat | 地牢战斗 | 15分钟 | 50 | 40 | 30 | 地牢 |
| move_small_map | 小地图移动 | 2分钟 | 2 | 1 | 0 | 无 |
| move_big_map | 大地图移动 | 10分钟 | 10 | 5 | 0 | 无 |
| shop | 商店交易 | 15分钟 | 2 | 5 | 0 | 商店 |
| sleep | 睡觉 | 480分钟 | -1000 | -1000 | -500 | 无 |

---

### 2. AI核心决策 (AICore)

#### 类结构

```python
class AICore:
    """AI核心 - 负责角色行为决策"""
    
    def __init__(self, event_manager):
        """初始化AI核心"""
        
    def make_decision(self, chara_id: str, context: dict = None) -> dict:
        """为单个角色做出行为决策"""
        
    def process_all_characters(self, context: dict = None, exclude_ids: list = None) -> list:
        """为所有角色做出行为决策"""
        
    def execute_action(self, chara_id: str, action_id: str) -> dict:
        """执行角色的行为"""
        
    def process_time_step(self, time_cost: float, context: dict = None, 
                         exclude_ids: list = None) -> list:
        """处理一个时间步长（同步其他角色）"""
        
    def _calculate_action_score(...) -> float:
        """计算行为的综合评分"""
        
    def _get_character_state(...) -> dict:
        """获取角色当前状态"""
        
    def _apply_time_modifiers(...) -> dict:
        """应用时间段修正"""
        
    def _apply_dungeon_modifiers(...) -> dict:
        """应用地牢修正"""
```

#### 决策评分机制

```
行为评分 = (
    花销评分 × 花销权重 +
    时间评分 × 时间权重 +
    状态评分 × 状态权重 +
    偏好评分 × 偏好权重 +
    时间段评分 × 时间段权重 +
    地牢评分 × 地牢权重
) × (1 + 随机浮动)
```

**各部分评分详解**：

1. **花销评分**：花销越低，评分越高
   ```
   花销评分 = 100 / (体力消耗 + 精力消耗 + 灵力消耗 + 10)
   ```

2. **时间评分**：时间越短，评分越高
   ```
   时间评分 = 100 / (时间消耗 + 5)
   ```

3. **状态评分**：当前状态适配度
   ```
   状态评分 = (体力适配度 + 精力适配度 + 灵力适配度) / 3
   
   体力适配度 = 
     如果体力 < 30%: 恢复行为=100, 消耗行为=0
     如果体力 > 70%: 恢复行为=20, 消耗行为=100
     其他: 50
   ```

4. **偏好评分**：基于角色性格类型

5. **时间段评分**：基于当前时间段的修正

6. **地牢评分**：地牢内探索优先

#### 角色性格类型

| 性格类型 | 探索 | 战斗 | 社交 | 休息 | 特点 |
|----------|------|------|------|------|------|
| 探索型 | 1.3 | 1.0 | 0.8 | 0.7 | 偏向探索和战斗 |
| 战斗型 | 0.9 | 1.5 | 0.7 | 0.6 | 偏向战斗 |
| 社交型 | 0.8 | 0.6 | 1.4 | 0.9 | 偏向社交和休息 |
| 保守型 | 0.7 | 0.6 | 1.1 | 1.3 | 偏向休息和社交 |

**获取角色性格**：
```python
# 从角色CFLAG获取性格类型
chara_state = this.console.init.chara_key[chara_id]['CFLAG']
personality = chara_state.get('性格', '探索型')  # 默认为探索型
```

#### 时间段修正

| 时间段 | 小时范围 | 探索 | 战斗 | 社交 | 休息 |
|--------|----------|------|------|------|------|
| 早晨 | 6-9 | +20% | -20% | +10% | +5% |
| 白天 | 9-18 | 0% | 0% | 0% | 0% |
| 傍晚 | 18-21 | -10% | -20% | +20% | +15% |
| 夜晚 | 21-6 | -30% | -40% | +10% | +50% |

#### 地牢修正

- 角色在地牢内时：
  - 地牢探索优先 + 50%
  - 地牢战斗优先 + 30%
  - 其他行为优先 - 20%

---

## 事件接口文档

### CostCalculator 事件接口

**事件名称**：`cost_calculator`

**Trigger格式**：
```python
this.event_manager.trigger_event(
    'cost_calculator',    # 事件名称
    this,                 # 事件上下文
    operation,            # 操作类型
    **kwargs              # 操作参数
)
```

#### 支持的操作

##### 1. calculate - 计算行为花销

**功能**：计算特定角色执行特定行为的详细花销信息

**参数**：
- `chara_id` (str, 必需)：角色ID
- `action_id` (str, 必需)：行为ID
- `context` (dict, 可选)：上下文信息
  - `weather` (str)：天气（晴/阴/雨/雪）
  - `hour` (int)：当前小时（0-23）

**返回值**：
```python
{
    'success': True,                    # 是否成功
    'action_id': 'explore',            # 行为ID
    'action_name': '探索',              # 行为名称
    'time_cost': 15.0,                 # 时间消耗（分钟）
    'stamina_cost': 20,                # 体力消耗
    'energy_cost': 10,                 # 精力消耗
    'spirit_cost': 5,                  # 灵力消耗
    'effects': ['获得经验', '可能发现物品'],  # 行为效果
    'can_execute': True,               # 是否可执行
    'reason': ''                       # 不能执行时的原因
}
```

**使用示例**：
```python
def event_check_cost(this):
    """检查角色探索的花销"""
    
    # 准备上下文
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR']
    }
    
    # 计算花销
    result = this.event_manager.trigger_event(
        'cost_calculator',
        this,
        'calculate',
        chara_id='1',
        action_id='explore',
        context=context
    )
    
    if result['success']:
        this.console.PRINT(f"行为: {result['action_name']}")
        this.console.PRINT(f"时间: {result['time_cost']}分钟")
        this.console.PRINT(f"体力: -{result['stamina_cost']}")
        this.console.PRINT(f"精力: -{result['energy_cost']}")
        this.console.PRINT(f"灵力: -{result['spirit_cost']}")
        this.console.PRINT(f"可执行: {'是' if result['can_execute'] else '否'}")
```

---

##### 2. daily - 计算每日花销

**功能**：计算角色每日基础花销

**参数**：
- `chara_id` (str, 必需)：角色ID

**返回值**：
```python
{
    'success': True,
    'chara_id': '0',
    'chara_name': '主角',
    'daily_stamina_cost': 10,      # 每日体力消耗
    'daily_energy_cost': 15,       # 每日精力消耗
    'daily_spirit_cost': 5,        # 每日灵力消耗
    'current_stamina': 100,        # 当前体力
    'current_energy': 100,         # 当前精力
    'current_spirit': 100          # 当前灵力
}
```

**使用示例**：
```python
def event_show_daily_cost(this):
    """显示角色每日花销"""
    
    result = this.event_manager.trigger_event(
        'cost_calculator',
        this,
        'daily',
        chara_id='1'
    )
    
    if result['success']:
        this.console.PRINT(f"角色: {result['chara_name']}")
        this.console.PRINT(f"每日基础消耗:")
        this.console.PRINT(f"  体力: {result['daily_stamina_cost']}")
        this.console.PRINT(f"  精力: {result['daily_energy_cost']}")
        this.console.PRINT(f"  灵力: {result['daily_spirit_cost']}")
```

---

##### 3. available - 获取可执行行为

**功能**：获取角色当前可执行的所有行为

**参数**：
- `chara_id` (str, 必需)：角色ID
- `location` (str, 可选)：当前位置（用于位置限制过滤）

**返回值**：
```python
{
    'success': True,
    'chara_id': '1',
    'chara_name': '角色名',
    'location': '房间1',
    'actions': [
        {
            'action_id': 'rest',
            'action_name': '休息',
            'time_cost': 30.0,
            'stamina_cost': -50,
            'energy_cost': -30,
            'spirit_cost': 0
        },
        # ... 更多可执行行为
    ]
}
```

**使用示例**：
```python
def event_show_available(this):
    """显示角色可执行的所有行为"""
    
    result = this.event_manager.trigger_event(
        'cost_calculator',
        this,
        'available',
        chara_id='1'
    )
    
    if result['success']:
        this.console.PRINT(f"角色: {result['chara_name']}")
        this.console.PRINT(f"可执行的行为:")
        for action in result['actions']:
            this.console.PRINT(f"  - {action['action_name']}: {action['time_cost']}分钟")
```

---

##### 4. apply - 应用花销到角色

**功能**：应用行为花销到角色，更新角色状态

**参数**：
- `chara_id` (str, 必需)：角色ID
- `action_id` (str, 必需)：行为ID

**返回值**：
```python
{
    'success': True,
    'chara_id': '1',
    'action_id': 'explore',
    'action_name': '探索',
    'cost_applied': {
        'time_cost': 15.0,
        'stamina_cost': 20,
        'energy_cost': 10,
        'spirit_cost': 5
    },
    'new_state': {
        'stamina': 80,
        'energy': 90,
        'spirit': 95
    }
}
```

**使用示例**：
```python
def event_apply_action(this):
    """执行角色行为"""
    
    result = this.event_manager.trigger_event(
        'cost_calculator',
        this,
        'apply',
        chara_id='1',
        action_id='explore'
    )
    
    if result['success']:
        cost = result['cost_applied']
        new_state = result['new_state']
        this.console.PRINT(f"角色执行了 {result['action_name']}")
        this.console.PRINT(f"消耗时间: {cost['time_cost']}分钟")
        this.console.PRINT(f"新体力: {new_state['stamina']}")
```

---

##### 5. reload - 重新加载花销配置

**功能**：重新加载行为花销配置（用于开发调试）

**参数**：无

**返回值**：
```python
{
    'success': True,
    'message': '花销配置已重新加载',
    'actions_count': 10
}
```

**使用示例**：
```python
def event_reload_config(this):
    """重新加载花销配置"""
    
    result = this.event_manager.trigger_event(
        'cost_calculator',
        this,
        'reload'
    )
    
    this.console.PRINT(result['message'])
```

---

### AICore 事件接口

**事件名称**：`ai_core`

**Trigger格式**：
```python
this.event_manager.trigger_event(
    'ai_core',            # 事件名称
    this,                 # 事件上下文
    operation,            # 操作类型
    **kwargs              # 操作参数
)
```

#### 支持的操作

##### 1. decide - 为角色决定行为

**功能**：为单个角色做出行为决策

**参数**：
- `chara_id` (str, 必需)：角色ID
- `context` (dict, 可选)：上下文信息
  - `weather` (str)：天气
  - `hour` (int)：当前小时
  - `location` (str)：当前位置

**返回值**：
```python
{
    'success': True,
    'decision': {
        'chara_id': '1',
        'chara_name': '角色名',
        'action_id': 'explore',
        'action_name': '探索',
        'cost_score': 25.5,
        'time_cost': 15.0,
        'stamina_cost': 20,
        'energy_cost': 10,
        'spirit_cost': 5,
        'reasoning': '选择探索，体力充沛，寻找机会',
        'priority': 80,
        'state': {
            'stamina_percent': 80,
            'energy_percent': 70,
            'spirit_percent': 90
        }
    }
}
```

**使用示例**：
```python
def event_make_decision(this):
    """为角色做决策"""
    
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR']
    }
    
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'decide',
        chara_id='1',
        context=context
    )
    
    if result['success']:
        decision = result['decision']
        this.console.PRINT(f"角色: {decision['chara_name']}")
        this.console.PRINT(f"决定: {decision['action_name']}")
        this.console.PRINT(f"理由: {decision['reasoning']}")
```

---

##### 2. process_all - 处理所有角色的决策

**功能**：为所有角色（或指定角色）做出行为决策

**参数**：
- `context` (dict, 可选)：上下文信息
- `exclude_ids` (list, 可选)：要排除的角色ID列表（如主角）
- `include_ids` (list, 可选)：只包含的角色ID列表（与exclude_ids互斥）

**返回值**：
```python
{
    'success': True,
    'decisions': [
        {
            'chara_id': '1',
            'chara_name': '角色1',
            'action_id': 'explore',
            'action_name': '探索',
            # ... 其他决策信息
        },
        {
            'chara_id': '2',
            'chara_name': '角色2',
            'action_id': 'rest',
            'action_name': '休息',
            # ... 其他决策信息
        }
    ],
    'total_count': 2
}
```

**使用示例**：
```python
def event_process_all(this):
    """处理所有角色的决策（排除主角）"""
    
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR']
    }
    
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'process_all',
        context=context,
        exclude_ids=['0']  # 排除主角
    )
    
    if result['success']:
        for decision in result['decisions']:
            this.console.PRINT(
                f"{decision['chara_name']} 将 {decision['action_name']}"
            )
```

---

##### 3. execute - 执行角色行为

**功能**：执行角色决定的行为（更新角色状态和时间）

**参数**：
- `chara_id` (str, 必需)：角色ID
- `action_id` (str, 必需)：行为ID

**返回值**：
```python
{
    'success': True,
    'chara_id': '1',
    'action_id': 'explore',
    'action_name': '探索',
    'executed': True,
    'time_passed': 15.0,
    'state_changes': {
        'stamina': -20,
        'energy': -10,
        'spirit': -5
    },
    'message': '角色1 执行了 探索'
}
```

**使用示例**：
```python
def event_execute_action(this):
    """执行角色的行为"""
    
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'execute',
        chara_id='1',
        action_id='explore'
    )
    
    if result['success'] and result['executed']:
        this.console.PRINT(result['message'])
        this.console.PRINT(f"消耗时间: {result['time_passed']}分钟")
```

---

##### 4. time_step - 处理时间步长

**功能**：在主角执行操作时，同步处理其他角色的行动

**参数**：
- `time_cost` (float, 必需)：时间消耗（分钟）
- `context` (dict, 可选)：上下文信息
- `exclude_ids` (list, 可选)：要排除的角色ID列表

**返回值**：
```python
{
    'success': True,
    'time_passed': 30.0,
    'processed_count': 2,
    'results': [
        {
            'chara_id': '1',
            'chara_name': '角色1',
            'decision': {
                'action_id': 'explore',
                'action_name': '探索',
                # ... 决策信息
            },
            'execution': {
                'executed': True,
                'time_passed': 15.0,
                'state_changes': {...}
            }
        },
        {
            'chara_id': '2',
            'chara_name': '角色2',
            'decision': {
                'action_id': 'rest',
                'action_name': '休息',
                # ... 决策信息
            },
            'execution': {
                'executed': True,
                'time_passed': 30.0,
                'state_changes': {...}
            }
        }
    ]
}
```

**使用示例**：
```python
def event_time_step(this):
    """处理时间步长"""
    
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR']
    }
    
    # 主角操作消耗30分钟，同步处理其他角色
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'time_step',
        time_cost=30,
        context=context,
        exclude_ids=['0']  # 排除主角
    )
    
    if result['success']:
        this.console.PRINT(f"经过时间: {result['time_passed']}分钟")
        this.console.PRINT(f"处理角色数: {result['processed_count']}")
        
        for action_result in result['results']:
            decision = action_result['decision']
            execution = action_result['execution']
            this.console.PRINT(
                f"{decision['chara_name']} {decision['action_name']} "
                f"({execution['time_passed']}分钟)"
            )
```

---

## 使用指南

### 基本使用流程

#### 1. 导入模块

```python
# 在事件文件中导入
from events.角色AI机 import cost_calculator, ai_core
```

#### 2. 初始化

AI机系统会在首次使用时自动初始化，无需手动初始化。

#### 3. 典型使用场景

**场景1：主角执行操作时同步其他角色**

```python
def event_explore(this):
    """主角探索场景"""
    
    # 显示主角探索
    this.console.PRINT("你开始探索周围...")
    
    # 准备上下文
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR'],
        'location': this.console.init.global_key['System']['LOCATION']
    }
    
    # 主角探索消耗15分钟
    time_cost = 15
    
    # 同步处理其他角色的行动
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'time_step',
        time_cost=time_cost,
        context=context,
        exclude_ids=['0']  # 排除主角
    )
    
    if result['success']:
        # 显示其他角色的行动
        this.console.PRINT("\n其他角色:")
        for action_result in result['results']:
            decision = action_result['decision']
            execution = action_result['execution']
            if execution['executed']:
                this.console.PRINT(
                    f"  {decision['chara_name']} 正在 {decision['action_name']}"
                )
```

**场景2：显示角色状态和决策**

```python
def event_show_ai_status(this):
    """显示所有角色的AI状态"""
    
    # 获取当前上下文
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR']
    }
    
    # 处理所有角色的决策
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'process_all',
        context=context,
        exclude_ids=['0']
    )
    
    if result['success']:
        this.console.PRINT("=== 角色AI状态 ===\n")
        
        for decision in result['decisions']:
            this.console.PRINT(f"角色: {decision['chara_name']}")
            
            # 显示当前状态
            state = decision['state']
            this.console.PRINT(f"  状态:")
            this.console.PRINT(f"    体力: {state['stamina_percent']}%")
            this.console.PRINT(f"    精力: {state['energy_percent']}%")
            this.console.PRINT(f"    灵力: {state['spirit_percent']}%")
            
            # 显示决策
            this.console.PRINT(f"  决策: {decision['action_name']}")
            this.console.PRINT(f"  理由: {decision['reasoning']}")
            this.console.PRINT("")
```

**场景3：检查角色是否能执行特定行为**

```python
def event_check_can_execute(this):
    """检查角色是否能执行地牢战斗"""
    
    chara_id = '1'
    action_id = 'dungeon_combat'
    
    # 计算行为花销
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR']
    }
    
    result = this.event_manager.trigger_event(
        'cost_calculator',
        this,
        'calculate',
        chara_id=chara_id,
        action_id=action_id,
        context=context
    )
    
    if result['success']:
        if result['can_execute']:
            this.console.PRINT(
                f"角色可以执行 {result['action_name']}\n"
                f"消耗: 时间{result['time_cost']}分钟, "
                f"体力-{result['stamina_cost']}, "
                f"精力-{result['energy_cost']}, "
                f"灵力-{result['spirit_cost']}"
            )
        else:
            this.console.PRINT(
                f"角色无法执行 {result['action_name']}\n"
                f"原因: {result['reason']}"
            )
```

### 在现有事件中集成AI机

#### 示例1：在移动事件中集成

```python
def event_move(this):
    """移动事件 - 集成AI机"""
    
    # 原有的移动逻辑
    # ... 移动处理代码 ...
    
    # 移动消耗2分钟
    time_cost = 2
    
    # 获取上下文
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR'],
        'location': this.console.init.global_key['System']['LOCATION']
    }
    
    # 同步其他角色
    this.event_manager.trigger_event(
        'ai_core',
        this,
        'time_step',
        time_cost=time_cost,
        context=context,
        exclude_ids=['0']
    )
    
    # ... 其他逻辑 ...
```

#### 示例2：在战斗事件中集成

```python
def event_combat(this):
    """战斗事件 - 集成AI机"""
    
    # 战斗消耗10分钟
    time_cost = 10
    
    # 获取上下文
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR'],
        'location': '地牢'
    }
    
    # 战斗前其他角色的反应
    this.event_manager.trigger_event(
        'ai_core',
        this,
        'time_step',
        time_cost=time_cost,
        context=context,
        exclude_ids=['0']
    )
    
    # 战斗处理
    # ... 战斗逻辑 ...
```

---

## 配置和自定义

### 添加新行为

#### 步骤1：定义行为配置

在 `cost_calculator.py` 的 `ActionCost` 字典中添加新行为：

```python
ActionCost = {
    # ... 现有行为 ...
    
    'craft_item': {
        'name': '制作道具',
        'time_cost': 60,
        '体力消耗': 40,
        '精力消耗': 30,
        '灵力消耗': 0,
        'required_stats': {
            '技巧': 30  # 需要技巧≥30
        },
        'effects': ['获得制作物品', '消耗材料']
    }
}
```

#### 步骤2：添加行为偏好（可选）

在 `ai_core.py` 的 `behavior_weights` 字典中为新行为添加偏好权重：

```python
self.behavior_weights = {
    '探索型': {
        # ... 现有权重 ...
        'craft_item': 0.8  # 探索型角色的制作权重
    },
    '战斗型': {
        # ... 现有权重 ...
        'craft_item': 0.5
    },
    '社交型': {
        # ... 现有权重 ...
        'craft_item': 0.9
    },
    '保守型': {
        # ... 现有权重 ...
        'craft_item': 1.1  # 保守型角色更喜欢制作
    }
}
```

#### 步骤3：添加时间段修正（可选）

在 `_apply_time_modifiers` 方法中添加：

```python
if time_period == 'evening':  # 傍晚
    modifiers['craft_item'] = 1.2  # 傍晚制作+20%
```

### 自定义花销修正

#### 添加新的状态修正

在 `_apply_state_modifiers` 方法中添加：

```python
def _apply_state_modifiers(self, stamina_cost, energy_cost, spirit_cost, chara_state):
    """应用状态修正"""
    
    # 原有逻辑...
    
    # 添加新状态：疲劳状态
    is_fatigued = chara_state.get('CFLAG', {}).get('疲劳', 0) == 1
    if is_fatigued:
        stamina_cost *= 1.3  # 疲劳体力消耗+30%
        energy_cost *= 1.2
    
    return stamina_cost, energy_cost, spirit_cost
```

#### 添加新的天气修正

在 `_apply_weather_modifiers` 方法中添加：

```python
weather_modifiers = {
    '晴': {'stamina': 1.0, 'energy': 1.0, 'spirit': 1.0},
    '阴': {'stamina': 1.1, 'energy': 1.1, 'spirit': 1.1},
    '雨': {'stamina': 1.2, 'energy': 1.2, 'spirit': 1.2},
    '雪': {'stamina': 1.3, 'energy': 1.3, 'spirit': 1.3},
    '台风': {'stamina': 1.5, 'energy': 1.4, 'spirit': 1.2}  # 新增
}
```

#### 添加新的能力修正

在 `_apply_ability_modifiers` 方法中添加：

```python
# 添加新能力：体力能力影响体力消耗
stamina_ability = chara_state.get('ABL', {}).get('体力', 0)
stamina_cost *= max(0.5, 1.0 - stamina_ability * 0.05)

# 添加新能力：精力能力影响精力消耗
energy_ability = chara_state.get('ABL', {}).get('精力', 0)
energy_cost *= max(0.5, 1.0 - energy_ability * 0.05)

# 添加新能力：灵力能力影响灵力消耗
spirit_ability = chara_state.get('ABL', {}).get('灵力', 0)
spirit_cost *= max(0.5, 1.0 - spirit_ability * 0.05)
```

### 自定义AI决策

#### 添加新的性格类型

在 `ai_core.py` 的初始化中添加新性格：

```python
self.behavior_weights = {
    # ... 现有性格 ...
    '冒险型': {
        '探索': 1.4,
        '战斗': 1.3,
        '地牢探索': 1.5,
        '地牢战斗': 1.4,
        '社交': 0.6,
        '休息': 0.5
    },
    '学术型': {
        '探索': 0.8,
        '战斗': 0.5,
        '社交': 1.2,
        'rest': 1.3,
        'craft_item': 1.4
    }
}
```

#### 自定义决策评分权重

修改 `_calculate_action_score` 方法中的权重：

```python
# 原有权重
weights = {
    'cost': 0.4,      # 花销权重
    'time': 0.2,      # 时间权重
    'state': 0.25,    # 状态权重
    'preference': 0.15  # 偏好权重
}

# 自定义权重（例如更重视偏好）
weights = {
    'cost': 0.3,      # 降低花销权重
    'time': 0.15,     # 降低时间权重
    'state': 0.25,    # 保持状态权重
    'preference': 0.3  # 提高偏好权重
}
```

#### 添加新的决策因素

例如添加"角色关系"因素：

```python
def _calculate_action_score(self, chara_id, action_id, action_cost, 
                           chara_state, context):
    """计算行为的综合评分"""
    
    # ... 原有计算 ...
    
    # 添加关系因素
    relationship_score = self._calculate_relationship_score(
        chara_id, action_id
    )
    
    # 更新总评分
    weights['relationship'] = 0.1
    action_score += weights['relationship'] * relationship_score
    
    return action_score

def _calculate_relationship_score(self, chara_id, action_id):
    """
    计算关系评分
    社交行为时，关系好的角色会有更高评分
    """
    if action_id == 'social':
        # 获取角色关系数据
        # 这里需要根据实际数据结构实现
        # 返回 0-100 的评分
        return 80
    
    return 50
```

---

## 实际应用案例

### 案例1：完整的日常循环事件

```python
def event_daily_cycle(this):
    """角色日常循环事件"""
    
    # 获取所有角色
    chara_ids = this.console.init.global_key['System']['CHARA_LIST']
    
    # 排除主角
    other_charas = [cid for cid in chara_ids if cid != '0']
    
    # 准备上下文
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR'],
        'location': this.console.init.global_key['System']['LOCATION']
    }
    
    this.console.PRINT("=== 角色日常行动 ===\n")
    
    # 为每个角色决定行动
    for chara_id in other_charas:
        # 决策
        result = this.event_manager.trigger_event(
            'ai_core',
            this,
            'decide',
            chara_id=chara_id,
            context=context
        )
        
        if result['success']:
            decision = result['decision']
            chara_name = decision['chara_name']
            action_name = decision['action_name']
            reasoning = decision['reasoning']
            
            this.console.PRINT(f"{chara_name}:")
            this.console.PRINT(f"  行动: {action_name}")
            this.console.PRINT(f"  理由: {reasoning}")
            
            # 执行行动
            exec_result = this.event_manager.trigger_event(
                'ai_core',
                this,
                'execute',
                chara_id=chara_id,
                action_id=decision['action_id']
            )
            
            if exec_result['success'] and exec_result['executed']:
                time_passed = exec_result['time_passed']
                this.console.PRINT(f"  耗时: {time_passed}分钟\n")
```

### 案例2：地牢探索事件

```python
def event_dungeon_explore(this):
    """地牢探索事件"""
    
    # 设置位置为地牢
    this.console.init.global_key['System']['LOCATION'] = '地牢'
    
    # 地牢探索参数
    max_time = 180  # 最多探索180分钟（3小时）
    elapsed_time = 0
    
    this.console.PRINT("进入地牢...")
    this.console.PRINT(f"其他角色也在行动中...\n")
    
    # 准备上下文
    context = {
        'weather': '未知',
        'hour': this.console.init.global_key['System']['HOUR'],
        'location': '地牢'
    }
    
    # 探索循环
    while elapsed_time < max_time:
        # 主角探索一次，消耗20分钟
        explore_time = 20
        elapsed_time += explore_time
        
        # 处理其他角色在地牢的行动
        result = this.event_manager.trigger_event(
            'ai_core',
            this,
            'time_step',
            time_cost=explore_time,
            context=context,
            exclude_ids=['0']
        )
        
        if result['success']:
            # 显示其他角色的行动
            this.console.PRINT(f"\n经过{explore_time}分钟:")
            for action_result in result['results']:
                decision = action_result['decision']
                execution = action_result['execution']
                if execution['executed']:
                    this.console.PRINT(
                        f"  {decision['chara_name']} "
                        f"{decision['action_name']}"
                    )
        
        # 检查是否应该退出
        # ... 检查逻辑 ...
    
    this.console.PRINT("\n地牢探索结束")
```

### 案例3：商店交易事件

```python
def event_shop_transaction(this):
    """商店交易事件"""
    
    this.console.PRINT("欢迎来到商店！")
    
    # 交易消耗15分钟
    transaction_time = 15
    
    # 准备上下文
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR'],
        'location': '商店'
    }
    
    # 在主角交易时，其他角色也在行动
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'time_step',
        time_cost=transaction_time,
        context=context,
        exclude_ids=['0']
    )
    
    if result['success']:
        this.console.PRINT(f"\n交易时间: {transaction_time}分钟")
        this.console.PRINT("其他角色:")
        
        for action_result in result['results']:
            decision = action_result['decision']
            execution = action_result['execution']
            if execution['executed']:
                this.console.PRINT(
                    f"  {decision['chara_name']} {decision['action_name']}"
                )
    
    # 显示商店菜单
    # ... 商店逻辑 ...
```

### 案例4：睡眠事件

```python
def event_sleep(this):
    """睡眠事件"""
    
    chara_id = '0'  # 主角
    
    # 睡觉消耗480分钟（8小时）
    sleep_time = 480
    
    this.console.PRINT("你决定睡觉休息...")
    
    # 准备上下文
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR'],
        'location': this.console.init.global_key['System']['LOCATION']
    }
    
    # 其他角色在主角睡觉时的行动
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'time_step',
        time_cost=sleep_time,
        context=context,
        exclude_ids=['0']
    )
    
    if result['success']:
        this.console.PRINT(f"\n经过 {sleep_time} 分钟...")
        this.console.PRINT("其他角色的行动:")
        
        for action_result in result['results']:
            decision = action_result['decision']
            execution = action_result['execution']
            if execution['executed']:
                this.console.PRINT(
                    f"  {decision['chara_name']} {decision['action_name']}"
                )
    
    # 应用主角睡觉的恢复效果
    sleep_result = this.event_manager.trigger_event(
        'cost_calculator',
        this,
        'apply',
        chara_id=chara_id,
        action_id='sleep'
    )
    
    if sleep_result['success']:
        cost = sleep_result['cost_applied']
        this.console.PRINT(f"\n体力恢复: +{abs(cost['stamina_cost'])}")
        this.console.PRINT(f"精力恢复: +{abs(cost['energy_cost'])}")
        this.console.PRINT(f"灵力恢复: +{abs(cost['spirit_cost'])}")
    
    this.console.PRINT("你醒来，感到精力充沛！")
```

---

## 测试和调试

### 测试事件

AI机系统提供了三个测试事件：

#### 1. test_ai - 全面测试

```python
def event_test_ai(this):
    """全面测试AI决策功能"""
    
    this.console.PRINT("=== AI机系统测试 ===\n")
    
    # 测试1：计算行为花销
    this.console.PRINT("【测试1】计算行为花销")
    result = this.event_manager.trigger_event(
        'cost_calculator',
        this,
        'calculate',
        chara_id='1',
        action_id='explore',
        context={'weather': '晴', 'hour': 12}
    )
    
    if result['success']:
        this.console.PRINT(f"行为: {result['action_name']}")
        this.console.PRINT(f"时间: {result['time_cost']}分钟")
        this.console.PRINT(f"花销: 体力-{result['stamina_cost']}, "
                          f"精力-{result['energy_cost']}, "
                          f"灵力-{result['spirit_cost']}")
    
    # 测试2：计算每日花销
    this.console.PRINT("\n【测试2】计算每日花销")
    result = this.event_manager.trigger_event(
        'cost_calculator',
        this,
        'daily',
        chara_id='1'
    )
    
    if result['success']:
        this.console.PRINT(f"角色: {result['chara_name']}")
        this.console.PRINT(f"每日消耗: "
                          f"体力{result['daily_stamina_cost']}, "
                          f"精力{result['daily_energy_cost']}, "
                          f"灵力{result['daily_spirit_cost']}")
    
    # 测试3：AI决策
    this.console.PRINT("\n【测试3】AI决策")
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'decide',
        chara_id='1',
        context={'weather': '晴', 'hour': 12}
    )
    
    if result['success']:
        decision = result['decision']
        this.console.PRINT(f"角色: {decision['chara_name']}")
        this.console.PRINT(f"决定: {decision['action_name']}")
        this.console.PRINT(f"理由: {decision['reasoning']}")
    
    # 测试4：处理所有角色
    this.console.PRINT("\n【测试4】处理所有角色")
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'process_all',
        context={'weather': '晴', 'hour': 12},
        exclude_ids=['0']
    )
    
    if result['success']:
        for decision in result['decisions']:
            this.console.PRINT(
                f"{decision['chara_name']}: {decision['action_name']}"
            )
    
    this.console.PRINT("\n=== 测试完成 ===")
```

#### 2. ai_status - 显示AI状态

```python
def event_ai_status(this):
    """显示所有角色的AI状态"""
    
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR']
    }
    
    result = this.event_manager.trigger_event(
        'ai_core',
        this,
        'process_all',
        context=context,
        exclude_ids=['0']
    )
    
    if result['success']:
        this.console.PRINT("=== 角色AI状态 ===\n")
        
        for decision in result['decisions']:
            this.console.PRINT(f"角色: {decision['chara_name']}")
            
            state = decision['state']
            this.console.PRINT(f"  状态:")
            this.console.PRINT(f"    体力: {state['stamina_percent']}%")
            this.console.PRINT(f"    精力: {state['energy_percent']}%")
            this.console.PRINT(f"    灵力: {state['spirit_percent']}%")
            
            this.console.PRINT(f"  决策: {decision['action_name']}")
            this.console.PRINT(f"  理由: {decision['reasoning']}")
            this.console.PRINT("")
```

#### 3. ai_info - 显示系统说明

```python
def event_ai_info(this):
    """显示AI机系统说明"""
    
    this.console.PRINT("=== AI机系统说明 ===")
    this.console.PRINT("")
    this.console.PRINT("AI机系统是角色AI决策系统，实现以下功能:")
    this.console.PRINT("  • 花销计算: 计算角色行为的资源消耗")
    this.console.PRINT("  • 行为决策: 基于多因素评分选择最优行为")
    this.console.PRINT("  • 时间同步: 与游戏时间系统同步")
    this.console.PRINT("  • 动态调整: 根据状态、天气等因素调整")
    this.console.PRINT("")
    this.console.PRINT("事件接口:")
    this.console.PRINT("  • cost_calculator: 花销计算")
    this.console.PRINT("    - calculate: 计算行为花销")
    this.console.PRINT("    - daily: 计算每日花销")
    this.console.PRINT("    - available: 获取可执行行为")
    this.console.PRINT("    - apply: 应用花销到角色")
    this.console.PRINT("")
    this.console.PRINT("  • ai_core: AI决策")
    this.console.PRINT("    - decide: 为角色决定行为")
    this.console.PRINT("    - process_all: 处理所有角色")
    this.console.PRINT("    - execute: 执行角色行为")
    this.console.PRINT("    - time_step: 处理时间步长")
    this.console.PRINT("")
    this.console.PRINT("详细文档请查看: doc/AI机系统说明.md")
```

### 调试技巧

#### 1. 查看角色详细状态

```python
def event_debug_chara_state(this):
    """调试：查看角色详细状态"""
    
    chara_id = '1'
    chara = this.console.init.chara_key[chara_id]
    
    this.console.PRINT(f"=== 角色{chara_id}详细状态 ===")
    this.console.PRINT(f"名字: {chara['NAME']}")
    this.console.PRINT(f"体力: {chara['体力']}/{chara['体力上限']}")
    this.console.PRINT(f"精力: {chara['精力']}/{chara['精力上限']}")
    this.console.PRINT(f"灵力: {chara['灵力']}/{chara['灵力上限']}")
    
    # 查看能力
    if 'ABL' in chara:
        this.console.PRINT(f"\n能力值:")
        for abl_name, abl_value in chara['ABL'].items():
            this.console.PRINT(f"  {abl_name}: {abl_value}")
    
    # 查看状态标志
    if 'CFLAG' in chara:
        this.console.PRINT(f"\n状态标志:")
        for flag_name, flag_value in chara['CFLAG'].items():
            this.console.PRINT(f"  CFLAG:{flag_name} = {flag_value}")
```

#### 2. 查看行为配置

```python
def event_debug_action_config(this):
    """调试：查看所有行为配置"""
    
    from events.角色AI机.cost_calculator import ActionCost
    
    this.console.PRINT("=== 行为配置 ===\n")
    
    for action_id, action_info in ActionCost.items():
        this.console.PRINT(f"行为ID: {action_id}")
        this.console.PRINT(f"  名称: {action_info['name']}")
        this.console.PRINT(f"  时间: {action_info['time_cost']}分钟")
        this.console.PRINT(f"  体力: {action_info['体力消耗']}")
        this.console.PRINT(f"  精力: {action_info['精力消耗']}")
        this.console.PRINT(f"  灵力: {action_info['灵力消耗']}")
        
        if 'effects' in action_info:
            this.console.PRINT(f"  效果: {', '.join(action_info['effects'])}")
        
        this.console.PRINT("")
```

#### 3. 测试特定行为

```python
def event_debug_test_action(this):
    """调试：测试特定行为"""
    
    chara_id = '1'
    action_id = 'dungeon_combat'
    
    # 计算花销
    context = {
        'weather': this.console.init.global_key['System']['WEATHER'],
        'hour': this.console.init.global_key['System']['HOUR']
    }
    
    this.console.PRINT(f"=== 测试行为: {action_id} ===\n")
    
    result = this.event_manager.trigger_event(
        'cost_calculator',
        this,
        'calculate',
        chara_id=chara_id,
        action_id=action_id,
        context=context
    )
    
    if result['success']:
        this.console.PRINT(f"行为: {result['action_name']}")
        this.console.PRINT(f"可执行: {result['can_execute']}")
        this.console.PRINT(f"\n消耗:")
        this.console.PRINT(f"  时间: {result['time_cost']}分钟")
        this.console.PRINT(f"  体力: {result['stamina_cost']}")
        this.console.PRINT(f"  精力: {result['energy_cost']}")
        this.console.PRINT(f"  灵力: {result['spirit_cost']}")
        
        if result['effects']:
            this.console.PRINT(f"\n效果:")
            for effect in result['effects']:
                this.console.PRINT(f"  • {effect}")
```

---

## 扩展开发

### 扩展1：添加角色互动行为

实现角色之间的互动行为，如聊天、合作等。

```python
# 在ActionCost中添加互动行为
ActionCost = {
    # ... 现有行为 ...
    
    'chat_with': {
        'name': '与角色聊天',
        'time_cost': 30,
        '体力消耗': 5,
        '精力消耗': 15,
        '灵力消耗': 0,
        'required_stats': {},
        'effects': ['提升好感度', '交流信息']
    },
    
    'cooperate': {
        'name': '合作行动',
        'time_cost': 45,
        '体力消耗': 30,
        '精力消耗': 20,
        '灵力消耗': 10,
        'required_stats': {},
        'effects': ['提升团队配合', '共享经验']
    }
}

# 在AI决策中添加互动评分
def _calculate_interaction_score(self, chara_id, action_id):
    """计算互动行为评分"""
    if action_id in ['chat_with', 'cooperate']:
        # 获取角色关系数据
        # 根据好感度返回评分
        return 75
    
    return 50
```

### 扩展2：实现目标系统

为角色添加短期和长期目标，影响行为决策。

```python
# 目标数据结构
CharacterGoals = {
    '1': {  # 角色ID
        'current_goal': '探索地牢',
        'goals': [
            {
                'name': '探索地牢',
                'priority': 90,
                'deadline': 10  # 10天内完成
            },
            {
                'name': '提升战斗能力',
                'priority': 70,
                'deadline': 30
            }
        ]
    }
}

# 在AI决策中添加目标影响
def _calculate_goal_score(self, chara_id, action_id, chara_goals):
    """计算目标对行为的影响"""
    if not chara_goals:
        return 50
    
    current_goal = chara_goals.get('current_goal', '')
    priority = chara_goals.get('priority', 50)
    
    # 根据目标和行为的关系返回评分
    goal_action_map = {
        '探索地牢': ['explore', 'dungeon_explore', 'dungeon_combat'],
        '提升战斗能力': ['combat', 'dungeon_combat'],
        '收集物品': ['explore', 'shop'],
        '社交': ['social', 'chat_with']
    }
    
    if current_goal in goal_action_map:
        if action_id in goal_action_map[current_goal]:
            return priority * 1.5  # 目标相关行为评分提升
    
    return 50
```

### 扩展3：实现情绪系统

添加角色情绪状态，影响行为决策和花销。

```python
# 情绪数据结构
CharacterEmotions = {
    '1': {
        'current': '快乐',
        'intensity': 0.7,  # 0.0-1.0
        'history': []  # 情绪历史
    }
}

# 情绪对花销的影响
emotion_modifiers = {
    '快乐': {'stamina': 0.9, 'energy': 1.1, 'spirit': 1.0},
    '愤怒': {'stamina': 1.2, 'energy': 0.8, 'spirit': 1.1},
    '悲伤': {'stamina': 1.1, 'energy': 0.7, 'spirit': 0.9},
    '平静': {'stamina': 1.0, 'energy': 1.0, 'spirit': 1.0}
}

# 在花销计算中应用情绪修正
def _apply_emotion_modifiers(self, stamina_cost, energy_cost, spirit_cost, chara_id):
    """应用情绪修正"""
    # 获取角色情绪
    emotion = CharacterEmotions.get(chara_id, {})
    current_emotion = emotion.get('current', '平静')
    intensity = emotion.get('intensity', 0.5)
    
    # 获取情绪修正
    modifiers = emotion_modifiers.get(current_emotion, 
                                     emotion_modifiers['平静'])
    
    # 应用修正（考虑情绪强度）
    stamina_cost *= 1.0 + (modifiers['stamina'] - 1.0) * intensity
    energy_cost *= 1.0 + (modifiers['energy'] - 1.0) * intensity
    spirit_cost *= 1.0 + (modifiers['spirit'] - 1.0) * intensity
    
    return stamina_cost, energy_cost, spirit_cost
```

### 扩展4：实现学习机制

角色根据历史行为和结果，调整行为偏好。

```python
# 学习数据结构
CharacterLearning = {
    '1': {
        'action_history': {
            'explore': {
                'count': 10,
                'success_count': 8,
                'total_reward': 150
            },
            'combat': {
                'count': 5,
                'success_count': 4,
                'total_reward': 100
            }
        },
        'learned_preferences': {
            'explore': 1.2,  # 通过学习获得的偏好修正
            'combat': 1.1
        }
    }
}

# 计算学习偏好
def _calculate_learned_preference(self, chara_id, action_id):
    """计算学习到的偏好"""
    learning = CharacterLearning.get(chara_id, {})
    action_history = learning.get('action_history', {})
    
    if action_id not in action_history:
        return 1.0  # 默认值
    
    history = action_history[action_id]
    
    # 成功率
    success_rate = history['success_count'] / history['count']
    
    # 平均奖励
    avg_reward = history['total_reward'] / history['count']
    
    # 学习评分：成功率 × 平均奖励的某种组合
    learned_score = success_rate * (avg_reward / 10)
    
    # 转换为偏好修正系数
    return min(max(0.5, 1.0 + (learned_score - 5) * 0.1), 2.0)

# 更新学习数据
def update_learning_data(self, chara_id, action_id, success, reward):
    """更新角色学习数据"""
    if chara_id not in CharacterLearning:
        CharacterLearning[chara_id] = {
            'action_history': {},
            'learned_preferences': {}
        }
    
    learning = CharacterLearning[chara_id]
    history = learning['action_history']
    
    if action_id not in history:
        history[action_id] = {
            'count': 0,
            'success_count': 0,
            'total_reward': 0
        }
    
    # 更新统计数据
    history[action_id]['count'] += 1
    if success:
        history[action_id]['success_count'] += 1
    history[action_id]['total_reward'] += reward
    
    # 重新计算偏好
    learned_pref = self._calculate_learned_preference(chara_id, action_id)
    learning['learned_preferences'][action_id] = learned_pref
```

---

## 技术说明

### Python版本

- **使用Python 3.13.x语法**
- 利用类型提示提高代码可读性
- 使用数据类（dataclass）简化数据结构

### Pera框架接口

- 通过 `this.event_manager.trigger_event()` 进行事件通信
- 通过 `this.console.init.global_key['System']` 访问全局变量
- 通过 `this.console.init.chara_key[chara_id]` 访问角色数据
- 通过 `this.console.PRINT()` 输出文本

### 代码规范

- 所有注释均为中文
- 遵循PEP 8代码风格
- 函数和类均有详细的文档字符串
- 使用有意义的变量名和函数名

### 性能优化建议

1. **缓存计算结果**：对于不常变化的数据（如每日花销）可以缓存
2. **批量处理**：处理多个角色时尽量使用 `process_all` 而非循环调用 `decide`
3. **避免重复计算**：在单次决策中复用已计算的值
4. **限制查询深度**：在获取角色数据时只获取必要字段

---

## 注意事项

### 1. 时间同步

- 确保在主角执行操作时调用AI系统处理其他角色的行动
- 使用 `time_step` 操作可以自动处理时间同步
- 注意角色时间消耗不应超过主角时间消耗

### 2. 资源限制

- 角色无法执行资源不足的行为
- 检查 `can_execute` 字段判断是否可执行
- 负值表示恢复，正值表示消耗

### 3. 状态修正

- 要睡觉状态（CFLAG:1 = 1）会使所有花销翻倍
- 异常状态会影响可执行行为列表
- 优先检查状态后再进行决策

### 4. 地牢行为

- 地牢内角色的行为偏好会有所不同
- 地牢行为有位置限制
- 注意区分探索和地牢探索

### 5. 随机性

- AI决策包含少量随机因素，避免完全确定性
- 随机浮动范围：±10%
- 可通过调整随机浮动大小控制随机性

### 6. 数据一致性

- 确保角色数据结构的完整性
- 修改角色数据后及时同步
- 定期检查数据有效性

### 7. 错误处理

- 检查返回值的 `success` 字段
- 处理角色不存在的情况
- 处理行为不存在的情况

---

## 常见问题 (FAQ)

### Q1: 如何添加新的行为类型？

A: 在 `cost_calculator.py` 的 `ActionCost` 字典中添加新行为配置，然后在 `ai_core.py` 的 `behavior_weights` 中为不同性格类型设置偏好权重。

### Q2: 如何修改角色的性格？

A: 通过修改角色的 `CFLAG` 中的性格标志：
```python
this.console.init.chara_key[chara_id]['CFLAG']['性格'] = '探索型'
```

### Q3: AI决策过于随机，如何减少随机性？

A: 在 `_calculate_action_score` 方法中调整随机浮动范围：
```python
random_fluctuation = random.uniform(-0.05, 0.05)  # 缩小范围
action_score *= (1.0 + random_fluctuation)
```

### Q4: 如何让角色优先执行特定行为？

A: 提高该行为的偏好权重，或在决策前设置临时目标：
```python
# 设置临时目标
CharacterGoals[chara_id]['current_goal'] = '探索地牢'
CharacterGoals[chara_id]['priority'] = 100
```

### Q5: 如何查看角色当前的状态？

A: 使用调试事件或直接访问角色数据：
```python
chara = this.console.init.chara_key[chara_id]
print(f"体力: {chara['体力']}/{chara['体力上限']}")
print(f"CFLAG: {chara['CFLAG']}")
```

### Q6: 角色无法执行行为，如何查找原因？

A: 检查以下几点：
1. 资源是否充足（体力、精力、灵力）
2. 是否满足能力要求
3. 位置是否匹配
4. 是否处于限制状态

### Q7: 如何禁用某个角色的AI决策？

A: 在调用 `process_all` 或 `time_step` 时将该角色ID加入 `exclude_ids` 列表。

### Q8: AI机系统会影响性能吗？

A: AI机系统性能开销较小，但建议：
- 避免在每一帧都调用
- 批量处理多个角色
- 缓存计算结果

---

## 未来扩展计划

- [ ] 添加角色相性影响花销
- [ ] 实现角色之间的互动行为
- [ ] 添加更多行为类型（如学习、工作等）
- [ ] 实现角色学习机制（根据历史数据调整决策）
- [ ] 添加角色情绪系统
- [ ] 实现角色目标系统（短期/长期目标）
- [ ] 添加角色记忆系统
- [ ] 实现角色关系网络
- [ ] 添加角色职业系统
- [ ] 实现角色技能系统

---

## 版本历史

### v1.0.0 (当前版本)

- 实现基础花销计算系统
- 实现AI核心决策系统
- 支持10种默认行为
- 支持4种性格类型
- 提供完整的事件接口
- 提供测试事件
- 提供完整文档

---

## 联系和支持

如有问题或建议，请查看：
- 项目文档：doc/
- 示例代码：events/test_ai.py
- 设计思路：Pera幻想FOD设计思路.txt

---

**文档版本**: 1.0.0  
**最后更新**: 2025-12-30  
**作者**: Pera开发团队
