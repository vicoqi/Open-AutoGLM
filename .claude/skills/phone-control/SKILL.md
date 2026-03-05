---
name: phone-control
description: Control Android/HarmonyOS/iOS phones through natural language commands. Use when the user wants to (1) Execute phone automation tasks, (2) Open apps, send messages, or perform actions on a phone, (3) Get real-time progress updates during task execution. Triggers: "用手机...", "打开手机上的...", "在手机上执行...", "控制手机...", "use phone to...", "on my phone..."
---

# Phone Control Skill

WebSocket client for executing phone automation tasks through the Phone Agent Server.

## Overview

This skill provides a TypeScript WebSocket client that connects to a Phone Agent Server to execute automation tasks on connected devices.

**Supported Platforms:** Android, HarmonyOS, iOS

## Script Directory

**Agent Execution**:
1. `SKILL_DIR` = this SKILL.md file's directory
2. Script path = `${SKILL_DIR}/scripts/main.ts`

## Quick Start

```bash
# Execute a task (no npm install needed - bun handles dependencies automatically)
npx -y bun ${SKILL_DIR}/scripts/main.ts "打开微信"
```

## Usage

### Command Line

```bash
# Default server (ws://localhost:8765)
npx -y bun ${SKILL_DIR}/scripts/main.ts "task description"

# Custom server
npx -y bun ${SKILL_DIR}/scripts/main.ts "打开微信" ws://192.168.1.100:8765
```

## Examples

```bash
# Open app
npx -y bun ${SKILL_DIR}/scripts/main.ts "打开微信"

# Send message
npx -y bun ${SKILL_DIR}/scripts/main.ts "在微信里给张三发消息说明天开会"

# Search
npx -y bun ${SKILL_DIR}/scripts/main.ts "在淘宝搜索iPhone手机壳"

# System settings
npx -y bun ${SKILL_DIR}/scripts/main.ts "打开设置，调低屏幕亮度"
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `PHONE_AGENT_WS_URI` | `ws://localhost:8765` | Server URI |

## Files

| File | Description |
|------|-------------|
| `${SKILL_DIR}/scripts/main.ts` | TypeScript WebSocket client |
| `${SKILL_DIR}/scripts/package.json` | Dependencies (bun auto-installs) |
| `${SKILL_DIR}/references/api.md` | Complete API reference |

## API Reference

See [${SKILL_DIR}/references/api.md](references/api.md) for message formats, response types, and error handling.
