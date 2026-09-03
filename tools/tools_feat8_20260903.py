#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""改版⑪(2026-09-03):⚠賣出提醒 chip 顯示「證券名稱 代碼」(原本非核心 109 檔會退化成「6446 6446」)。
名稱查找鏈:exits[].n → VD(核心109) → WATCH.items → GEXP.items → STAR_OUT.items;找不到才只顯示代碼。
冪等:已含 data-nm 的 .fx chip 即跳過。用法:python3 tools_feat8_20260903.py <html> [<html> ...]
"""
import sys, io, hashlib

OLD1 = """    ex.forEach(function(e){var nm=(window.VD&&VD[e.sid])?VD[e.sid][0]:e.sid;
     xh+='<span class="stk fx" data-id="'+e.sid+'" style="border:1px solid #e05252;border-radius:8px;padding:3px 9px;cursor:pointer;font-size:12.5px;background:#1a0f0f;color:#ffb3b3">'+e.sid+' '+nm+' ・'+e.why+' '+e.d.slice(5).replace('-','/')+'</span>'});"""
NEW1 = """    ex.forEach(function(e){var nm=e.n||((window.VD&&VD[e.sid])?VD[e.sid][0]:'')||wn[e.sid]||'';
     if(!nm){[window.GEXP,window.STAR_OUT].forEach(function(o){if(!nm&&o&&o.items)o.items.forEach(function(it){if(!nm&&it&&it.sid===e.sid&&it.n)nm=it.n})});}
     var lb=nm?nm+' '+e.sid:e.sid;
     xh+='<span class="stk fx" data-id="'+e.sid+'" data-nm="'+nm+'" style="border:1px solid #e05252;border-radius:8px;padding:3px 9px;cursor:pointer;font-size:12.5px;background:#1a0f0f;color:#ffb3b3">'+lb+' ・'+e.why+' '+e.d.slice(5).replace('-','/')+'</span>'});"""
OLD2 = """    fg.querySelectorAll('.fx').forEach(function(x){x.onclick=function(){var sid=x.dataset.id;
     if(window.VD&&VD[sid]&&typeof selectStock==='function')selectStock(sid);
     else if(typeof query==='function')query(sid,sid)}});}}}"""
NEW2 = """    fg.querySelectorAll('.fx').forEach(function(x){x.onclick=function(){var sid=x.dataset.id;
     if(window.VD&&VD[sid]&&typeof selectStock==='function')selectStock(sid);
     else if(typeof query==='function')query(sid,x.dataset.nm||sid)}});}}}"""

def sha(p):
    return hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]

def patch(p):
    s = io.open(p, encoding='utf-8', newline='').read()
    if 'data-nm="\'+nm+\'" style="border:1px solid #e05252' in s:
        print(p, 'SKIP already patched', sha(p)); return
    if s.count(OLD1) != 1 or s.count(OLD2) != 1:
        print(p, 'FAIL anchors', s.count(OLD1), s.count(OLD2)); sys.exit(1)
    s = s.replace(OLD1, NEW1).replace(OLD2, NEW2)
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print(p, 'OK', sha(p))

for f in sys.argv[1:]:
    patch(f)
