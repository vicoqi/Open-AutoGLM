#!/bin/bash

# Phone Agent Server 管理脚本
# 用法: ./phone_agent_server.sh {start|stop|restart|status}

# 配置
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/phone_agent_server.pid"
LOG_FILE="$SCRIPT_DIR/phone_agent_server.log"
PYTHON_CMD="python3"
SERVER_MODULE="phone_agent_server.server"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查服务是否运行
is_valid_pid() {
    [[ "$1" =~ ^[0-9]+$ ]]
}

get_process_start_time() {
    ps -p "$1" -o lstart= 2>/dev/null | sed 's/^[[:space:]]*//'
}

is_target_process() {
    local cmd
    cmd=$(ps -p "$1" -o args= 2>/dev/null)
    [[ -n "$cmd" && "$cmd" == *"-m $SERVER_MODULE"* ]]
}

get_recorded_start_time() {
    if [ -f "$PID_FILE" ]; then
        sed -n '2p' "$PID_FILE"
    fi
}

is_running() {
    local pid
    local recorded_start
    local current_start

    if [ -f "$PID_FILE" ]; then
        pid=$(get_pid)
        recorded_start=$(get_recorded_start_time)

        if is_valid_pid "$pid" && ps -p "$pid" > /dev/null 2>&1 && is_target_process "$pid"; then
            if [ -n "$recorded_start" ]; then
                current_start=$(get_process_start_time "$pid")
                [ "$recorded_start" = "$current_start" ] && return 0
            else
                return 0
            fi
        fi
    fi
    return 1
}

# 获取 PID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        sed -n '1p' "$PID_FILE"
    fi
}

# 启动服务
start() {
    if is_running; then
        log_warn "服务已在运行中 (PID: $(get_pid))"
        return 1
    fi

    log_info "启动 Phone Agent Server..."

    # 检查虚拟环境
    if [ -d "$SCRIPT_DIR/venv" ]; then
        source "$SCRIPT_DIR/venv/bin/activate"
        log_info "已激活虚拟环境"
    fi

    # 后台启动服务
    cd "$SCRIPT_DIR"
    nohup $PYTHON_CMD -m $SERVER_MODULE >> "$LOG_FILE" 2>&1 &
    pid=$!

    # 等待一下确认启动成功
    sleep 1

    if ps -p "$pid" > /dev/null 2>&1; then
        {
            echo "$pid"
            get_process_start_time "$pid"
        } > "$PID_FILE"
        log_info "服务已启动 (PID: $pid)"
        log_info "日志文件: $LOG_FILE"
        return 0
    else
        log_error "服务启动失败，请查看日志: $LOG_FILE"
        return 1
    fi
}

# 停止服务
stop() {
    local pid
    local recorded_start
    local current_start

    if ! is_running; then
        log_warn "服务未运行"
        [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
        return 0
    fi

    pid=$(get_pid)
    recorded_start=$(get_recorded_start_time)

    if ! is_valid_pid "$pid"; then
        log_warn "PID 文件格式无效，已清理"
        rm -f "$PID_FILE"
        return 0
    fi

    if ! ps -p "$pid" > /dev/null 2>&1; then
        log_warn "PID 文件存在但进程不存在，已清理"
        rm -f "$PID_FILE"
        return 0
    fi

    if ! is_target_process "$pid"; then
        log_warn "PID $pid 不是 Phone Agent Server 进程，已跳过停止并清理 PID 文件"
        rm -f "$PID_FILE"
        return 0
    fi

    if [ -n "$recorded_start" ]; then
        current_start=$(get_process_start_time "$pid")
        if [ "$recorded_start" != "$current_start" ]; then
            log_warn "PID $pid 与记录的启动时间不匹配，已跳过停止并清理 PID 文件"
            rm -f "$PID_FILE"
            return 0
        fi
    fi

    log_info "停止服务 (PID: $pid)..."

    # 发送 SIGTERM
    kill "$pid" 2>/dev/null

    # 等待进程结束
    for i in {1..10}; do
        if ! ps -p "$pid" > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done

    # 如果还在运行，强制结束
    if ps -p "$pid" > /dev/null 2>&1; then
        log_warn "进程未响应，强制结束..."
        kill -9 "$pid" 2>/dev/null
        sleep 1
    fi

    if ! ps -p "$pid" > /dev/null 2>&1; then
        rm -f "$PID_FILE"
        log_info "服务已停止"
        return 0
    else
        log_error "无法停止服务"
        return 1
    fi
}

# 重启服务
restart() {
    log_info "重启服务..."
    stop
    sleep 1
    start
}

# 查看状态
status() {
    if is_running; then
        pid=$(get_pid)
        log_info "服务运行中 (PID: $pid)"

        # 显示进程信息
        echo ""
        ps -p "$pid" -o pid,ppid,%cpu,%mem,etime,command 2>/dev/null

        # 显示最近日志
        if [ -f "$LOG_FILE" ]; then
            echo ""
            log_info "最近日志 (最后 5 行):"
            tail -5 "$LOG_FILE"
        fi
    else
        log_warn "服务未运行"
        [ -f "$PID_FILE" ] && log_warn "PID 文件存在但不是目标服务或已失效，可执行 stop 自动清理"
    fi
}

# 查看日志
logs() {
    if [ -f "$LOG_FILE" ]; then
        log_info "显示日志 (Ctrl+C 退出)..."
        tail -f "$LOG_FILE"
    else
        log_warn "日志文件不存在: $LOG_FILE"
    fi
}

# 帮助信息
help() {
    echo "Phone Agent Server 管理脚本"
    echo ""
    echo "用法: $0 {start|stop|restart|status|logs}"
    echo ""
    echo "命令:"
    echo "  start   - 后台启动服务"
    echo "  stop    - 停止服务"
    echo "  restart - 重启服务"
    echo "  status  - 查看服务状态"
    echo "  logs    - 查看实时日志"
    echo ""
    echo "文件:"
    echo "  PID 文件: $PID_FILE"
    echo "  日志文件: $LOG_FILE"
}

# 主入口
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        help
        exit 1
        ;;
esac
