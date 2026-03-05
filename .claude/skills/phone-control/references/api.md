# Phone Agent WebSocket API Reference

Complete API documentation for the Phone Agent WebSocket Server.

## Connection

### Endpoint

```
ws://host:port/
```

**Default:** `ws://localhost:8765/`

### Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `PHONE_AGENT_WS_HOST` | `0.0.0.0` | Server host address |
| `PHONE_AGENT_WS_PORT` | `8765` | Server port |
| `PHONE_AGENT_WS_MAX_CONNECTIONS` | `10` | Max concurrent connections |
| `PHONE_AGENT_WS_HEARTBEAT_INTERVAL` | `30` | Heartbeat interval (seconds) |
| `PHONE_AGENT_WS_TASK_TIMEOUT` | `300` | Task timeout (seconds) |

## Request Messages

### Execute Task

Execute a phone automation task.

```json
{
  "action": "execute",
  "task": "打开微信发送消息给张三",
  "device_id": "optional_device_id",
  "options": {}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | Yes | Must be `"execute"` |
| `task` | string | Yes | Task description in natural language |
| `device_id` | string | No | Specific device ID to use |
| `options` | object | No | Additional options (reserved) |

### Ping

Test connection and keep alive.

```json
{
  "action": "ping"
}
```

### Cancel Task

Request cancellation of current task (limited support in MVP).

```json
{
  "action": "cancel"
}
```

## Response Messages

### Progress Update

Sent during task execution for each step.

```json
{
  "type": "progress",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "step": 1,
  "action": {
    "_metadata": "do",
    "action": "Tap",
    "element": [500, 300]
  },
  "thinking": "正在分析屏幕，寻找微信图标...",
  "message": null,
  "timestamp": "2026-03-01T10:00:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"progress"` |
| `task_id` | string | Unique task identifier (UUID) |
| `step` | integer | Current step number |
| `action` | object | Action details (optional) |
| `thinking` | string | AI thinking process (optional) |
| `message` | string | Result message (optional) |
| `timestamp` | string | ISO 8601 timestamp |

### Task Completed

Sent when task execution completes successfully.

```json
{
  "type": "completed",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "result": {
    "success": true,
    "total_steps": 5
  },
  "total_steps": 5,
  "timestamp": "2026-03-01T10:01:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"completed"` |
| `task_id` | string | Task identifier |
| `result` | object | Task execution result |
| `result.success` | boolean | Whether task succeeded |
| `total_steps` | integer | Total steps executed |
| `timestamp` | string | ISO 8601 timestamp |

### Error

Sent when an error occurs.

```json
{
  "type": "error",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "error": "Device not found",
  "error_type": "execution_error",
  "timestamp": "2026-03-01T10:00:30Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"error"` |
| `task_id` | string | Task identifier (or `"unknown"`) |
| `error` | string | Error description |
| `error_type` | string | Error type (see below) |
| `timestamp` | string | ISO 8601 timestamp |

**Error Types:**

| Type | Description |
|------|-------------|
| `protocol_error` | Invalid message format or unknown action |
| `execution_error` | Task execution failed |
| `internal_error` | Server internal error |

### Pong

Response to ping request.

```json
{
  "type": "pong",
  "timestamp": "2026-03-01T10:00:00Z"
}
```

## Connection Lifecycle

```
┌─────────┐                    ┌─────────┐
│ Client  │                    │ Server  │
└────┬────┘                    └────┬────┘
     │                              │
     │──── Connect (WebSocket) ────>│
     │                              │
     │<─── Connected ───────────────│
     │                              │
     │──── Execute Request ────────>│
     │                              │
     │<─── Progress Update ─────────│
     │<─── Progress Update ─────────│
     │<─── ... ─────────────────────│
     │                              │
     │<─── Completed/Error ─────────│
     │                              │
     │──── Close ──────────────────>│
     │                              │
```

## TypeScript Types

```typescript
// Request types
interface ExecuteRequest {
  action: 'execute';
  task: string;
  device_id?: string;
  options?: Record<string, unknown>;
}

interface PingRequest {
  action: 'ping';
}

interface CancelRequest {
  action: 'cancel';
}

type ClientRequest = ExecuteRequest | PingRequest | CancelRequest;

// Response types
interface ProgressMessage {
  type: 'progress';
  task_id: string;
  step: number;
  action?: {
    _metadata?: string;
    action: string;
    element?: number[] | string;
  };
  thinking?: string;
  message?: string;
  timestamp: string;
}

interface CompletedMessage {
  type: 'completed';
  task_id: string;
  result: {
    success: boolean;
    total_steps?: number;
  };
  total_steps: number;
  timestamp: string;
}

interface ErrorMessage {
  type: 'error';
  task_id: string;
  error: string;
  error_type: 'protocol_error' | 'execution_error' | 'internal_error';
  timestamp: string;
}

interface PongMessage {
  type: 'pong';
  timestamp: string;
}

type ServerMessage = ProgressMessage | CompletedMessage | ErrorMessage | PongMessage;
```

## Error Handling

### Connection Errors

| Error | Solution |
|-------|----------|
| Max connections reached | Server closes with code 1008 |
| Connection lost | Task continues but client loses updates |

### Protocol Errors

| Error | Solution |
|-------|----------|
| Invalid JSON | Check message format |
| Missing fields | Add required fields |
| Unknown action | Use valid action name |

### Execution Errors

| Error | Solution |
|-------|----------|
| Device not found | Check device connection and `device_id` |
| Model API error | Check model server status |
| Task timeout | Increase timeout or simplify task |

## Best Practices

1. **Handle all message types** - Always handle `progress`, `completed`, `error`, and `pong`
2. **Implement reconnection** - Handle connection drops gracefully
3. **Set timeouts** - Don't wait indefinitely for responses
4. **Log progress** - Save progress updates for debugging
5. **Validate responses** - Check message format before processing

## Limitations (MVP)

1. **Task Cancellation** - Limited support, tasks continue until completion
2. **Concurrent Tasks** - One task per connection at a time
3. **Task Resumption** - No support for resuming disconnected tasks
4. **Authentication** - No authentication in MVP version
5. **Device Locking** - No device-level locking for concurrent connections

## Security Considerations

**MVP Version has no authentication.** For production:

1. Implement authentication (token or certificate-based)
2. Use TLS/SSL (`wss://` instead of `ws://`)
3. Validate all input on server side
4. Rate limit connections and requests
5. Monitor for abuse
