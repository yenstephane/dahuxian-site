# -*- coding: utf-8 -*-
# 8/21 操盤台功能補丁:①B版階梯顯示開關 ②十字線同步顯示已開啟線種數值
import sys
f=sys.argv[1]
s=open(f,encoding='utf-8').read()
R=[
# R1 勾選框
('<label class="ck" title="20/60/120 日簡單移動平均(還原收盤價)"><input type="checkbox" id="ma" checked>均線 20/60/120</label>',
 '<label class="ck" title="20/60/120 日簡單移動平均(還原收盤價)"><input type="checkbox" id="ma" checked>均線 20/60/120</label>\n  <label class="ck" title="B v2 引擎的價格階梯與 ±1×ATR14 帶;隱藏只影響圖層,訊號引擎照常運作"><input type="checkbox" id="stair" checked>B版階梯</label>'),
# R2 帶狀填色 gate
(" if(!res.noBand)for(var i3=v0;i3<v1;i3++){var L2=res.line[i3];if(L2==null)continue;",
 " var stairOn=(!$('stair')||$('stair').checked);\n if(!res.noBand&&stairOn)for(var i3=v0;i3<v1;i3++){var L2=res.line[i3];if(L2==null)continue;"),
# R3 階梯線 gate
(" g.lineWidth=2.2;\n var i5=v0;\n while(i5<v1){",
 " g.lineWidth=2.2;\n var i5=stairOn?v0:v1;\n while(i5<v1){"),
# R4 tip 各線數值
(''' if($('ma')&&$('ma').checked&&cur._ma){var f9=function(v){return isNaN(v)?'—':v.toFixed(2)};
  tip.innerHTML+='<br><span style="color:#f0f0f0">MA20 '+f9(cur._ma.m20[xi])+'</span> <span style="color:#3fa7ff">60 '+f9(cur._ma.m60[xi])+'</span> <span style="color:#ff4fd8">120 '+f9(cur._ma.m120[xi])+'</span>';}''',
 ''' if($('ma')&&$('ma').checked&&cur._ma){var f9=function(v){return isNaN(v)?'—':v.toFixed(2)};
  tip.innerHTML+='<br><span style="color:#f0f0f0">MA20 '+f9(cur._ma.m20[xi])+'</span> <span style="color:#3fa7ff">60 '+f9(cur._ma.m60[xi])+'</span> <span style="color:#ff4fd8">120 '+f9(cur._ma.m120[xi])+'</span>';}
 var xh9=function(v){return (v==null||isNaN(v))?'—':(+v).toFixed(2)};
 if((!$('stair')||$('stair').checked)&&res.line&&res.line[xi]!=null){var bb9=(D.atr[xi])||0;
  tip.innerHTML+='<br><span style="color:'+(res.dirs[xi]===1?'#ff9f1a':'#22c55e')+'">階梯 '+(+res.line[xi]).toFixed(2)+' 帶 '+(res.line[xi]-bb9).toFixed(2)+'~'+(res.line[xi]+bb9).toFixed(2)+'</span>';}
 if($('wx')&&$('wx').checked&&cur.wei)tip.innerHTML+='<br><span style="color:#3ef94a">法人壓 '+xh9(cur.wei.P[xi])+'</span> <span style="color:#ffd700">法人支 '+xh9(cur.wei.S[xi])+'</span>';
 if($('dp')&&$('dp').checked&&cur.dl)tip.innerHTML+='<br><span style="color:#ff5ca8">D壓5 '+xh9(cur.dl.p5[xi])+'</span> <span style="color:#c13fff">D壓10 '+xh9(cur.dl.p10[xi])+'</span>';
 if($('ds')&&$('ds').checked&&cur.dl)tip.innerHTML+='<br><span style="color:#4fd8ff">D支5 '+xh9(cur.dl.s5[xi])+'</span> <span style="color:#3f7fd4">D支10 '+xh9(cur.dl.s10[xi])+'</span>';'''),
# R5 readout gate+法人線
(''' var b2=(D.atr[xi])||0,L3=res.line[xi];
 $('readout').textContent=D.dates[xi]+'  開'+D.o[xi].toFixed(2)+' 高'+D.h[xi].toFixed(2)+' 低'+D.l[xi].toFixed(2)+' 收'+D.c[xi].toFixed(2)
  +(L3!=null?('|階梯 '+L3.toFixed(2)+' 帶['+(L3-b2).toFixed(2)+'~'+(L3+b2).toFixed(2)+']'+(res.dirs[xi]===1?' 多方':' 空方')):'');}''',
 ''' var b2=(D.atr[xi])||0,L3=res.line[xi],sOn9=(!$('stair')||$('stair').checked);
 var ro9=D.dates[xi]+'  開'+D.o[xi].toFixed(2)+' 高'+D.h[xi].toFixed(2)+' 低'+D.l[xi].toFixed(2)+' 收'+D.c[xi].toFixed(2)
  +((sOn9&&L3!=null)?('|階梯 '+L3.toFixed(2)+' 帶['+(L3-b2).toFixed(2)+'~'+(L3+b2).toFixed(2)+']'+(res.dirs[xi]===1?' 多方':' 空方')):'');
 if($('wx')&&$('wx').checked&&cur.wei){var wp9=cur.wei.P[xi],ws9=cur.wei.S[xi];ro9+='|法人壓 '+((wp9==null||isNaN(wp9))?'—':wp9.toFixed(2))+' 支 '+((ws9==null||isNaN(ws9))?'—':ws9.toFixed(2));}
 $('readout').textContent=ro9;}'''),
# R6 onchange
("$('wx').onchange=function(){if(cur)render()};",
 "$('wx').onchange=function(){if(cur)render()};\nif($('stair'))$('stair').onchange=function(){if(cur)render()};"),
]
fail=0
for a,b in R:
    n=s.count(a)
    if n!=1:
        print('MISMATCH x%d: %r'%(n,a[:60])); fail+=1
    s=s.replace(a,b)
if fail: sys.exit('FAIL %d'%fail)
open(f,'w',encoding='utf-8').write(s)
print('OK',f)
