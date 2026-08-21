# -*- coding: utf-8 -*-
# 8/21 附圖:成交金額(億,含5/10日均)+KD(9,3,3);雙側刻度;與主圖縮放/平移/十字線連動
import sys
f=sys.argv[1]
s=open(f,encoding='utf-8').read()
R=[
# R1 bars 補量/金額
("bars.push({d:r.date,o:o1,h:h1,l:l1,c:c1,vw:+r.Trading_money/vol});",
 "bars.push({d:r.date,o:o1,h:h1,l:l1,c:c1,vw:+r.Trading_money/vol,v:vol,m:+r.Trading_money});"),
# R2 HTML 兩塊附圖
('''    <div id="tip"></div>''',
 '''    <div id="tip"></div>
    <div style="font-size:11.5px;color:#9a9a9a;margin:8px 0 3px"><b>成交金額(億)</b> <span style="color:#ffd37a">5日均</span> <span style="color:#4fd8ff">10日均</span></div>
    <canvas id="cvAMT" height="92"></canvas>
    <div style="font-size:11.5px;color:#9a9a9a;margin:8px 0 3px"><b>KD(9,3,3)</b> <span style="color:#ffd37a">K</span> <span style="color:#4fd8ff">D</span> <span style="color:#666">(20/80 虛線)</span></div>
    <canvas id="cvKD" height="92"></canvas>'''),
# R3 GEO 後畫附圖
(" GEO={W:W,H:H,padL:padL,padR:padR,padT:padT,padB:padB,cw:cw,hi:hi,lo:lo,v0:v0,v1:v1};",
 " GEO={W:W,H:H,padL:padL,padR:padR,padT:padT,padB:padB,cw:cw,hi:hi,lo:lo,v0:v0,v1:v1};\n drawSubs(-1);"),
# R4 新函式(掛在 xClear 前)
("function xClear(){",
 '''function subCache(){
 if(cur._sub)return cur._sub;
 var bs=cur.bars,n=bs.length,amt=[],K=[],D9=[],i,j;
 for(i=0;i<n;i++)amt.push((bs[i].m||0)/1e8);
 var k=50,d=50;
 for(i=0;i<n;i++){var lo=Infinity,hi=-Infinity;
  for(j=Math.max(0,i-8);j<=i;j++){if(bs[j].l<lo)lo=bs[j].l;if(bs[j].h>hi)hi=bs[j].h;}
  var rsv=hi>lo?(bs[i].c-lo)/(hi-lo)*100:50;
  k=k*2/3+rsv/3;d=d*2/3+k/3;K.push(k);D9.push(d);}
 cur._sub={amt:amt,a5:smaAll(amt,5),a10:smaAll(amt,10),K:K,D:D9};
 return cur._sub;}
function drawSubs(hv){
 if(!cur||!GEO)return;
 var S=subCache(),G=GEO,dpr=window.devicePixelRatio||1;
 function fmtA(v){return v>=100?v.toFixed(0):v>=10?v.toFixed(1):v.toFixed(2)}
 function labels(q,W,txt,y){q.font='10px sans-serif';
  q.fillStyle='#9a9a9a';q.textAlign='left';q.fillText(txt,W-G.padR+4,y+3);
  var tw=q.measureText(txt).width;
  q.fillStyle='rgba(0,0,0,.6)';q.fillRect(G.padL+1,y-6,tw+6,12);
  q.fillStyle='#9a9a9a';q.fillText(txt,G.padL+4,y+3);}
 function vline(q,H2){if(hv<G.v0||hv>=G.v1)return;var x=G.padL+(hv-G.v0)*G.cw+G.cw/2;
  q.strokeStyle='rgba(255,211,122,.5)';q.setLineDash([3,3]);q.beginPath();q.moveTo(x,2);q.lineTo(x,H2-2);q.stroke();q.setLineDash([]);}
 function panel(id,draw){var cv=$(id);if(!cv)return;var W=G.W,H2=92;
  cv.width=W*dpr;cv.height=H2*dpr;var q=cv.getContext('2d');q.setTransform(dpr,0,0,dpr,0,0);
  q.fillStyle='#000';q.fillRect(0,0,W,H2);draw(q,W,H2);vline(q,H2);}
 panel('cvAMT',function(q,W,H2){
  var mx=0,i;for(i=G.v0;i<G.v1;i++){if(S.amt[i]>mx)mx=S.amt[i];
   if(!isNaN(S.a5[i])&&S.a5[i]>mx)mx=S.a5[i];if(!isNaN(S.a10[i])&&S.a10[i]>mx)mx=S.a10[i];}
  mx=(mx||1)*1.08;
  function Y2(v){return H2-5-(v/mx)*(H2-14);}
  q.strokeStyle='#1d1d1d';
  for(var t=1;t<=2;t++){var gv=mx*t/3,gy=Y2(gv);
   q.beginPath();q.moveTo(G.padL,gy);q.lineTo(W-G.padR,gy);q.stroke();labels(q,W,fmtA(gv),gy);}
  for(i=G.v0;i<G.v1;i++){var x=G.padL+(i-G.v0)*G.cw;
   var up=cur.bars[i].c>=cur.bars[i].o;
   q.fillStyle=up?'rgba(236,74,74,.8)':'rgba(22,185,129,.8)';
   var bw=Math.max(1,G.cw*0.6),y=Y2(S.amt[i]);
   q.fillRect(x+(G.cw-bw)/2,y,bw,Math.max(1,H2-5-y));}
  function ln(arr,col){q.strokeStyle=col;q.lineWidth=1.2;q.beginPath();var on=false;
   for(var i4=G.v0;i4<G.v1;i4++){var v=arr[i4];if(isNaN(v)){on=false;continue;}
    var x2=G.padL+(i4-G.v0)*G.cw+G.cw/2,y2=Y2(v);
    if(!on){q.moveTo(x2,y2);on=true;}else q.lineTo(x2,y2);}
   q.stroke();q.lineWidth=1;}
  ln(S.a5,'#ffd37a');ln(S.a10,'#4fd8ff');});
 panel('cvKD',function(q,W,H2){
  function Y3(v){return 5+(100-v)/100*(H2-14);}
  [80,50,20].forEach(function(gv){var gy=Y3(gv);
   q.strokeStyle=gv===50?'#1d1d1d':'#2a2a1a';
   if(gv!==50)q.setLineDash([3,3]);
   q.beginPath();q.moveTo(G.padL,gy);q.lineTo(W-G.padR,gy);q.stroke();q.setLineDash([]);
   labels(q,W,String(gv),gy);});
  function ln2(arr,col){q.strokeStyle=col;q.lineWidth=1.2;q.beginPath();var on=false;
   for(var i5=G.v0;i5<G.v1;i5++){var x3=G.padL+(i5-G.v0)*G.cw+G.cw/2,y3=Y3(arr[i5]);
    if(!on){q.moveTo(x3,y3);on=true;}else q.lineTo(x3,y3);}
   q.stroke();q.lineWidth=1;}
  ln2(S.K,'#ffd37a');ln2(S.D,'#4fd8ff');});
}
function xClear(){'''),
# R5 十字線:tip/readout 補值+附圖連動
(" $('readout').textContent=ro9;}",
 ''' var sb9=(typeof subCache==='function')?subCache():null;
 if(sb9){var fa9=function(v){return v>=100?v.toFixed(0):v>=10?v.toFixed(1):v.toFixed(2)};
  tip.innerHTML+='<br><span style="color:#bbb">額 '+fa9(sb9.amt[xi])+'億</span> <span style="color:#ffd37a">額5 '+(isNaN(sb9.a5[xi])?'—':fa9(sb9.a5[xi]))+'</span> <span style="color:#4fd8ff">額10 '+(isNaN(sb9.a10[xi])?'—':fa9(sb9.a10[xi]))+'</span> | <span style="color:#ffd37a">K '+sb9.K[xi].toFixed(1)+'</span> <span style="color:#4fd8ff">D '+sb9.D[xi].toFixed(1)+'</span>';
  ro9+='|額 '+fa9(sb9.amt[xi])+'億 K '+sb9.K[xi].toFixed(1)+' D '+sb9.D[xi].toFixed(1);}
 if(typeof drawSubs==='function')drawSubs(xi);
 $('readout').textContent=ro9;}'''),
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
