# 大戶線網站 —— PythonAnywhere 部署用(靜態檔案+盤中指數代理)
# WSGI 入口:PythonAnywhere 的 WSGI 設定檔 import 本檔的 app
import json, os, time

import requests
from flask import Flask, Response, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
_cache = {"t": 0.0, "body": None}


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
