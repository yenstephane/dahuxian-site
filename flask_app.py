# 大戶線網站 —— PythonAnywhere 部署用(靜態檔案+盤中指數代理+密碼閘門)
# WSGI 入口:PythonAnywhere 的 WSGI 設定檔 import 本檔的 app
import json, os, time

import requests
from flask import Flask, Response, request, session, redirect, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.secret_key = 'dahu-gate-7f3a9c2e51b8d604'  # session cookie 簽章用(非密碼)
_cache = {"t": 0.0, "body": None}

GATE_PASS = 'dahu2026'
# 免驗白名單:API 代理+資料 js(本機操盤台以 file:// 跨站載入,帶不了 session cookie)
OPEN_PATHS = {'zco_data.js', 'jia_badge.js', 'rotation_data.js', 'dahu_filters.js',
              'favicon.ico', 'login'}

LOGIN_HTML = '''<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>大戶線</title>
<body style="margin:0;background:#101418;color:#dde;display:flex;align-items:center;justify-content:center;height:100vh;font-family:system-ui,'Noto Sans TC',sans-serif">
<form method="post" action="/login" style="background:#1a2028;border:1px solid #2c3642;border-radius:12px;padding:36px 40px;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.5)">
<div style="font-size:22px;font-weight:700;margin-bottom:6px;color:#ffd37a">大戶線</div>
<div style="font-size:13px;color:#8a97a5;margin-bottom:20px">請輸入通行密碼</div>
<input type="password" name="p" autofocus autocomplete="current-password"
 style="background:#0d1116;border:1px solid #39434f;border-radius:8px;color:#eef;padding:10px 12px;font-size:16px;width:200px;text-align:center;outline:none">
<div style="margin-top:16px"><button type="submit"
 style="background:#ffd37a;color:#1a2028;border:0;border-radius:8px;padding:10px 28px;font-size:15px;font-weight:700;cursor:pointer">進入</button></div>
<div style="font-size:12px;color:#e05656;margin-top:12px;min-height:14px">{msg}</div>
<div style="font-size:11px;color:#5a6672;margin-top:8px">僅供研究,非投資建議</div>
</form></body></html>'''


@app.before_request
def gate():
    p = (request.path or '/').lstrip('/')
    if p.startswith('api/') or p in OPEN_PATHS:
        return None
    if session.get('ok'):
        return None
    if request.method == 'POST' and p == '':
        return None
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if (request.form.get('p') or '').strip() == GATE_PASS:
            session['ok'] = True
            session.permanent = True
            return redirect('/')
        return Response(LOGIN_HTML.replace('{msg}', '密碼錯誤,請再試一次'), 200,
                        mimetype='text/html')
    if session.get('ok'):
        return redirect('/')
    return Response(LOGIN_HTML.replace('{msg}', ''), 200, mimetype='text/html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/api/taiex')
def taiex():
    """替代 Netlify _redirects 的 200 代理:盤中大盤即時價(mis.twse.com.tw 無 CORS,需伺服器代抓)。
    10 秒快取降低上游負擔;免費帳號若被對外連線白名單擋下會回 502,前端自動退回盤後價。"""
    now = time.time()
    if _cache["body"] is not None and now - _cache["t"] < 10:
        body, code = _cache["body"], 200
    else:
        try:
            r = requests.get(
                'https://mis.twse.com.tw/stock/api/getStockInfo.jsp',
                params={'ex_ch': 'tse_t00.tw', 'json': '1', 'delay': '0'},
                headers={'User-Agent': 'Mozilla/5.0',
                         'Referer': 'https://mis.twse.com.tw/stock/index.jsp'},
                timeout=8)
            body, code = r.text, r.status_code
            if code == 200:
                _cache.update(t=now, body=body)
        except Exception as e:  # 白名單封鎖/逾時皆走此路
            body, code = json.dumps({'error': 'proxy_failed', 'detail': str(e)[:120]}), 502
    resp = Response(body, code, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Cache-Control'] = 'no-store'
    return resp


@app.route('/')
@app.route('/<path:p>')
def site(p='index.html'):
    """整站靜態檔由 Flask 供應(免設 static mapping;夜掃覆蓋 js 後即時生效)。"""
    full = os.path.normpath(os.path.join(BASE, p))
    if not (full + os.sep).startswith(BASE + os.sep) and full != BASE:
        return Response('forbidden', 403)
    if os.path.isdir(full):
        full = os.path.join(full, 'index.html')
    if not os.path.isfile(full):
        return Response('not found', 404)
    rel = os.path.relpath(full, BASE)
    resp = send_from_directory(BASE, rel)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    if rel.endswith('.js'):
        resp.headers['Cache-Control'] = 'no-cache'  # rotation_data/dahu_filters 每晚更新
    return resp
