# Phone Agent WebSocket Server API

WebSocket API documentation for the Phone Agent Server.

## Connection

**Endpoint**: `ws://host:port/`

Default: `ws://localhost:8765/`

## Message Protocol

All messages are JSON-formatted strings.

### Request Messages

#### Execute Task

Execute a phone automation task.

```json
{
  "action": "execute",
  "task": "打开微信发送消息给张三",
  "device_id": "optional_device_id",
  "options": {}
}
```

**Fields**:
- `action` (string, required): Must be "execute"
- `task` (string, required): Task description in natural language
- `device_id` (string, optional): Specific device ID to use
- `options` (object, optional): Additional options (reserved for future use)

#### Ping

Test connection and keep alive.

```json
{
  "action": "ping"
}
```

#### Cancel Task

Request cancellation of current task (limited support in MVP).

```json
{
  "action": "cancel"
}
```

### Response Messages

#### Progress Update

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

**Fields**:
- `type` (string): "progress"
- `task_id` (string): Unique task identifier (UUID)
- `step` (integer): Current step number
- `action` (object, optional): Action details
- `thinking` (string, optional): AI thinking process
- `message` (string, optional): Result message
- `timestamp` (string): ISO 8601 timestamp

#### Task Completed

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

**Fields**:
- `type` (string): "completed"
- `task_id` (string): Task identifier
- `result` (object): Task execution result
- `total_steps` (integer): Total number of steps executed
- `timestamp` (string): ISO 8601 timestamp

#### Error

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

**Fields**:
- `type` (string): "error"
- `task_id` (string): Task identifier (or "unknown")
- `error` (string): Error description
- `error_type` (string): Error type (see Error Types below)
- `timestamp` (string): ISO 8601 timestamp

**Error Types**:
- `protocol_error`: Invalid message format or unknown action
- `execution_error`: Task execution failed
- `internal_error`: Server internal error

#### Pong

Response to ping request.

```json
{
  "type": "pong",
  "timestamp": "2026-03-01T10:00:00Z"
}
```

## Connection Lifecycle

1. **Connect**: Client establishes WebSocket connection
2. **Heartbeat**: Server sends WebSocket ping frames every 30 seconds (configurable)
3. **Execute**: Client sends execute request
4. **Progress**: Server streams progress updates during execution
5. **Complete**: Server sends completion or error message
6. **Disconnect**: Either party can close the connection

## Configuration

Server configuration via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PHONE_AGENT_WS_HOST` | Server host address | `0.0.0.0` |
| `PHONE_AGENT_WS_PORT` | Server port | `8765` |
| `PHONE_AGENT_WS_MAX_CONNECTIONS` | Max concurrent connections | `10` |
| `PHONE_AGENT_WS_HEARTBEAT_INTERVAL` | Heartbeat interval (seconds) | `30` |
| `PHONE_AGENT_WS_TASK_TIMEOUT` | Task timeout (seconds) | `300` |

Plus all standard Open-AutoGLM environment variables (see main README).

## Example Usage

### Python Client

```python
import asyncio
import json
import websockets

async def execute_task():
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        # Send task
        request = {
            "action": "execute",
            "task": "打开微信"
        }
        await websocket.send(json.dumps(request, ensure_ascii=False))

        # Receive responses
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "progress":
                print(f"Step {data['step']}: {data.get('action')}")
            elif data["type"] == "completed":
                print("Task completed!")
                break
            elif data["type"] == "error":
                print(f"Error: {data['error']}")
                break

asyncio.run(execute_task())
```

### JavaScript Client

```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
  // Send task
  ws.send(JSON.stringify({
    action: 'execute',
    task: '打开微信'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'progress') {
    console.log(`Step ${data.step}:`, data.action);
  } else if (data.type === 'completed') {
    console.log('Task completed!');
    ws.close();
  } else if (data.type === 'error') {
    console.error('Error:', data.error);
    ws.close();
  }
};
```

## Limitations (MVP Version)

1. **Task Cancellation**: Limited support - tasks continue until completion
2. **Concurrent Tasks**: One task per connection at a time
3. **Task Resumption**: No support for resuming disconnected tasks
4. **Authentication**: No authentication in MVP version
5. **Device Locking**: No device-level locking for concurrent connections

## Error Handling

### Connection Errors

- **Max connections reached**: Server closes connection with code 1008
- **Connection lost**: Task continues executing but client loses progress updates

### Protocol Errors

- **Invalid JSON**: Server sends error message with `error_type: "protocol_error"`
- **Missing fields**: Server sends error message describing missing field
- **Unknown action**: Server sends error message with unknown action name

### Execution Errors

- **Device not found**: Check device connection and `device_id` parameter
- **Model API error**: Check model server status and configuration
- **Task timeout**: Task exceeded configured timeout (default 300s)

## Best Practices

1. **Handle all message types**: Always handle progress, completed, error, and pong messages
2. **Implement reconnection**: Handle connection drops gracefully
3. **Set timeouts**: Don't wait indefinitely for responses
4. **Log progress**: Save progress updates for debugging
5. **Validate responses**: Check message format before processing

## Security Considerations

**MVP Version has no authentication**. For production use:

1. Implement authentication (token-based or certificate-based)
2. Use TLS/SSL (wss:// instead of ws://)
3. Validate all input on server side
4. Rate limit connections and requests
5. Monitor for abuse

## Support

For issues and questions:
- GitHub Issues: https://github.com/zai-org/Open-AutoGLM/issues
- Documentation: See project README and PRD documents
