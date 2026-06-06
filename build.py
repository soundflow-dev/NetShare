#!/usr/bin/env python3
"""Gera um static/index.html autossuficiente (CSS+JS embutidos).

As fontes editaveis sao static/style.css e static/app.js. Corre este script
sempre que as alterares:  python3 build.py
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent / "static"
css = (BASE / "style.css").read_text()
js = (BASE / "app.js").read_text()

# CSS extra para o seletor de idioma no menu de conta (pequeno)
extra_css = """
/* seletor de idioma no menu de conta */
.acct-divider { height:1px; background:rgba(255,255,255,.08); margin:4px 0; }
.acct-label { padding:6px 12px 2px; font-size:11px; opacity:.55; letter-spacing:.04em; }
.acct-item.lang-opt { display:flex; align-items:center; justify-content:space-between; }
.acct-item.lang-opt .check { opacity:0; }
.acct-item.lang-opt.selected .check { opacity:1; color:#25c685; }
"""

template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NetShare</title>
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <link rel="manifest" href="manifest.webmanifest">
  <meta name="theme-color" content="#0d1218">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="NetShare">
  <style>
__CSS__
__EXTRA_CSS__
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <span class="logo">◈</span>
      <div>
        <div class="brand-name">NetShare</div>
        <div class="brand-sub">Gateway</div>
      </div>
    </div>
    <div class="topbar-right">
      <div id="conn-pill" class="conn-pill"><span class="dot"></span><span id="conn-text" data-i18n="conn.checking">checking…</span></div>
      <div class="acct" id="acct">
        <button id="acct-btn" class="ghost acct-btn">👤 <span id="acct-name" data-i18n="account.account">account</span> ▾</button>
        <div id="acct-menu" class="acct-menu hidden">
          <button id="acct-chpw" class="acct-item" data-i18n="account.changePassword">Change password</button>
          <button id="acct-logout" class="acct-item" data-i18n="account.logout">Sign out</button>
          <div class="acct-divider"></div>
          <div class="acct-label" data-i18n="account.language">Language</div>
          <button class="acct-item lang-opt" data-lang-opt="pt"><span>Português</span><span class="check">✓</span></button>
          <button class="acct-item lang-opt" data-lang-opt="en"><span>English</span><span class="check">✓</span></button>
        </div>
      </div>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="hero-info">
        <div class="hero-icon" id="hero-icon">\U0001f310</div>
        <div class="hero-meta">
          <div class="hero-label" data-i18n="hero.label">INTERNET</div>
          <div class="hero-isp" id="hero-isp">—</div>
          <div class="hero-rows">
            <div><span class="k" data-i18n="hero.publicIp">Public IP</span><span class="v" id="hero-ip">—</span></div>
            <div><span class="k" data-i18n="hero.org">Org</span><span class="v" id="hero-org">—</span></div>
            <div><span class="k" data-i18n="hero.location">Location</span><span class="v" id="hero-loc">—</span></div>
            <div><span class="k" data-i18n="hero.wan">WAN</span><span class="v" id="hero-wan">—</span></div>
          </div>
        </div>
      </div>
      <div class="hero-graph">
        <div class="rates">
          <div class="rate down"><span class="arrow">↓</span><span id="hero-down">0</span><small id="hero-down-u">bps</small></div>
          <div class="rate up"><span class="arrow">↑</span><span id="hero-up">0</span><small id="hero-up-u">bps</small></div>
        </div>
        <canvas id="hero-canvas" class="graph" height="120"></canvas>
      </div>
    </section>

    <section>
      <div class="section-head">
        <h2 data-i18n="sections.interfaces">Interfaces</h2>
        <button id="refresh" class="ghost" data-i18n="sections.refresh">↻ Refresh</button>
      </div>
      <div id="devices" class="grid"></div>
    </section>

    <section id="wifi-section" class="hidden">
      <div class="section-head">
        <h2><span data-i18n="sections.wifiNetworks">Wi-Fi networks</span> <small id="wifi-dev"></small></h2>
        <button id="scan" class="ghost" data-i18n="sections.scan">⟳ Scan</button>
      </div>
      <div id="wifi-list" class="wifi-list"></div>
    </section>
  </main>

  <div id="toast" class="toast hidden"></div>

  <div id="modal" class="modal hidden">
    <div class="modal-box">
      <h3 id="modal-ssid"></h3>
      <input id="modal-pass" type="password" data-i18n-ph="wifi.passwordPlaceholder" placeholder="Network password" autocomplete="off">
      <div class="modal-actions">
        <button id="modal-cancel" class="ghost" data-i18n="modal.cancel">Cancel</button>
        <button id="modal-connect" data-i18n="modal.connect">Connect</button>
      </div>
    </div>
  </div>

  <!-- mudar password -->
  <div id="pw-modal" class="modal hidden">
    <div class="modal-box">
      <h3 data-i18n="modal.changePassword">Change password</h3>
      <input id="pw-current" type="password" data-i18n-ph="modal.currentPw" placeholder="Current password" autocomplete="current-password">
      <input id="pw-new" type="password" data-i18n-ph="modal.newPw" placeholder="New password (min. 6)" autocomplete="new-password">
      <input id="pw-new2" type="password" data-i18n-ph="modal.confirmNewPw" placeholder="Confirm new password" autocomplete="new-password">
      <div id="pw-error" class="auth-error"></div>
      <div class="modal-actions">
        <button id="pw-cancel" class="ghost" data-i18n="modal.cancel">Cancel</button>
        <button id="pw-save" data-i18n="modal.save">Save</button>
      </div>
    </div>
  </div>

  <!-- login / 1.o arranque -->
  <div id="auth-screen" class="auth-screen hidden">
    <div class="auth-box">
      <div class="auth-logo"><span class="logo">◈</span> NetShare</div>
      <div id="auth-title" class="auth-title" data-i18n="auth.signIn">Sign in</div>
      <div id="auth-sub" class="auth-sub"></div>
      <input id="auth-user" data-i18n-ph="auth.username" placeholder="Username" autocomplete="username">
      <input id="auth-pass" type="password" data-i18n-ph="auth.password" placeholder="Password" autocomplete="current-password">
      <input id="auth-pass2" type="password" data-i18n-ph="auth.confirmPassword" placeholder="Confirm password" class="hidden" autocomplete="new-password">
      <div id="auth-error" class="auth-error"></div>
      <button id="auth-submit" data-i18n="auth.signInBtn">Sign in</button>
    </div>
  </div>

  <script>
__JS__
  </script>
</body>
</html>
"""

html = template.replace("__CSS__", css).replace("__EXTRA_CSS__", extra_css).replace("__JS__", js)
(BASE / "index.html").write_text(html)
print("static/index.html gerado (autossuficiente, %d bytes)" % len(html))
