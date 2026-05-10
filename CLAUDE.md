# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概述

macOS 桌面悬浮小组件，显示 DeepSeek API 余额。单文件架构：`widget.py` 包含全部 Python 后端 + HTML/CSS/JS 前端。

## 运行与调试

```bash
# 手动启动
./run.sh

# 开机启动管理
launchctl load ~/Library/LaunchAgents/com.deepseek.balance-widget.plist    # 启用
launchctl unload ~/Library/LaunchAgents/com.deepseek.balance-widget.plist  # 停用

# 查看日志
cat /tmp/deepseek-balance-widget.log
cat /tmp/deepseek-balance-widget.err
```

## 架构

```
widget.py
├── HTML 常量 (inline HTML/CSS/JS)
├── BalanceAPI 类 → 通过 pywebview JS bridge 暴露给前端
│   ├── get_api_key / set_and_test / init / refresh / auto_refresh / quit_app
│   └── 余额缓存到 ~/.deepseek-balance/cache.json (TTL=5min)
├── _setup_desktop_behavior() → 窗口显示后设置层级和 Dock 隐藏
└── main() → create_window() + events.shown/moved hooks + webview.start()
```

**关键 pywebview 参数：** `frameless=True, transparent=True, vibrancy=True, easy_drag=True`

- `transparent=True` → WKWebView 背景透明（`drawsTransparentBackground`）
- `vibrancy=True` → NSVisualEffectView 原生毛玻璃效果
- `easy_drag=True` → 通过原生 mouseDown/mouseDragged 实现窗口拖拽

**配置与缓存**（位于 `~/.deepseek-balance/`，不在仓库内）：
- `config.json` — API Key + 窗口位置
- `cache.json` — 余额缓存 + 时间戳

**LaunchAgent：** `~/Library/LaunchAgents/com.deepseek.balance-widget.plist`
- 登录自启，直接调 Python 解释器，不依赖 run.sh

## 注意事项

- **不要使用 `-webkit-app-region` CSS 属性** — WKWebView 不支持，会导致点击事件失效
- 窗口层级使用正常层级 + `orderBack_()`，不用 `kCGDesktopWindowLevel`（会导致无法点击）
- `NSApp.setActivationPolicy_(1)` 隐藏 Dock 图标，此调用必须在窗口创建后执行
- DeepSeek 余额 API：`GET https://api.deepseek.com/user/balance`，Bearer token 鉴权，返回 `balance_infos[0].total_balance`
- 自动刷新间隔：JS 端 `setInterval(300_000)`，Python 缓存 TTL 5 分钟
