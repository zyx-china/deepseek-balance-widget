#!/bin/bash
# DeepSeek 余额桌面小组件启动脚本

cd "$(dirname "$0")"
nohup python3 widget.py > /dev/null 2>&1 &
echo "DeepSeek 余额小组件已启动 (PID: $!)"
