"""
Simple WebSocket client example for Phone Agent Server.

Demonstrates basic connection and task execution.
"""

import asyncio
import json
import sys
import websockets


async def execute_task(uri: str, task: str):
    """
    Connect to server and execute a task.

    Args:
        uri: WebSocket server URI
        task: Task description
    """
    print(f"Connecting to {uri}...")

    async with websockets.connect(uri) as websocket:
        print("Connected!")

        # Send execute request
        request = {
            "action": "execute",
            "task": task,
        }

        print(f"\nSending task: {task}")
        await websocket.send(json.dumps(request, ensure_ascii=False))

        # Receive responses
        print("\nReceiving responses:")
        print("-" * 60)

        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "progress":
                step = data.get("step")
                action = data.get("action", {})
                thinking = data.get("thinking", "")

                print(f"\n[Step {step}]")
                if action:
                    print(f"Action: {action.get('action', 'N/A')}")
                if thinking:
                    # Truncate long thinking text
                    thinking_preview = thinking[:100] + "..." if len(thinking) > 100 else thinking
                    print(f"Thinking: {thinking_preview}")

            elif msg_type == "completed":
                print(f"\n✓ Task completed!")
                print(f"Total steps: {data.get('total_steps')}")
                print(f"Result: {data.get('result')}")
                break

            elif msg_type == "error":
                print(f"\n✗ Error: {data.get('error')}")
                print(f"Error type: {data.get('error_type')}")
                break

            elif msg_type == "pong":
                # Ignore pong messages
                pass

        print("-" * 60)


async def main():
    """Main entry point."""
    # Default values
    uri = "ws://localhost:8765"
    task = "打开微信"

    # Parse command line arguments
    if len(sys.argv) > 1:
        task = sys.argv[1]
    if len(sys.argv) > 2:
        uri = sys.argv[2]

    try:
        await execute_task(uri, task)
    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Phone Agent WebSocket Client")
    print("=" * 60)

    asyncio.run(main())
