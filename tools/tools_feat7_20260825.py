#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""feat7 (2026-08-25): star-out panel"""
import sys, hashlib, io

HTML_ANCHOR = ' <div id="filtgrid" style="display:flex;flex-wrap:wrap;gap:6px"></div>\n'
HTML_ADD = (' <div id="soutwrap" style="display:none;margin-top:7px">'
            '<div style="font-size:12px;color:#9a9a9a;margin-bottom:4px"><b>➖ 近期移出 ★</b> '
            '<span id="soutmeta" style="color:#777;font-size:11px"></span></div>'
            '<div id="soutgrid" style="display:flex;flex-wrap:wrap;gap:6px"></div></div>\n')

JS_ANCHOR = "(function(){var a=document.getElementById('idxBtn')"
JS_ADD = """(function(){try{
 var S=window.STAR_OUT;if(!S||!S.items||!S.items.length)return;
 var w=(S.w||7),cut=new Date();cut.setDate(cut.getDate()-w);var cs=cut.toISOString().slice(0,10);
 var it=S.items.filter(function(e){return e.d>=cs});
 if(!it.length)return;
 var el=document.getElementById('filtpanel'),sw=document.getElementById('soutwrap'),sg=document.getElementById('soutgrid');
 if(!sw||!sg)return;if(el)el.style.display='block';
 it.sort(function(a,b){return a.d<b.d?1:-1});
 var h='';
 it.forEach(function(e){
  var nm=e.n||((window.VD&&VD[e.sid])?VD[e.sid][0]:e.sid);
  var tip=(e.det||'')+(e.hold?'\\uff5c'+e.hold:'');
  h+='<span class="stk so" data-id="'+e.sid+'" data-nm="'+nm+'" title="'+tip+'" style="border:1px dashed #6a6a6a;border-radius:8px;padding:3px 9px;cursor:pointer;font-size:12.5px;background:#131313;color:#a8a8a8">'
   +(e.src==='watch'?'<span style="color:#5a7fa8">\\u25c7</span>':'')+e.sid+' '+nm+' \\u30fb<b style="color:#c9a24a">'+e.why+'</b> '+e.d.slice(5).replace('-','/')+'</span>'});
 sg.innerHTML=h;sw.style.display='block';
 var m=document.getElementById('soutmeta');
 if(m)m.textContent='(\\u8fd1'+w+'\\u5929\\u81ea \\u2605 \\u6e05\\u55ae\\u79fb\\u51fa\\uff5c'+(S.note||'')+'\\uff5c\\u6ed1\\u9f20\\u505c\\u7559\\u770b\\u7d30\\u7bc0\\uff5c\\u9ede\\u64ca\\u958b K \\u7dda)';
 sg.querySelectorAll('.so').forEach(function(x){x.onclick=function(){var sid=x.dataset.id;
  if(window.VD&&VD[sid]&&typeof selectStock==='function')selectStock(sid);
  else if(typeof query==='function')query(sid,x.dataset.nm||sid)}});
}catch(e){}})();
"""


def patch(path):
    with io.open(path, encoding='utf-8') as f:
        s = f.read()
    if 'soutwrap' in s:
        return 'SKIP(already)', hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]
    if HTML_ANCHOR not in s:
        return 'FAIL(html anchor)', ''
    if JS_ANCHOR not in s:
        return 'FAIL(js anchor)', ''
    s = s.replace(HTML_ANCHOR, HTML_ANCHOR + HTML_ADD, 1)
    s = s.replace(JS_ANCHOR, JS_ADD + JS_ANCHOR, 1)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(s)
    return 'OK', hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]


if __name__ == '__main__':
    for p in sys.argv[1:]:
        st, sh = patch(p)
        print(p, st, sh)
