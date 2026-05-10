# DeepSeek Balance Widget

macOS 桌面小组件，原生毛玻璃质感，实时显示 DeepSeek API 余额。

<img width="230" alt="screenshot" src="https://github.com/user-attachments/assets/placeholder" />

## 功能

- 原生 NSVisualEffectView 毛玻璃效果
- 自动适配浅色 / 深色模式
- 余额数字等宽字体，千分位格式化
- 5 分钟自动刷新，本地缓存
- 窗口位置记忆
- 支持开机自启（LaunchAgent）

## 安装

```bash
git clone https://github.com/zyx-china/deepseek-balance-widget.git
cd deepseek-balance-widget
pip install -r requirements.txt
```

## 使用

```bash
# 手动启动
./run.sh

# 右键小组件 → 齿轮图标 → 输入 DeepSeek API Key
# 在 platform.deepseek.com/api_keys 获取
```

## 开机自启

```bash
# 编辑 plist 中的 Python 路径（如需）
# 已内置 plist 模板，默认使用 miniconda py311
launchctl load ~/Library/LaunchAgents/com.deepseek.balance-widget.plist
```

## 配置

所有用户数据存储在 `~/.deepseek-balance/`，与仓库分离：

- `config.json` — API Key + 窗口位置
- `cache.json` — 余额缓存（5 分钟有效）
