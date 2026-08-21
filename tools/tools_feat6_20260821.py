# -*- coding: utf-8 -*-
# feat6 2026-08-21:主力吸籌徽章(純顯示層)——vdBand 加 JBADGE 亮燈 + 載入 jia_badge.js
# 用法:python3 tools_feat6_20260821.py <html路徑>
import sys, hashlib, io

p = sys.argv[1]
s = io.open(p, 'r', encoding='utf-8').read()
orig = s

# 1) script 標籤:zco_data.js 後插 jia_badge.js
tag_old = '<script src="https://stephaneyen.pythonanywhere.com/zco_data.js"></script>'
tag_new = tag_old + '<script src="https://stephaneyen.pythonanywhere.com/jia_badge.js"></script>'
assert s.count(tag_old) == 1, 'zco tag not unique: %d' % s.count(tag_old)
assert 'jia_badge.js' not in s, 'already patched?'
s = s.replace(tag_old, tag_new)

# 2) vdBand:濾網區塊後加徽章
anchor = " el.innerHTML=t;el.style.display='block';}"
badge = (" if(window.JBADGE&&window.JBADGE.m&&window.JBADGE.m[cur.sid]){var jb=window.JBADGE.m[cur.sid];\n"
 "  t+='|'+(jb[0]===1?'<b style=\"color:#ffb74d\" title=\"近10日主力買賣超 +'+jb[1]+' 張、買賣家數差 '+jb[2]+'(負=集中)——雙條件成立(資料日 '+window.JBADGE.date+');研究顯示參考,非引擎訊號\">\\u26a1主力吸籌中</b>':'<span style=\"color:#777\" title=\"雙條件未成立(資料日 '+window.JBADGE.date+'):M10='+jb[1]+' 家數10='+jb[2]+'\">主力吸籌:無</span>');}\n")
assert s.count(anchor) == 1, 'vdBand anchor not unique: %d' % s.count(anchor)
s = s.replace(anchor, badge + anchor)

io.open(p, 'w', encoding='utf-8').write(s)
h = hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]
print('OK', p, 'sha16=', h)
