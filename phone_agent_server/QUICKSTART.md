# Quick Start Guide - Phone Agent WebSocket Server

## 快速开始指南

本指南帮助您快速启动和测试 Phone Agent WebSocket Server。

## 前置条件

1. ✅ Python 3.10+ 已安装
2. ✅ 虚拟环境已创建并激活
3. ✅ 依赖已安装 (`pip3 install -r requirements.txt`)
4. ✅ 手机已通过 ADB/HDC 连接
5. ✅ 模型服务器正在运行

## 步骤 1: 验证安装

```bash
# 激活虚拟环境
source venv/bin/activate

# 测试模块导入
python3 -c "from phone_agent_server import server; print('✓ 安装成功')"
```

## 步骤 2: 配置环境变量

### 方法 1: 使用 .env 文件（推荐）

```bash
# 1. 复制示例配置文件
cp .env.example .env

# 2. 编辑 .env 文件，修改配置
nano .env  # 或使用你喜欢的编辑器
```

**.env 文件示例**:
```bash
# WebSocket 服务器配置
PHONE_AGENT_WS_HOST=0.0.0.0
PHONE_AGENT_WS_PORT=8765

# 模型配置（本地模型服务）
PHONE_AGENT_BASE_URL=http://localhost:8000/v1
PHONE_AGENT_MODEL=autoglm-phone-9b
PHONE_AGENT_API_KEY=EMPTY

# 或使用智谱 BigModel
# PHONE_AGENT_BASE_URL=https://open.bigmodel.cn/api/paas/v4
# PHONE_AGENT_MODEL=autoglm-phone
# PHONE_AGENT_API_KEY=your-api-key-here

# 设备配置
PHONE_AGENT_DEVICE_TYPE=adb
PHONE_AGENT_LANG=cn
```

### 方法 2: 使用环境变量（临时）

```bash
# WebSocket 服务器配置
export PHONE_AGENT_WS_HOST="0.0.0.0"
export PHONE_AGENT_WS_PORT="8765"

# 模型配置（使用本地模型服务）
export PHONE_AGENT_BASE_URL="http://localhost:8000/v1"
export PHONE_AGENT_MODEL="autoglm-phone-9b"
export PHONE_AGENT_API_KEY="EMPTY"

# 设备配置
export PHONE_AGENT_DEVICE_TYPE="adb"  # 或 "hdc"
export PHONE_AGENT_LANG="cn"
```

**注意**: 如果不配置，将使用默认值。

## 步骤 3: 启动服务器

```bash
# 从项目根目录启动
python3 -m phone_agent_server.server
```

**预期输出**:
```
INFO:phone_agent_server.server:Phone Agent WebSocket Server starting...
INFO:phone_agent_server.server:Model: autoglm-phone-9b at http://localhost:8000/v1
INFO:phone_agent_server.server:Device type: adb
INFO:phone_agent_server.server:Language: cn
INFO:phone_agent_server.server:Starting WebSocket server on ws://0.0.0.0:8765
INFO:phone_agent_server.server:WebSocket server started on ws://0.0.0.0:8765
```

## 步骤 4: 测试连接（新终端）

```bash
# 激活虚拟环境
source venv/bin/activate

# 测试基本连接
python3 phone_agent_server/examples/test_connection.py
```

**预期输出**:
```
Phone Agent WebSocket Server - Connection Test
============================================================
Testing connection to ws://localhost:8765...
✓ Connected successfully!

Testing ping...
✓ Ping/pong successful!

✓ All tests passed!
```

## 步骤 5: 执行简单任务

```bash
# 执行一个简单的任务
python3 phone_agent_server/examples/simple_client.py "打开微信"
```

**预期输出**:
```
Phone Agent WebSocket Client
============================================================
Connecting to ws://localhost:8765...
Connected!

Sending task: 打开微信

Receiving responses:
------------------------------------------------------------

[Step 1]
Action: Launch
Thinking: 正在启动微信应用...

[Step 2]
Action: Wait
Thinking: 等待应用加载...

✓ Task completed!
Total steps: 2
Result: {'success': True, 'total_steps': 2}
------------------------------------------------------------
```

## 常见问题

### 问题 1: 服务器无法启动

**错误**: `Address already in use`

**解决方案**:
```bash
# 检查端口占用
lsof -i :8765

# 使用不同端口
export PHONE_AGENT_WS_PORT="8766"
python3 -m phone_agent_server.server
```

### 问题 2: 连接被拒绝

**错误**: `Connection refused`

**检查清单**:
- [ ] 服务器是否正在运行？
- [ ] 端口号是否正确？
- [ ] 防火墙是否阻止连接？

### 问题 3: 设备未找到

**错误**: `Device not found`

**解决方案**:
```bash
# 检查设备连接
adb devices  # Android
hdc list targets  # HarmonyOS

# 重启 ADB/HDC
adb kill-server && adb start-server
hdc kill && hdc start
```

### 问题 4: 模型服务器错误

**错误**: `Model API error`

**检查清单**:
- [ ] 模型服务器是否运行？ `curl http://localhost:8000/v1/models`
- [ ] BASE_URL 是否正确？
- [ ] API_KEY 是否正确？

## 下一步

### 1. 编写自定义客户端

参考 `phone_agent_server/examples/simple_client.py` 编写您自己的客户端。

### 2. 查看 API 文档

详细的 API 文档: `phone_agent_server/docs/API.md`

### 3. 运行集成测试

```bash
# 确保服务器正在运行
python3 tests/test_websocket_integration.py
```

### 4. 集成到 OpenClaw

参考 PRD-003 文档了解如何集成到 OpenClaw。

## 停止服务器

在服务器终端按 `Ctrl+C` 优雅关闭服务器。

**预期输出**:
```
INFO:phone_agent_server.server:Received exit signal SIGINT
INFO:phone_agent_server.server:Shutting down server...
INFO:phone_agent_server.server:Closing 0 active connections
INFO:phone_agent_server.server:Server shutdown complete
```

## 获取帮助

- **文档**: `phone_agent_server/README.md`
- **API 参考**: `phone_agent_server/docs/API.md`
- **实现细节**: `phone_agent_server/IMPLEMENTATION.md`
- **问题反馈**: GitHub Issues

---

**提示**: 首次运行建议使用简单任务（如"打开微信"）测试，确认一切正常后再尝试复杂任务。
