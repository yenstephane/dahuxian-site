# -*- coding: utf-8 -*-
# 8/21 主力線(分點):讀 window.ZCO(夜掃寫入),支撐=近5/20日買超成本、賣壓=近5日賣超成本;吸籌/出貨=集中度判別
import sys
f=sys.argv[1]
s=open(f,encoding='utf-8').read()
R=[
# R1 勾選框(接在法人線 label 後)
('<input type="checkbox" id="wx">法人線</label>',
 '''<input type="checkbox" id="wx">法人線</label>
  <label class="ck" title="券商分點前15大買賣超彙總(夜掃每日更新;僅涵蓋★雙過與持倉追蹤股約15檔)。支撐=近5日(亮)/近20日(暗)主力買超量加權成本;賣壓=近5日賣超成本(僅畫在收盤之上時)。吸籌/出貨判別=籌碼集中度:買超合計>賣超合計→買方集中(主力吃貨、散戶分散出)=吸籌;反之=倒貨。僅顯示參考,不進回測、不影響引擎訊號"><input type="checkbox" id="zl">主力線(分點)</label>'''),
# R2 zlData 函式(掛在 subCache 前)
("function subCache(){",
 '''function zlData(sid){
 var Z=window.ZCO&&window.ZCO.m&&window.ZCO.m[sid];if(!Z)return null;
 if(cur._zl&&cur._zl.sid===sid)return cur._zl;
 var ds=Object.keys(Z).sort();
 var bi={},i;for(i=0;i<cur.bars.length;i++)bi[cur.bars[i].d]=i;
 var n=cur.bars.length;
 function A(){return new Array(n).fill(NaN)}
 var s5=A(),s20=A(),p5=A(),mArr=A();
 for(var k=0;k<ds.length;k++){var idx=bi[ds[k]];if(idx==null)continue;
  var mk=function(win,side){var num=0,den=0;
   for(var j=Math.max(0,k-win+1);j<=k;j++){var r=Z[ds[j]];if(!r)continue;
    var vol=side==='b'?r[0]:r[1],cc=side==='b'?r[2]:r[3];
    if(vol>0&&cc>0){num+=vol*cc;den+=vol;}}
   return den>0?num/den:NaN;};
  s5[idx]=mk(5,'b');s20[idx]=mk(20,'b');p5[idx]=mk(5,'s');
  var r0=Z[ds[k]];mArr[idx]=(r0[0]||0)-(r0[1]||0);}
 cur._zl={sid:sid,s5:s5,s20:s20,p5:p5,m:mArr,cover:ds.length};
 return cur._zl;}
function subCache(){'''),
# R3 繪圖(接在法人線 wx 區塊尾)
('''  for(var z8=0;z8<WE.sell.length;z8++){var si9=WE.sell[z8];if(si9>=v0&&si9<vE)star(X(si9),Y(D.h[si9])-28,'#00d5ff');}
 }''',
 '''  for(var z8=0;z8<WE.sell.length;z8++){var si9=WE.sell[z8];if(si9>=v0&&si9<vE)star(X(si9),Y(D.h[si9])-28,'#00d5ff');}
 }

 if($('zl')&&$('zl').checked){
  var ZL=zlData(cur.sid);
  if(ZL){var zline=function(arr,color,lw,mask){g.strokeStyle=color;g.lineWidth=lw;g.beginPath();var onz=false;
    for(var iz=v0;iz<v1;iz++){var vz=arr[iz];if(isNaN(vz)||(mask&&!mask(iz))){onz=false;continue;}
     var xz=padL+(iz-v0)*cw,yz=Y(vz);
     if(!onz){g.moveTo(xz,yz);onz=true;}else g.lineTo(xz,yz);
     g.lineTo(xz+cw,yz);}
    g.stroke();g.lineWidth=1;};
   zline(ZL.s20,'#9b7a30',1.1);
   zline(ZL.s5,'#ffc04d',1.6);
   zline(ZL.p5,'#4dd0a0',1.3,function(i9){return ZL.p5[i9]>D.c[i9]});}
 }'''),
# R4 卡片徵兆(接在法人線快訊區塊尾)
('''  if(ex9)$('cSigSub').textContent=($('cSigSub').textContent?$('cSigSub').textContent+'\\n':'')+ex9;
 }''',
 '''  if(ex9)$('cSigSub').textContent=($('cSigSub').textContent?$('cSigSub').textContent+'\\n':'')+ex9;
 }
 if($('zl')&&$('zl').checked){var ZB=zlData(cur.sid);
  if(ZB){var li=-1,q9;for(q9=cur.D.n-1;q9>=0;q9--){if(!isNaN(ZB.s5[q9])){li=q9;break;}}
   if(li>=0){var acc=0,tot=0;for(var q8=cur.D.n-1;q8>=0&&tot<5;q8--){if(isNaN(ZB.m[q8]))continue;tot++;if(ZB.m[q8]>0)acc++;}
    var dv=(cur.D.c[cur.D.n-1]/ZB.s5[li]-1)*100;
    $('cSigSub').textContent=($('cSigSub').textContent?$('cSigSub').textContent+'\\n':'')+'主力(分點):近5筆 '+acc+'吸'+(tot-acc)+'出;5日成本 '+ZB.s5[li].toFixed(2)+'(收盤乖離 '+(dv>=0?'+':'')+dv.toFixed(1)+'%)';}}
  else $('cSigSub').textContent=($('cSigSub').textContent?$('cSigSub').textContent+'\\n':'')+'主力(分點):此股不在追蹤清單(夜掃僅提供★/持倉股)';}'''),
# R5 十字線 tip(接在法人線 tip 後)
('''<span style="color:#b89b3a">支2 '+xh9(cur.wei.S2[xi])+'</span>';''',
 '''<span style="color:#b89b3a">支2 '+xh9(cur.wei.S2[xi])+'</span>';
 if($('zl')&&$('zl').checked){var ZL9=zlData(cur.sid);
  if(ZL9)tip.innerHTML+='<br><span style="color:#ffc04d">主力5 '+xh9(ZL9.s5[xi])+'</span> <span style="color:#9b7a30">主力20 '+xh9(ZL9.s20[xi])+'</span> <span style="color:#4dd0a0">賣壓5 '+xh9(ZL9.p5[xi])+'</span>'+(isNaN(ZL9.m[xi])?'':(ZL9.m[xi]>0?' <span style="color:#ff9f1a">吸籌</span>':' <span style="color:#22c55e">出貨</span>'));}''' ),
# R6 readout(接在法人 readout 後)
('''ro9+='|法人 壓1 '+xr9(cur.wei.R1[xi])+' 壓2 '+xr9(cur.wei.R2[xi])+' 支1 '+xr9(cur.wei.S1[xi])+' 支2 '+xr9(cur.wei.S2[xi]);}''',
 '''ro9+='|法人 壓1 '+xr9(cur.wei.R1[xi])+' 壓2 '+xr9(cur.wei.R2[xi])+' 支1 '+xr9(cur.wei.S1[xi])+' 支2 '+xr9(cur.wei.S2[xi]);}
 if($('zl')&&$('zl').checked){var ZR9=zlData(cur.sid);
  if(ZR9&&!isNaN(ZR9.s5[xi]))ro9+='|主力5 '+ZR9.s5[xi].toFixed(2)+(isNaN(ZR9.m[xi])?'':(ZR9.m[xi]>0?' 吸':' 出'));}'''),
# R7 onchange
("if($('stair'))$('stair').onchange=function(){if(cur)render()};",
 "if($('stair'))$('stair').onchange=function(){if(cur)render()};\nif($('zl'))$('zl').onchange=function(){if(cur)render()};"),
]
fail=0
for a,b in R:
    n=s.count(a)
    if n!=1:
        print('MISMATCH x%d: %r'%(n,a[:70])); fail+=1
    s=s.replace(a,b)
if fail: sys.exit('FAIL %d'%fail)
# R8 zco_data.js 載入標籤
old8='<script src="dahu_filters.js"></script>'
new8='<script src="dahu_filters.js"></script>\n<script src="https://stephaneyen.pythonanywhere.com/zco_data.js"></script>'
if s.count(old8)==1: s=s.replace(old8,new8)
elif '<script src="https://stephaneyen.pythonanywhere.com/zco_data.js">' not in s: sys.exit('FAIL R8')
open(f,'w',encoding='utf-8').write(s)
print('OK',f)
