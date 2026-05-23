# v6 场景选择架构 — LIFE_STATES 分层路由表

## 设计目标

让 cron 自动运行时生成的写真内容具有叙事逻辑：不是完全随机的场景拼接，而是基于"生活状态"的合理流动。

## 核心概念

### 生活状态（Life State）

每个生活状态包含：
- `weight`: cron 随机选择时的权重（越高越容易被选中）
- `time_range`: 时间范围 `("HH:MM", "HH:MM")`，None = 不限时间
- `weekdays_only`: True=仅工作日，False=仅周末，None=每天适用
- `scenes`: 候选场景列表，每个含 `scene`（场景文件名）和 `weight`（场景内权重）

### 两层随机

1. **第一层**：根据当前时间+工作日/周末筛选候选生活状态 → 按权重随机选一个
2. **第二层**：从已选生活状态的候选场景中，按场景权重随机选一个具体场景

## LIFE_STATES 结构

```python
LIFE_STATES = {
    # ── 工作日上午 (7:00-9:30) ──
    "weekday_morning": {
        "weight": 1.0,
        "time_range": ("07:00", "09:30"),
        "weekdays_only": True,
        "description": "工作日上午",
        "scenes": [
            {"scene": "bedroom", "weight": 4.0},     # 在家穿睡衣（最高概率）
            {"scene": "boulevard", "weight": 2.5},    # 通勤路上/校园林荫道
            {"scene": "cafe", "weight": 1.0},          # 早餐咖啡馆
        ],
    },

    # ── 工作日中午 (11:30-14:00) ──
    "weekday_noon": {
        "weight": 1.0,
        "time_range": ("11:30", "14:00"),
        "weekdays_only": True,
        "description": "工作日中午",
        "scenes": [
            {"scene": "cafe", "weight": 3.0},           # 午餐咖啡馆/食堂（最高概率）
            {"scene": "library", "weight": 2.0},         # 图书馆午休
            {"scene": "bedroom", "weight": 1.5},          # 回家午休
        ],
    },

    # ── 工作日下午 (14:30-17:30) ──
    "weekday_afternoon": {
        "weight": 1.0,
        "time_range": ("14:30", "17:30"),
        "weekdays_only": True,
        "description": "工作日下午",
        "scenes": [
            {"scene": "library", "weight": 4.0},         # 图书馆学习（最高概率）
            {"scene": "cafe", "weight": 2.5},             # 咖啡馆自习/休息
            {"scene": "boulevard", "weight": 1.5},        # 校园林荫道散步
        ],
    },

    # ── 工作日晚间 (18:00-21:30) ──
    "weekday_evening": {
        "weight": 1.0,
        "time_range": ("18:00", "21:30"),
        "weekdays_only": True,
        "description": "工作日晚间",
        "scenes": [
            {"scene": "cafe", "weight": 2.5},             # 晚餐/咖啡馆
            {"scene": "boulevard", "weight": 2.0},         # 校园散步
            {"scene": "library", "weight": 1.5},           # 图书馆自习
            {"scene": "rooftop", "weight": 1.0},           # 天台跑步/吹风
        ],
    },

    # ── 工作日深夜 (21:30-23:00) ──
    "weekday_night": {
        "weight": 1.0,
        "time_range": ("21:30", "23:00"),
        "weekdays_only": True,
        "description": "工作日深夜",
        "scenes": [
            {"scene": "bedroom", "weight": 5.0},           # 卧室睡衣（最高概率）
            {"scene": "cafe", "weight": 1.5},              # 深夜咖啡馆/自习室
            {"scene": "rooftop", "weight": 1.0},            # 天台夜景
        ],
    },

    # ── 周末上午 (9:00-14:00) ──
    "weekend_morning": {
        "weight": 1.0,
        "time_range": ("09:00", "14:00"),
        "weekdays_only": False,                         # 仅周末
        "description": "周末上午",
        "scenes": [
            {"scene": "bedroom", "weight": 3.0},           # 睡懒觉/在家
            {"scene": "park", "weight": 2.5},              # 公园晨练（最高概率）
            {"scene": "cafe", "weight": 2.0},              # Brunch 咖啡馆
        ],
    },

    # ── 周末下午 (14:00-23:00) ──
    "weekend_afternoon": {
        "weight": 1.0,
        "time_range": ("14:00", "23:00"),
        "weekdays_only": False,
        "description": "周末下午",
        "scenes": [
            {"scene": "park", "weight": 3.5},              # 公园散步/野餐（最高概率）
            {"scene": "rooftop", "weight": 2.0},            # 天台运动/休息
            {"scene": "cafe", "weight": 1.5},               # 咖啡馆下午茶
        ],
    },

    # ── 周末晚间 (18:00-23:00) ──
    "weekend_evening": {
        "weight": 1.0,
        "time_range": ("18:00", "23:00"),
        "weekdays_only": False,
        "description": "周末晚间",
        "scenes": [
            {"scene": "cafe", "weight": 2.5},              # 晚餐/约会咖啡馆（最高概率）
            {"scene": "rooftop", "weight": 2.0},            # 天台夜景
            {"scene": "boulevard", "weight": 1.5},          # 逛街散步
        ],
    },

    # ── 深夜 (23:00-7:00) ──
    "late_night": {
        "weight": 1.0,
        "time_range": ("23:00", "07:00"),
        "weekdays_only": None,                          # 每天适用（覆盖所有）
        "description": "深夜",
        "scenes": [
            {"scene": "bedroom", "weight": 5.0},           # 卧室睡衣（最高概率）
            {"scene": "cafe", "weight": 1.5},               # 深夜自习/咖啡馆
            {"scene": "rooftop", "weight": 1.0},            # 天台观星
        ],
    },

    # ── 旅行（独立状态，cron 可触发） ──
    "travel": {
        "weight": 0.2,                                  # 低频出现（周末上午/下午各约5-6%概率）
        "time_range": None,                              # 不限时间
        "weekdays_only": None,                           # 不限工作日
        "description": "旅行中",
        "scenes": [
            {"scene": "travel", "weight": 1.0},
        ],
    },
}
```

## 时段匹配逻辑

### 线性范围（start < end）

```python
if start_minutes <= current_minutes < end_minutes:
    match_time = True
```

示例：`("09:00", "14:00")` → 09:00-14:00 之间匹配

### 跨午夜范围（start > end）

```python
if start_minutes > end_minutes:
    match_time = (current_minutes >= start_minutes or current_minutes < end_minutes)
else:
    match_time = (start_minutes <= current_minutes < end_minutes)
```

示例：`("23:00", "07:00")` → 23:00-24:00 或 00:00-07:00 之间匹配

## 工作日/周末筛选

```python
if weekdays_only is True and not weekday:
    continue  # 仅工作日的状态，周末不匹配
elif weekdays_only is False and weekday:
    continue  # 仅周末的状态，工作日不匹配
```

`weekdays_only=None` → 每天都参与候选（如 late_night、travel）

## 随机选择算法

### 第一层：生活状态选择

1. 筛选所有满足时间+工作日约束的候选状态
2. 提取 `weight` 列表
3. `random.choices(keys, weights=weights, k=1)` → 加权随机选一个

### 第二层：场景选择

从已选生活状态的 `scenes` 列表中，按场景权重加权随机选一个。

## 调试方法

```bash
# 测试当前时间匹配的生活状态
python3 selfie-v6.py --life-state weekday_morning

# 指定场景（跳过生活状态）
python3 selfie-v6.py --scene cafe

# 模拟多次运行看分布
for i in {1..50}; do python3 selfie-v6.py --life-state weekend_morning; done | grep "场景"
```

## v5 → v6 变更

| 特性 | v5 (ROUTINES) | v6 (LIFE_STATES) |
|------|---------------|------------------|
| 结构 | 扁平字典，按季节×时段列出所有(场景,光线)元组 | 分层：生活状态→场景，两层权重随机 |
| 叙事性 | 无，完全随机 | 有，基于"我在哪"的生活逻辑 |
| 工作日/周末区分 | 无（ROUTINES 是季节固定的） | `weekdays_only` 字段控制 |
| 跨午夜支持 | 无 | `time_range` 特殊处理 start > end |
| 旅行状态 | ROUTINES 中分散在 night 时段 | 独立 LIFE_STATE，低权重始终参与候选 |

## 注意事项

- cron 自动运行时**不指定 --scene**，走 v6 两层随机选择
- 手动出图时可用 `--life-state weekend_morning` 调试特定生活状态
- `travel` 状态权重0.2确保低频出现（与其他生活状态同时匹配时约5-6%概率）
- late_night 跨午夜（23:00-07:00），需要特殊时间匹配逻辑
