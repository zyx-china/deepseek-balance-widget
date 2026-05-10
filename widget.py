#!/usr/bin/env python3
"""
DeepSeek API 余额桌面小组件
macOS 桌面悬浮小组件，原生毛玻璃质感，Apple 设计风格
"""

import json
import os
from datetime import datetime, timedelta

import requests
import webview

# ---- 常量 ----
CONFIG_DIR = os.path.expanduser("~/.deepseek-balance")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
CACHE_FILE = os.path.join(CONFIG_DIR, "cache.json")
CACHE_TTL = timedelta(minutes=5)
BALANCE_URL = "https://api.deepseek.com/user/balance"

# ---- HTML / CSS / JS ----
HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
  :root {
    --text-primary: rgba(255,255,255,0.92);
    --text-secondary: rgba(255,255,255,0.55);
    --text-tertiary: rgba(255,255,255,0.38);
    --accent: #5e9cff;
    --green: #30d158;
    --yellow: #ffd60a;
    --red: #ff453a;
    --radius: 18px;
  }

  @media (prefers-color-scheme: light) {
    :root {
      --text-primary: rgba(0,0,0,0.82);
      --text-secondary: rgba(0,0,0,0.52);
      --text-tertiary: rgba(0,0,0,0.32);
      --accent: #0071e3;
      --green: #248a3d;
      --yellow: #b68b00;
      --red: #c73b35;
    }
  }

  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    font-family: -apple-system, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
    background: transparent;
    -webkit-user-select: none;
    user-select: none;
    overflow: hidden;
    width: 230px;
    height: 150px;
  }

  .widget {
    width: 100%;
    height: 100%;
    padding: 19px 20px 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  /* ---- 顶部标题栏 ---- */
  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .title {
    font-size: 11px;
    font-weight: 590;
    color: var(--text-secondary);
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .actions {
    display: flex;
    gap: 4px;
  }

  .action-btn {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    border: none;
    background: rgba(128,128,128,0.16);
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.15s, color 0.15s;
    line-height: 1;
    padding: 0;
  }

  .action-btn:hover {
    background: rgba(128,128,128,0.28);
    color: var(--text-primary);
  }

  .action-btn:active {
    background: rgba(128,128,128,0.36);
    transform: scale(0.94);
  }

  .close-btn:hover {
    background: rgba(255,69,58,0.28);
    color: var(--red);
  }

  /* ---- 余额主区域 ---- */
  .balance-area {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .balance-row {
    display: flex;
    align-items: baseline;
    gap: 5px;
  }

  .balance-number {
    font-size: 33px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1;
    font-feature-settings: "tnum";
    font-variant-numeric: tabular-nums;
  }

  .balance-currency {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-tertiary);
    letter-spacing: 0.01em;
  }

  .status-bar {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: 4px;
  }

  .status-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .status-dot.ok    { background: var(--green); }
  .status-dot.load  { background: var(--yellow); animation: blink 1.2s infinite; }
  .status-dot.error { background: var(--red); }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.25; }
  }

  .status-label {
    font-size: 10px;
    font-weight: 450;
    color: var(--text-tertiary);
  }

  /* ---- 设置面板 (overlay) ---- */
  .settings-overlay {
    display: none;
    position: absolute;
    inset: 0;
    background: rgba(30,30,32,0.92);
    border-radius: var(--radius);
    padding: 22px 20px 18px;
    z-index: 10;
  }

  @media (prefers-color-scheme: light) {
    .settings-overlay {
      background: rgba(245,245,247,0.94);
    }
  }

  .settings-overlay.show { display: flex; flex-direction: column; }

  .settings-overlay label {
    font-size: 11px;
    font-weight: 590;
    color: var(--text-secondary);
    margin-bottom: 7px;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }

  .settings-overlay input {
    flex: 0 0 auto;
    padding: 7px 10px;
    border-radius: 7px;
    border: 1px solid rgba(128,128,128,0.25);
    background: rgba(128,128,128,0.08);
    color: var(--text-primary);
    font-size: 12px;
    outline: none;
    width: 100%;
    font-family: "SF Mono", "Menlo", monospace;
    transition: border-color 0.15s;
    margin-bottom: 14px;
  }

  .settings-overlay input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(0,113,227,0.25);
  }

  .settings-btns {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }

  .btn-primary {
    padding: 5px 15px;
    border-radius: 6px;
    border: none;
    background: var(--accent);
    color: #fff;
    font-size: 12px;
    font-weight: 590;
    cursor: pointer;
    transition: opacity 0.15s;
  }

  .btn-primary:hover  { opacity: 0.82; }
  .btn-primary:active { opacity: 0.65; }

  .btn-ghost {
    padding: 5px 15px;
    border-radius: 6px;
    border: none;
    background: rgba(128,128,128,0.14);
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
  }

  .btn-ghost:hover  { background: rgba(128,128,128,0.25); color: var(--text-primary); }
  .btn-ghost:active { background: rgba(128,128,128,0.35); }

  /* ---- Toast ---- */
  .toast {
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.78);
    color: #fff;
    font-size: 10px;
    font-weight: 550;
    padding: 4px 12px;
    border-radius: 20px;
    opacity: 0;
    transition: opacity 0.25s;
    pointer-events: none;
    white-space: nowrap;
    z-index: 20;
  }

  .toast.show { opacity: 1; }
</style>
</head>
<body>

<div class="widget">
  <!-- 标题栏 -->
  <div class="topbar">
    <span class="title">DeepSeek</span>
    <div class="actions">
      <button class="action-btn" id="btn-settings" title="设置 API Key">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
          <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </button>
      <button class="action-btn" id="btn-refresh" title="刷新">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
      </button>
      <button class="action-btn close-btn" id="btn-close" title="关闭">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
  </div>

  <!-- 余额显示 -->
  <div class="balance-area">
    <div class="balance-row">
      <span class="balance-number" id="balance-num">---</span>
      <span class="balance-currency" id="balance-unit">CNY</span>
    </div>
    <div class="status-bar">
      <span class="status-dot load" id="status-dot"></span>
      <span class="status-label" id="status-text">等待设置 API Key</span>
    </div>
  </div>
</div>

<!-- 设置面板 -->
<div class="settings-overlay" id="settings-overlay">
  <label>API Key</label>
  <input type="password" id="apikey-input" placeholder="sk-..." spellcheck="false">
  <div class="settings-btns">
    <button class="btn-ghost" id="btn-cancel">取消</button>
    <button class="btn-primary" id="btn-save">保存</button>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
  const $num    = document.getElementById('balance-num');
  const $unit   = document.getElementById('balance-unit');
  const $dot    = document.getElementById('status-dot');
  const $status = document.getElementById('status-text');
  const $overlay= document.getElementById('settings-overlay');
  const $input  = document.getElementById('apikey-input');
  const $toast  = document.getElementById('toast');

  let toastTimer;
  function toast(msg) {
    $toast.textContent = msg;
    $toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => $toast.classList.remove('show'), 2000);
  }

  function setUI(status, dotClass) {
    $status.textContent = status;
    $dot.className = 'status-dot ' + (dotClass || '');
  }

  function display(balance, currency) {
    const n = parseFloat(balance);
    if (!isNaN(n)) {
      $num.textContent = n === Math.floor(n)
        ? n.toLocaleString()
        : n.toLocaleString(undefined, { minimumFractionDigits:2, maximumFractionDigits:2 });
    } else {
      $num.textContent = balance;
    }
    $unit.textContent = currency || 'CNY';
  }

  // ---- Settings ----
  document.getElementById('btn-settings').onclick = async () => {
    $input.value = await window.pywebview.api.get_api_key();
    $overlay.classList.add('show');
    setTimeout(() => $input.focus(), 100);
  };

  document.getElementById('btn-cancel').onclick = () => $overlay.classList.remove('show');

  document.getElementById('btn-save').onclick = async () => {
    const key = $input.value.trim();
    if (!key) return;
    setUI('验证中...', 'load');
    try {
      const r = await window.pywebview.api.set_and_test(key);
      $overlay.classList.remove('show');
      if (r.ok) { display(r.balance, r.currency); setUI('已连接', 'ok'); toast('已连接'); }
      else      { setUI(r.error || '验证失败', 'error'); toast('Key 无效'); }
    } catch (_) { setUI('网络错误', 'error'); }
  };

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') $overlay.classList.remove('show');
  });

  // ---- Refresh ----
  document.getElementById('btn-refresh').onclick = async () => {
    setUI('刷新中...', 'load');
    try {
      const r = await window.pywebview.api.refresh();
      if (r.ok) { display(r.balance, r.currency); setUI('已连接', 'ok'); toast('已刷新'); }
      else      { setUI(r.error || '刷新失败', 'error'); }
    } catch (_) { setUI('网络错误', 'error'); }
  };

  // ---- Close ----
  document.getElementById('btn-close').onclick = () => {
    window.pywebview.api.quit_app();
  };

  // ---- Init ----
  (async () => {
    try {
      const r = await window.pywebview.api.init();
      if (r.ok) {
        display(r.balance, r.currency); setUI('已连接', 'ok');
      } else {
        $num.textContent = '---'; $unit.textContent = 'CNY';
        if (r.need_key) { setUI('请设置 API Key', 'error'); setTimeout(() => $overlay.classList.add('show'), 300); }
        else           { setUI(r.error || '未知错误', 'error'); }
      }
    } catch (_) { $num.textContent = '---'; setUI('加载失败', 'error'); }
  })();

  // ---- Auto-refresh (5 min) ----
  setInterval(async () => {
    try {
      const r = await window.pywebview.api.auto_refresh();
      if (r && r.ok) { display(r.balance, r.currency); setUI('已连接', 'ok'); }
    } catch (_) {}
  }, 300_000);
</script>
</body>
</html>"""


# ---- Python Backend ----
class BalanceAPI:
    def __init__(self):
        self.api_key = ""
        self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                self.api_key = json.load(f).get("api_key", "")

    def _save_config(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump({"api_key": self.api_key}, f, indent=2)

    def _cache_get(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                return json.load(f)
        return {}

    def _cache_set(self, data):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def _fetch(self, api_key):
        resp = requests.get(
            BALANCE_URL,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            timeout=15,
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}")
        data = resp.json()
        if "balance_infos" in data and len(data["balance_infos"]) > 0:
            info = data["balance_infos"][0]
            return info.get("total_balance", "0.00"), info.get("currency", "CNY")
        if "balance" in data:
            return data["balance"], "CNY"
        raise Exception("Unexpected response")

    def _get_cached(self, api_key):
        cache = self._cache_get()
        if cache.get("ts"):
            ts = datetime.fromisoformat(cache["ts"])
            if datetime.now() - ts < CACHE_TTL:
                return cache["balance"], cache["currency"]
        balance, currency = self._fetch(api_key)
        self._cache_set({"ts": datetime.now().isoformat(), "balance": balance, "currency": currency})
        return balance, currency

    # ---- JS API ----
    def quit_app(self):
        os._exit(0)

    def get_api_key(self):
        return self.api_key

    def init(self):
        if not self.api_key:
            return {"ok": False, "need_key": True}
        try:
            balance, currency = self._get_cached(self.api_key)
            return {"ok": True, "balance": balance, "currency": currency}
        except Exception as e:
            return {"ok": False, "error": str(e)[:60]}

    def set_and_test(self, api_key):
        try:
            balance, currency = self._fetch(api_key)
            self.api_key = api_key
            self._save_config()
            self._cache_set({"ts": datetime.now().isoformat(), "balance": balance, "currency": currency})
            return {"ok": True, "balance": balance, "currency": currency}
        except Exception as e:
            return {"ok": False, "error": str(e)[:60]}

    def refresh(self):
        if not self.api_key:
            return {"ok": False, "error": "未设置 API Key"}
        try:
            balance, currency = self._fetch(self.api_key)
            self._cache_set({"ts": datetime.now().isoformat(), "balance": balance, "currency": currency})
            return {"ok": True, "balance": balance, "currency": currency}
        except Exception as e:
            return {"ok": False, "error": str(e)[:60]}

    def auto_refresh(self):
        if not self.api_key:
            return None
        try:
            balance, currency = self._get_cached(self.api_key)
            return {"ok": True, "balance": balance, "currency": currency}
        except Exception:
            return None


def _get_window_position():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        return config.get("win_x", 50), config.get("win_y", 50)
    return 50, 50


def _save_window_position(x, y):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    config["win_x"] = x
    config["win_y"] = y
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def _setup_desktop_behavior(window):
    """让窗口像桌面小组件一样行为：不出现在 Cmd+Tab，保持在所有桌面空间可见"""
    native = window.native

    # CanJoinAllSpaces (1) | Stationary (1<<4) | IgnoresCycle (1<<5)
    native.setCollectionBehavior_(1 | 16 | 32)

    # 发送到所有窗口后面，不抢焦点
    native.orderBack_(None)



def main():
    api = BalanceAPI()
    x, y = _get_window_position()

    window = webview.create_window(
        title="DeepSeek Balance",
        html=HTML,
        js_api=api,
        width=230,
        height=150,
        x=x,
        y=y,
        frameless=True,
        transparent=True,
        vibrancy=True,
        easy_drag=True,
        focus=True,
    )

    window.events.shown += lambda: _setup_desktop_behavior(window)

    # 窗口移动时保存位置
    def on_moved():
        _save_window_position(window.x, window.y)

    window.events.moved += on_moved

    webview.start(debug=False)


if __name__ == "__main__":
    main()
