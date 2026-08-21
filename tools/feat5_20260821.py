# -*- coding: utf-8 -*-
# 8/21 主力線 v2:分點狀態機——恆兩條;吸籌日刷新支撐/出貨日刷新壓力(否則沿用);跌破翻面攜號;四態 支1支2/壓1支2/壓1壓2/壓2支1
import sys
f=sys.argv[1]
s=open(f,encoding='utf-8').read()
OLD_FN='''function zlData(sid){
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
 return cur._zl;}'''
NEW_FN='''function zlData(sid){
 // 主力線 v2(2026-08-21 使用者規格):恆兩條;吸籌日(買超合計>賣超合計=賣方家數多、買方集中)才刷新支撐=近5日買超成本;
 // 出貨日(賣超合計>買超合計=買方家數多、主力倒貨)才刷新壓力=近5日賣超成本;其餘沿用前值。
 // 收盤跌破支撐→翻面為壓力(攜號)且保留較低支撐;站上壓力→翻回支撐。四態:支1支2/壓1支2/壓1壓2/壓2支1。
 var Z=window.ZCO&&window.ZCO.m&&window.ZCO.m[sid];if(!Z)return null;
 if(cur._zl&&cur._zl.sid===sid)return cur._zl;
 var ds=Object.keys(Z).sort();
 var bi={},i;for(i=0;i<cur.bars.length;i++)bi[cur.bars[i].d]=i;
 var n=cur.bars.length;
 function A(){return new Array(n).fill(NaN)}
 var V={支1:A(),支2:A(),壓1:A(),壓2:A()},mArr=A(),stArr=new Array(n).fill(null);
 var lv=[]; // 池:{v:價位,side:'S'|'P',no:1|2}
 function cost(k,win,side){var num=0,den=0;
  for(var j=Math.max(0,k-win+1);j<=k;j++){var r=Z[ds[j]];if(!r)continue;
   var vol=side==='b'?r[0]:r[1],cc=side==='b'?r[2]:r[3];
   if(vol>0&&cc>0){num+=vol*cc;den+=vol;}}
  return den>0?num/den:NaN;}
 function pushNew(side,v){ // 新值進場:同側舊1號降2號,最多各2層
  var same=lv.filter(function(x){return x.side===side}),other=lv.filter(function(x){return x.side!==side});
  same.forEach(function(x){x.no=2});
  same.sort(function(a,b){return side==='S'?b.v-a.v:a.v-b.v});
  same=same.slice(0,1);same.forEach(function(x){x.no=2});
  same.unshift({v:v,side:side,no:1});
  lv=other.concat(same);}
 for(var k=0;k<ds.length;k++){var idx=bi[ds[k]];if(idx==null)continue;
  var r0=Z[ds[k]],c=cur.bars[idx].c;
  var M=(r0[0]||0)-(r0[1]||0);mArr[idx]=M;
  // 1) 翻面:收盤跌破支撐→轉壓(攜號);站上壓力→轉支(攜號)
  lv.forEach(function(x){if(x.side==='S'&&c<x.v)x.side='P';else if(x.side==='P'&&c>x.v)x.side='S';});
  // 2) 刷新(僅集中方):吸籌日→支撐=買超成本5;出貨日→壓力=賣超成本5(僅高於收盤才有壓力意義)
  if(M>0){var sv=cost(k,5,'b');
   if(!isNaN(sv)&&sv<c){var s1=lv.filter(function(x){return x.side==='S'&&x.no===1})[0];
    if(!s1||Math.abs(sv-s1.v)/s1.v>0.001)pushNew('S',sv);}}
  else if(M<0){var pv=cost(k,5,'s');
   if(!isNaN(pv)&&pv>c){var p1=lv.filter(function(x){return x.side==='P'&&x.no===1})[0];
    if(!p1||Math.abs(pv-p1.v)/p1.v>0.001)pushNew('P',pv);}}
  // 3) 每側最多2層、全池最多…顯示取兩條:雙側→最近壓+最近支;單側→該側兩層
  var Ps=lv.filter(function(x){return x.side==='P'}).sort(function(a,b){return a.v-b.v});
  var Ss=lv.filter(function(x){return x.side==='S'}).sort(function(a,b){return b.v-a.v});
  var show=[];
  if(Ps.length&&Ss.length)show=[Ps[0],Ss[0]];
  else if(Ss.length)show=Ss.slice(0,2);
  else if(Ps.length)show=Ps.slice(0,2);
  var names=[];
  show.forEach(function(x){var nm=(x.side==='S'?'支':'壓')+x.no;names.push(nm);V[nm]&&(V[nm][idx]=x.v);});
  stArr[idx]=names.join('');
 }
 cur._zl={sid:sid,V:V,m:mArr,st:stArr,cover:ds.length};
 return cur._zl;}'''
R=[
(OLD_FN,NEW_FN),
# 繪圖
('''  if(ZL){var zline=function(arr,color,lw,mask){g.strokeStyle=color;g.lineWidth=lw;g.beginPath();var onz=false;
    for(var iz=v0;iz<v1;iz++){var vz=arr[iz];if(isNaN(vz)||(mask&&!mask(iz))){onz=false;continue;}
     var xz=padL+(iz-v0)*cw,yz=Y(vz);
     if(!onz){g.moveTo(xz,yz);onz=true;}else g.lineTo(xz,yz);
     g.lineTo(xz+cw,yz);}
    g.stroke();g.lineWidth=1;};
   zline(ZL.s20,'#9b7a30',1.1);
   zline(ZL.s5,'#ffc04d',1.6);
   zline(ZL.p5,'#4dd0a0',1.3,function(i9){return ZL.p5[i9]>D.c[i9]});}''',
 '''  if(ZL){var zc={支1:['#ffc04d',1.6],支2:['#9b7a30',1.1],壓1:['#3edb8f',1.6],壓2:['#2a8f5f',1.1]};
   Object.keys(zc).forEach(function(nm){var arr=ZL.V[nm];g.strokeStyle=zc[nm][0];g.lineWidth=zc[nm][1];g.beginPath();var onz=false;
    for(var iz=v0;iz<v1;iz++){var vz=arr[iz];if(isNaN(vz)){onz=false;continue;}
     var xz=padL+(iz-v0)*cw,yz=Y(vz);
     if(!onz){g.moveTo(xz,yz);onz=true;}else g.lineTo(xz,yz);
     g.lineTo(xz+cw,yz);}
    g.stroke();});g.lineWidth=1;}'''),
# tip
('''  if(ZL9)tip.innerHTML+='<br><span style="color:#ffc04d">主力5 '+xh9(ZL9.s5[xi])+'</span> <span style="color:#9b7a30">主力20 '+xh9(ZL9.s20[xi])+'</span> <span style="color:#4dd0a0">賣壓5 '+xh9(ZL9.p5[xi])+'</span>'+(isNaN(ZL9.m[xi])?'':(ZL9.m[xi]>0?' <span style="color:#ff9f1a">吸籌</span>':' <span style="color:#22c55e">出貨</span>'));}''',
 '''  if(ZL9&&ZL9.st[xi]){var zp9=[];['壓2','壓1','支1','支2'].forEach(function(nm){if(!isNaN(ZL9.V[nm][xi]))zp9.push('<span style="color:'+(nm[0]==='支'?'#ffc04d':'#3edb8f')+'">'+nm+' '+ZL9.V[nm][xi].toFixed(2)+'</span>');});
   tip.innerHTML+='<br>主力(分點) '+zp9.join(' ')+(isNaN(ZL9.m[xi])?'':(ZL9.m[xi]>0?' <span style="color:#ff9f1a">吸籌</span>':' <span style="color:#22c55e">出貨</span>'));}}'''),
# readout
('''  if(ZR9&&!isNaN(ZR9.s5[xi]))ro9+='|主力5 '+ZR9.s5[xi].toFixed(2)+(isNaN(ZR9.m[xi])?'':(ZR9.m[xi]>0?' 吸':' 出'));}''',
 '''  if(ZR9&&ZR9.st[xi]){var zr9=[];['壓2','壓1','支1','支2'].forEach(function(nm){if(!isNaN(ZR9.V[nm][xi]))zr9.push(nm+' '+ZR9.V[nm][xi].toFixed(2));});
   ro9+='|主力 '+zr9.join(' ')+(isNaN(ZR9.m[xi])?'':(ZR9.m[xi]>0?' 吸':' 出'));}}'''),
# 卡片
('''  if(ZB){var li=-1,q9;for(q9=cur.D.n-1;q9>=0;q9--){if(!isNaN(ZB.s5[q9])){li=q9;break;}}
   if(li>=0){var acc=0,tot=0;for(var q8=cur.D.n-1;q8>=0&&tot<5;q8--){if(isNaN(ZB.m[q8]))continue;tot++;if(ZB.m[q8]>0)acc++;}
    var dv=(cur.D.c[cur.D.n-1]/ZB.s5[li]-1)*100;
    $('cSigSub').textContent=($('cSigSub').textContent?$('cSigSub').textContent+'\\n':'')+'主力(分點):近5筆 '+acc+'吸'+(tot-acc)+'出;5日成本 '+ZB.s5[li].toFixed(2)+'(收盤乖離 '+(dv>=0?'+':'')+dv.toFixed(1)+'%)';}}''',
 '''  if(ZB){var li=-1,q9;for(q9=cur.D.n-1;q9>=0;q9--){if(ZB.st[q9]){li=q9;break;}}
   if(li>=0){var acc=0,tot=0;for(var q8=cur.D.n-1;q8>=0&&tot<5;q8--){if(isNaN(ZB.m[q8]))continue;tot++;if(ZB.m[q8]>0)acc++;}
    var vals=[];['壓2','壓1','支1','支2'].forEach(function(nm){if(!isNaN(ZB.V[nm][li]))vals.push(nm+'='+ZB.V[nm][li].toFixed(2));});
    $('cSigSub').textContent=($('cSigSub').textContent?$('cSigSub').textContent+'\\n':'')+'主力(分點)'+ZB.st[li]+'態:'+vals.join(' ')+';近5筆 '+acc+'吸'+(tot-acc)+'出';}}'''),
# tooltip 文案
('title="券商分點前15大買賣超彙總(夜掃每日更新;僅涵蓋★雙過與持倉追蹤股約15檔)。支撐=近5日(亮)/近20日(暗)主力買超量加權成本;賣壓=近5日賣超成本(僅畫在收盤之上時)。吸籌/出貨判別=籌碼集中度:買超合計>賣超合計→買方集中(主力吃貨、散戶分散出)=吸籌;反之=倒貨。僅顯示參考,不進回測、不影響引擎訊號"',
 'title="券商分點前15大買賣超彙總(夜掃每日更新;僅涵蓋★雙過與持倉追蹤股約15檔)。狀態機:恆兩條;吸籌日(買超合計>賣超合計=買方集中、賣方家數多)才刷新支撐=近5日買超成本;出貨日(反之=主力倒貨給分散散戶)才刷新壓力=近5日賣超成本;其餘沿用前值。收盤跌破支撐→翻面為壓力(攜號)並保留較低支撐;站上壓力→翻回支撐。四態:支1支2/壓1支2/壓1壓2/壓2支1,壓恆在支之上。僅顯示參考,不進回測、不影響引擎訊號"'),
]
fail=0
for a,b in R:
    n=s.count(a)
    if n!=1:
        print('MISMATCH x%d: %r'%(n,a[:70])); fail+=1
    s=s.replace(a,b)
if fail: sys.exit('FAIL %d'%fail)
open(f,'w',encoding='utf-8').write(s)
print('OK',f)
