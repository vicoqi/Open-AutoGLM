# PRD-001: WebSocket 服务器

## 需求概述

实现 WebSocket 服务器，提供手机自动化任务的控制接口，支持实时双向通信。

## 目标用户

- OpenClaw 系统
- 其他需要调用手机自动化的客户端

## 核心功能

### 1. WebSocket 连接管理
- 监听端口（默认 8765）
- 处理客户端连接/断开
- 心跳检测（30秒间隔）
- 连接数限制（最大 10 个并发）

### 2. 消息协议

**请求格式：**
```json
{
  "action": "execute",
  "task": "打开微信发送消息给张三",
  "device_id": "optional_device_id",
  "options": {}
}
```

**响应格式：**
```json
{
  "type": "progress|completed|error",
  "task_id": "uuid",
  "step": 1,
  "action": "tap",
  "thinking": "正在分析屏幕...",
  "timestamp": "2026-03-01T10:00:00Z"
}
```

### 3. 任务执行
- 接收任务请求
- 调用 PhoneAgent 执行
- 每一步实时推送进度
- 支持任务取消（Ctrl+C）

### 4. 错误处理
- 连接异常处理
- 任务执行失败处理
- 超时处理（默认 5 分钟）

## 技术规格

### 依赖库
- websockets >= 12.0
- python-dateutil
- Open-AutoGLM (本地路径)

### 配置项
```python
WEBSOCKET_PORT = 8765
MAX_CONNECTIONS = 10
HEARTBEAT_INTERVAL = 30  # 秒
TASK_TIMEOUT = 300  # 秒
```

### 接口清单
| 接口 | 方法 | 说明 |
|------|------|------|
| / | WebSocket | 主连接入口 |
| /health | HTTP GET | 健康检查 |

## 验收标准

- ✅ 可以通过 WebSocket 连接
- ✅ 可以发送任务并接收实时进度
- ✅ 任务完成后收到 completed 消息
- ✅ 任务失败时收到 error 消息
- ✅ 支持多个客户端同时连接
- ✅ 异常断开后自动清理资源

## 非功能性需求

- 性能：单任务执行延迟 < 100ms
- 可靠性：7x24 小时稳定运行
- 可维护性：代码注释覆盖率 > 30%

## 依赖条件

- Python 3.10+ 环境
- ADB/HDC 工具已安装
- 设备已连接并调试模式已开启
- Open-AutoGLM 项目可访问

## 风险和限制

- ⚠️ 单进程，不支持分布式
- ⚠️ 任务执行期间阻塞该连接
- ⚠️ MVP 版本无认证机制（仅本地使用）

## 交付物

1. websocket_handler.py
2. 配置文件 settings.py
3. 单元测试 test_websocket.py
4. API 文档 API.md

## 工期估算

**2 个工作日**

- Day 1: WebSocket 服务器开发 + 基本消息协议
- Day 2: 任务执行集成 + 测试 + 文档

## 后续迭代

- PRD-003: OpenClaw 集成
- 认证和安全机制
- 部署和监控系统
