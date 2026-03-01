# PRD-003: OpenClaw 集成

## 需求概述

在 OpenClaw 中集成 Phone Agent Server，让用户可以通过自然语言控制手机。

## 核心功能

### 1. OpenClaw Skill 开发
- 创建 phone-control skill
- 注册为 OpenClaw 工具
- 支持自然语言调用

### 2. WebSocket 客户端
- 连接到 Phone Agent Server
- 发送任务请求
- 接收实时进度
- 处理连接异常

### 3. 用户交互流程

**用户说：**
> "用手机打开微信，给张三发消息说会议改到3点"

**OpenClaw 处理：**
1. 识别意图（手机控制）
2. 调用 phone-control skill
3. 连接 WebSocket
4. 发送任务
5. 实时反馈进度
6. 返回结果

**用户看到：**
```
✅ 正在执行：打开微信...
✅ 点击联系人：张三
✅ 输入消息：会议改到3点
✅ 任务完成
```

### 4. 错误处理
- 连接失败提示
- 任务失败提示
- 超时提示
- 设备未连接提示

## 技术规格

### Skill 配置
```json
{
  "name": "phone-control",
  "description": "控制手机执行自动化任务",
  "tools": ["execute_phone_task"],
  "triggers": ["手机", "phone", "安卓"]
}
```

### 工具定义
```python
def execute_phone_task(task: str, device_id: str = None):
    """
    执行手机自动化任务
    
    参数:
        task: 任务描述（自然语言）
        device_id: 设备ID（可选）
    
    返回:
        执行结果和进度信息
    """
```

### WebSocket 客户端逻辑
1. 建立连接
2. 发送任务
3. 循环接收消息
4. 解析进度并返回
5. 直到收到 completed 或 error

## 验收标准

- ✅ 用户可以通过自然语言调用
- ✅ 实时看到任务执行进度
- ✅ 任务完成后收到明确反馈
- ✅ 错误时有清晰的错误信息
- ✅ 支持取消正在执行的任务

## 非功能性需求

- 响应时间：首次连接 < 1 秒
- 易用性：无需用户了解 WebSocket
- 可靠性：自动重连机制

## 依赖条件

- PRD-001 已完成（WebSocket 服务器）
- Phone Agent Server 正在运行

## 交付物

1. phone-control skill（SKILL.md）
2. openclaw_integration.py（客户端）
3. 使用示例文档
4. 测试用例

## 工期估算

**1-2 个工作日**

- Day 1: WebSocket 客户端开发
- Day 2: Skill 集成 + 测试

## 示例场景

### 场景 1：简单任务
```
用户：用手机打开微信
OpenClaw：✅ 已打开微信
```

### 场景 2：复杂任务
```
用户：打开淘宝搜索"机械键盘"，按价格排序
OpenClaw：
  ✅ 打开淘宝
  ✅ 搜索：机械键盘
  ✅ 按价格排序
  ✅ 找到 50 个商品
```

### 场景 3：错误处理
```
用户：用手机打电话给李四
OpenClaw：❌ 任务失败：未找到联系人"李四"
```

## 后续迭代

- 支持多设备选择
- 任务历史查询
- 定时任务
