# CLAUDE.md

Open-AutoGLM 项目开发指南

---

## 项目概述

Open-AutoGLM 是 AI 驱动的手机自动化框架，使用视觉语言模型理解屏幕内容并通过自然语言执行任务。

**支持平台**:
- Android (ADB)
- HarmonyOS (HDC)
- iOS (WebDriverAgent)

**核心流程**: 截图 → 视觉模型分析 → 生成动作 → 执行 → 循环

---

## Python 环境规范

### 命令使用规则（重要）

| 环境 | 使用命令 | 不要使用 |
|------|---------|---------|
| 系统环境 | `python` | `python3` |
| 虚拟环境（激活后） | `python3`, `pip3` | `python`, `pip` |

**示例**:
```bash
# 创建虚拟环境（在系统环境中）
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖（在虚拟环境中）
pip3 install -r requirements.txt

# 运行脚本（在虚拟环境中）
python3 script.py
```

---

## 快速开始

### 环境设置

```bash
# 1. 创建虚拟环境（系统环境）
python -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖（虚拟环境）
pip3 install -r requirements.txt
pip3 install -e .
```

### 运行（在虚拟环境中）

```bash
# Android
python3 main.py --base-url http://localhost:8000/v1 --model "autoglm-phone-9b"

# HarmonyOS
python3 main.py --device-type hdc --base-url http://localhost:8000/v1

# iOS
python3 ios.py --wda-url http://localhost:8100

# 使用第三方 API
python3 main.py --base-url https://open.bigmodel.cn/api/paas/v4 --model "autoglm-phone" --apikey "your-key" "任务"
```

### 设备管理

```bash
# 检查设备
adb devices              # Android
hdc list targets         # HarmonyOS
idevice_id -l            # iOS

# 列出支持的应用（在虚拟环境中）
python3 main.py --list-apps
```

---

## 架构

```
CLI Layer (main.py, ios.py)
    ↓
Agent Layer (PhoneAgent, IOSPhoneAgent)
    ↓
Model Layer (ModelClient)
    ↓
Action Layer (ActionHandler)
    ↓
Device Factory Layer (DeviceFactory)
    ↓
Device Control Layer (adb/, hdc/, xctest/)
```

---

## 核心模式

### 1. Device Factory Pattern

```python
from phone_agent.device_factory import DeviceType, set_device_type, get_device_factory

set_device_type(DeviceType.ADB)  # or HDC, IOS
device_factory = get_device_factory()
screenshot = device_factory.get_screenshot(device_id)
```

### 2. Configuration (Dataclasses)

```python
from phone_agent.model import ModelConfig
from phone_agent.agent import AgentConfig

model_config = ModelConfig(
    base_url="http://localhost:8000/v1",
    model_name="autoglm-phone-9b",
    api_key="EMPTY"
)

agent_config = AgentConfig(
    max_steps=100,
    device_id=None,
    lang="cn",
    verbose=True
)
```

### 3. Callbacks

```python
def confirmation_callback(message: str) -> bool:
    return input(f"Confirm: {message}? (y/n): ").lower() == "y"

def takeover_callback(message: str) -> None:
    print(f"Manual action required: {message}")
    input("Press Enter when done...")

agent = PhoneAgent(
    confirmation_callback=confirmation_callback,
    takeover_callback=takeover_callback
)
```

---

## 环境变量

| Variable | Default | Description |
|----------|---------|-------------|
| `PHONE_AGENT_BASE_URL` | `http://localhost:8000/v1` | 模型 API 地址 |
| `PHONE_AGENT_MODEL` | `autoglm-phone-9b` | 模型名称 |
| `PHONE_AGENT_API_KEY` | `EMPTY` | API 密钥 |
| `PHONE_AGENT_DEVICE_TYPE` | `adb` | 设备类型 (adb/hdc/ios) |
| `PHONE_AGENT_LANG` | `cn` | 语言 (cn/en) |
| `PHONE_AGENT_MAX_STEPS` | `100` | 最大步骤数 |

---

## Phone Agent Server (WebSocket API)

**位置**: `/phone_agent_server/`

**用途**: 为 Open-AutoGLM 提供 WebSocket API，支持远程控制。

**状态**: ✅ MVP 完成 (2026-03-01)

### 快速启动

```bash
# 启动服务器
python3 -m phone_agent_server.server

# 测试连接
python3 phone_agent_server/examples/test_connection.py

# 执行任务
python3 phone_agent_server/examples/simple_client.py "打开微信"
```

### 配置

```bash
export PHONE_AGENT_WS_HOST="0.0.0.0"
export PHONE_AGENT_WS_PORT="8765"
export PHONE_AGENT_WS_MAX_CONNECTIONS="10"
```

### 文档

- `phone_agent_server/README.md` - 使用文档
- `phone_agent_server/QUICKSTART.md` - 快速开始
- `phone_agent_server/docs/API.md` - API 参考

---

## 项目结构

```
phone_agent/
├── agent.py             # PhoneAgent 主类
├── agent_ios.py         # IOSPhoneAgent
├── device_factory.py    # 设备工厂
├── adb/                 # Android 控制
├── hdc/                 # HarmonyOS 控制
├── xctest/              # iOS 控制
├── actions/             # 动作处理
├── config/              # 配置文件
│   ├── apps.py          # Android 应用映射
│   ├── apps_harmonyos.py
│   ├── apps_ios.py
│   ├── prompts_zh.py    # 中文提示词
│   └── prompts_en.py    # 英文提示词
└── model/               # 模型客户端

main.py                  # Android/HarmonyOS 入口
ios.py                   # iOS 入口

phone_agent_server/      # WebSocket 服务器
├── server.py
├── websocket_handler.py
├── task_executor.py
├── message_protocol.py
├── config.py
└── examples/
```

---

## 常见问题

### 设备未找到

```bash
adb kill-server && adb start-server
hdc kill && hdc start
```

### Android 无法点击

在开发者选项中启用:
- USB 调试
- USB 调试（安全设置）

### Android 文本输入不工作

```bash
# 安装并启用 ADB Keyboard
adb shell ime enable com.android.adbkeyboard/.AdbIME
```

### iOS WebDriverAgent 未运行

1. 在 Xcode 中打开 WebDriverAgent.xcodeproj
2. 配置签名
3. 运行 WebDriverAgentRunner (Cmd+U)
4. 端口转发: `iproxy 8100 8100`

---

## 开发指南

### 添加新功能

1. **设备特定代码**: 添加到 `adb/`, `hdc/`, `xctest/`
2. **跨平台功能**: 添加到 `device_factory.py`
3. **新动作**: 添加到 `actions/handler.py`
4. **配置**: 使用 `@dataclass`
5. **应用映射**: 更新 `apps*.py`

### 测试方法

- 使用简单测试类（不继承 unittest）
- 使用 `logger` 而非 assertions
- 使用真实配置，不用 mocks
- 通过 `if __name__ == '__main__':` 执行

### 代码风格

- 使用类型提示
- 添加文档字符串
- 遵循 snake_case 命名
- 保持设备特定逻辑隔离

---

## 参考

- **主 README**: 完整用户文档
- **iOS 设置**: `docs/ios_setup/ios_setup.md`
- **模型仓库**: https://github.com/zai-org/GLM-V
- **论文**: AutoGLM (arXiv:2411.00820)

---

*最后更新: 2026-03-01*
