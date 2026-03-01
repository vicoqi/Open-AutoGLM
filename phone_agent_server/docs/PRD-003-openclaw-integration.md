# PRD-003: OpenClaw 集成

## 需求概述

在 skill 中集成 Phone Agent client，让用户可以通过自然语言控制手机。

## 核心功能

### 1. Skill 开发
- 创建 phone-control skill
- 支持自然语言调用
- 使用typescript开发

### 2. WebSocket 客户端
- 连接到 Phone Agent Server
- 发送任务请求
- 接收实时进度
- 处理连接异常

### 3. 用户交互流程

**用户说：**
> "用手机打开微信，给张三发消息说会议改到3点"

**大模型 处理：**
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

### 参考
现在python 代码客户端连接Phone Agent Server，使用方式如下：
`python3 phone_agent_server/examples/simple_client.py "给微信好友Chip 发送一个笑话"`
