/**
 * Phone Agent WebSocket Client
 *
 * A TypeScript client for connecting to the Phone Agent Server and executing
 * phone automation tasks.
 *
 * @example
 * // Command line usage:
 * // npx -y bun main.ts "打开微信"
 * // npx -y bun main.ts "打开微信" ws://localhost:8765
 *
 * // Programmatic usage:
 * import { PhoneAgentClient } from './main.ts';
 * const client = new PhoneAgentClient('ws://localhost:8765');
 * client.onProgress(console.log);
 * client.connect().then(() => client.executeTask('打开微信'));
 */

import WebSocket from 'ws';

// ============================================================================
// Type Definitions
// ============================================================================

/** Request to execute a task */
interface ExecuteRequest {
  action: 'execute';
  task: string;
  device_id?: string;
  options?: Record<string, unknown>;
}

/** Ping request to keep connection alive */
interface PingRequest {
  action: 'ping';
}

/** Cancel request to stop current task */
interface CancelRequest {
  action: 'cancel';
}

/** Union type for all client requests */
type ClientRequest = ExecuteRequest | PingRequest | CancelRequest;

/** Action details in a progress message */
interface ActionDetails {
  action: string;
  element?: string | number[];
}

/** Progress update message from server */
interface ProgressMessage {
  type: 'progress';
  task_id: string;
  step: number;
  action?: ActionDetails;
  thinking?: string;
  message?: string;
  timestamp: string;
}

/** Task completion message from server */
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

/** Error message from server */
interface ErrorMessage {
  type: 'error';
  task_id: string;
  error: string;
  error_type: 'protocol_error' | 'execution_error' | 'internal_error';
  timestamp: string;
}

/** Pong response message */
interface PongMessage {
  type: 'pong';
  timestamp: string;
}

/** Union type for all server messages */
type ServerMessage = ProgressMessage | CompletedMessage | ErrorMessage | PongMessage;

/** Callback types */
type ProgressCallback = (data: ProgressMessage) => void;
type CompletedCallback = (data: CompletedMessage) => void;
type ErrorCallback = (data: ErrorMessage) => void;

// ============================================================================
// PhoneAgentClient Class
// ============================================================================

/**
 * WebSocket client for Phone Agent Server.
 *
 * Provides methods to connect to the server, execute tasks, and receive
 * real-time progress updates.
 */
class PhoneAgentClient {
  private uri: string;
  private ws: WebSocket | null = null;
  private connected = false;

  // Callback handlers
  private progressCallbacks: ProgressCallback[] = [];
  private completedCallbacks: CompletedCallback[] = [];
  private errorCallbacks: ErrorCallback[] = [];

  /**
   * Create a new Phone Agent client.
   *
   * @param uri - WebSocket server URI (e.g., 'ws://localhost:8765')
   */
  constructor(uri: string) {
    this.uri = uri;
  }

  /**
   * Connect to the WebSocket server.
   *
   * @returns Promise that resolves when connected
   * @throws Error if connection fails
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.uri);

      this.ws.on('open', () => {
        this.connected = true;
        resolve();
      });

      this.ws.on('message', (data: WebSocket.RawData) => {
        this._handleMessage(data);
      });

      this.ws.on('error', (error: Error) => {
        if (!this.connected) {
          reject(error);
        } else {
          console.error('WebSocket error:', error.message);
        }
      });

      this.ws.on('close', () => {
        this.connected = false;
      });
    });
  }

  /**
   * Execute a phone automation task.
   *
   * @param task - Task description in natural language
   * @param deviceId - Optional specific device ID
   */
  executeTask(task: string, deviceId: string | null = null): void {
    if (!this.connected || !this.ws) {
      throw new Error('Not connected to server');
    }

    const request: ExecuteRequest = {
      action: 'execute',
      task: task
    };

    if (deviceId) {
      request.device_id = deviceId;
    }

    this.ws.send(JSON.stringify(request));
  }

  /**
   * Send a ping to keep the connection alive.
   */
  ping(): void {
    if (!this.connected || !this.ws) {
      throw new Error('Not connected to server');
    }

    const request: PingRequest = { action: 'ping' };
    this.ws.send(JSON.stringify(request));
  }

  /**
   * Request task cancellation.
   */
  cancel(): void {
    if (!this.connected || !this.ws) {
      throw new Error('Not connected to server');
    }

    const request: CancelRequest = { action: 'cancel' };
    this.ws.send(JSON.stringify(request));
  }

  /**
   * Close the WebSocket connection.
   */
  close(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.connected = false;
    }
  }

  /**
   * Register a callback for progress updates.
   *
   * @param callback - Function to call on progress
   */
  onProgress(callback: ProgressCallback): void {
    this.progressCallbacks.push(callback);
  }

  /**
   * Register a callback for task completion.
   *
   * @param callback - Function to call on completion
   */
  onCompleted(callback: CompletedCallback): void {
    this.completedCallbacks.push(callback);
  }

  /**
   * Register a callback for errors.
   *
   * @param callback - Function to call on error
   */
  onError(callback: ErrorCallback): void {
    this.errorCallbacks.push(callback);
  }

  /**
   * Handle incoming WebSocket message.
   *
   * @param data - Raw message data
   */
  private _handleMessage(data: WebSocket.RawData): void {
    try {
      const message = JSON.parse(data.toString()) as ServerMessage;
      const type = message.type;

      switch (type) {
        case 'progress':
          this.progressCallbacks.forEach(cb => cb(message as ProgressMessage));
          break;

        case 'completed':
          this.completedCallbacks.forEach(cb => cb(message as CompletedMessage));
          break;

        case 'error':
          this.errorCallbacks.forEach(cb => cb(message as ErrorMessage));
          break;

        case 'pong':
          // Ignore pong messages
          break;

        default:
          console.warn('Unknown message type:', type);
      }
    } catch (e) {
      const error = e as Error;
      console.error('Failed to parse message:', error.message);
    }
  }
}

// ============================================================================
// CLI Helpers
// ============================================================================

/**
 * Format action for display.
 *
 * @param action - Action object
 * @returns Formatted action string
 */
function formatAction(action: ActionDetails | undefined): string {
  if (!action) return 'N/A';

  const actionType = action.action || 'Unknown';
  const element = action.element;

  if (element) {
    if (Array.isArray(element)) {
      return `${actionType} at (${element.join(', ')})`;
    }
    return `${actionType} ${element}`;
  }

  return actionType;
}

/**
 * Run CLI client.
 *
 * @param task - Task description
 * @param uri - Server URI
 */
async function runCli(task: string, uri: string): Promise<void> {
  console.log('Phone Agent WebSocket Client');
  console.log('='.repeat(60));
  console.log(`Connecting to ${uri}...`);

  const client = new PhoneAgentClient(uri);

  // Set up event handlers
  client.onProgress((data) => {
    console.log(`\n[Step ${data.step}]`);
    if (data.action) {
      console.log(`  Action: ${formatAction(data.action)}`);
    }
    if (data.thinking) {
      // Truncate long thinking text
      const preview = data.thinking.length > 100
        ? data.thinking.substring(0, 100) + '...'
        : data.thinking;
      console.log(`  Thinking: ${preview}`);
    }
    if (data.message) {
      console.log(`  Message: ${data.message}`);
    }
  });

  client.onCompleted((data) => {
    console.log('\n' + '='.repeat(60));
    console.log('Task completed!');
    console.log(`Total steps: ${data.total_steps}`);
    console.log(`Result: ${JSON.stringify(data.result)}`);
    client.close();
    process.exit(0);
  });

  client.onError((data) => {
    console.log('\n' + '='.repeat(60));
    console.log(`Error: ${data.error}`);
    console.log(`Error type: ${data.error_type}`);
    client.close();
    process.exit(1);
  });

  try {
    await client.connect();
    console.log('Connected!');
    console.log(`\nSending task: ${task}`);
    console.log('-'.repeat(60));

    client.executeTask(task);
  } catch (error) {
    const err = error as Error;
    console.error('Connection failed:', err.message);
    process.exit(1);
  }
}

// ============================================================================
// CLI Entry Point
// ============================================================================

// Get command line arguments
const args = process.argv.slice(2);

if (args.length === 0) {
  console.log('Usage: npx -y bun main.ts <task> [server_uri]');
  console.log('');
  console.log('Arguments:');
  console.log('  task        Task description in natural language');
  console.log('  server_uri  WebSocket server URI (default: ws://localhost:8765)');
  console.log('');
  console.log('Examples:');
  console.log('  npx -y bun main.ts "打开微信"');
  console.log('  npx -y bun main.ts "打开微信" ws://192.168.1.100:8765');
  process.exit(1);
}

const task = args[0];
const uri = args[1] || process.env.PHONE_AGENT_WS_URI || 'ws://localhost:8765';

runCli(task, uri);

// Export for programmatic use
export { PhoneAgentClient };
export type {
  ExecuteRequest,
  PingRequest,
  CancelRequest,
  ClientRequest,
  ActionDetails,
  ProgressMessage,
  CompletedMessage,
  ErrorMessage,
  PongMessage,
  ServerMessage,
  ProgressCallback,
  CompletedCallback,
  ErrorCallback
};
