# -*- coding: utf-8 -*-
# 8/21 法人線 v2:翻面階梯狀態機(壓恆在支上;跌破翻壓×1.002267;保留下層;收復移除;壓縮上緣)
import sys
f=sys.argv[1]
s=open(f,encoding='utf-8').read()
OLD_FN='''function weiLines(bars,netMap){
 var n=bars.length,rows=[],i,j;
 for(i=0;i<n;i++){var nv=netMap[bars[i].d];
  rows.push({has:nv!==undefined,net:nv||0,p:(bars[i].o+bars[i].h+bars[i].l+bars[i].c)/4});}
 function cost(i,side){var s=0,w=0,cnt=0;
  for(j=i;j>=0&&cnt<2;j--){if(!rows[j].has)continue;var x=rows[j].net;
   if(side===1?x>0:x<0){var a=Math.abs(x);s+=a*rows[j].p;w+=a;cnt++;}}
  return w>0?s/w:NaN;}
 var P=new Array(n).fill(NaN),S=new Array(n).fill(NaN),dP=new Array(n).fill(false),dS=new Array(n).fill(false);
 var buy=[],sell=[],runP=0,runS=0;
 var c=bars.map(function(b){return b.c});
 for(i=0;i<n;i++){
  var p2=cost(i,-1),s2=cost(i,1);
  if(i===0||isNaN(P[i-1])){P[i]=p2;}
  else{var below=c[i-1]<P[i-1];
   P[i]=isNaN(p2)?P[i-1]:(below?Math.min(P[i-1],p2):p2);
   if(below){dP[i]=true;runP++;if(runP>=4&&!isNaN(P[i])&&c[i]>P[i])buy.push(i);}else runP=0;}
  if(i>0&&isNaN(P[i]))P[i]=P[i-1];
  if(i===0||isNaN(S[i-1])){S[i]=s2;}
  else{var above=c[i-1]>S[i-1];
   S[i]=isNaN(s2)?S[i-1]:(above?Math.max(S[i-1],s2):s2);
   if(above){dS[i]=true;runS++;if(runS>=4&&!isNaN(S[i])&&c[i]<S[i])sell.push(i);}else runS=0;}
  if(i>0&&isNaN(S[i]))S[i]=S[i-1];
 }
 return{P:P,S:S,dP:dP,dS:dS,buy:buy,sell:sell};}'''
NEW_FN='''function weiLines(bars,netMap,sid){
 // v2 翻面階梯(2026-08-21):支2=基準B、支1=B×間距;收盤跌破B→兩層×1.002267翻為壓力層(壓1近/壓2遠),B清空;
 // 反彈日重錨B=收盤/級距(間距壓縮為1.002267);收盤越過支1且近2日法人買超→升級B=收盤/級距(間距回復級距);
 // 收盤站上壓力層→該層移除(快訊)。級距:個股對照表,預設4.0009%。
 var GK={'3081':1.018685,'2327':1.018685,'2492':1.018685,'2330':1.028845,'6414':1.028845,'4979':1.028845,'2337':1.028845,'4991':1.028845,'2455':1.028845};
 var g=GK[sid]||1.040009,EPS=1.002267,n=bars.length;
 function A(){return new Array(n).fill(NaN)}
 var S1=A(),S2=A(),R1=A(),R2=A(),buy=[],sell=[];
 var B=null,sp=g,flips=[];
 function net(i){if(i<0)return 0;var v=netMap[bars[i].d];return v==null?0:v;}
 for(var i=0;i<n;i++){var c=bars[i].c;
  var m0=flips.length;
  flips=flips.filter(function(v){return c<v;});
  if(flips.length<m0)buy.push(i);
  if(B===null){
   if(c<(flips.length?flips[0]:Infinity)&&(net(i)>0||(i>0&&c>bars[i-1].c))){B=c/g;sp=EPS;}
  }else if(c<B){
   flips.push(B*EPS);flips.push(B*sp*EPS);
   flips=flips.filter(function(v){return c<v;});
   flips.sort(function(a,b){return a-b});flips=flips.slice(0,2);
   sell.push(i);B=null;
  }else if(flips.length===0&&c>B*sp&&(net(i)>0||net(i-1)>0)){B=c/g;sp=g;}
  if(B!=null){S2[i]=B;if(c>=B*sp)S1[i]=B*sp;}
  if(flips.length>0)R1[i]=flips[0];
  if(flips.length>1)R2[i]=flips[1];
 }
 return{S1:S1,S2:S2,R1:R1,R2:R2,buy:buy,sell:sell,g:g};}'''
R=[
(OLD_FN,NEW_FN),
(' var wei=weiLines(bars,netMap);',' var wei=weiLines(bars,netMap,sid);'),
('''  wline(WE.P,WE.dP,'#3ef94a');
  wline(WE.S,WE.dS,'#ffd700');''',
 '''  var wl2=function(arr,color,lw){g.strokeStyle=color;g.lineWidth=lw;g.beginPath();var op7=false;
   for(var i7=v0;i7<vE;i7++){if(arr[i7]==null||isNaN(arr[i7])){op7=false;continue;}
    var x7=padL+(i7-v0)*cw,y7=Y(arr[i7]);
    if(!op7){g.moveTo(x7,y7);op7=true;}else g.lineTo(x7,y7);
    g.lineTo(x7+cw,y7);}
   g.stroke();};
  wl2(WE.R2,'#2a8f3a',1.1);
  wl2(WE.R1,'#3ef94a',1.5);
  wl2(WE.S1,'#b89b3a',1.1);
  wl2(WE.S2,'#ffd700',1.5);'''),
("if(wl9.buy.length&&wl9.buy[wl9.buy.length-1]===n-1)ex9='★ 法人線快訊:今日收盤站上短窗大戶線(快訊,非引擎訊號)';",
 "if(wl9.buy.length&&wl9.buy[wl9.buy.length-1]===n-1)ex9='★ 法人線快訊:今日收盤站上壓力層→該層收復移除(非引擎訊號)';"),
("else if(wl9.sell.length&&wl9.sell[wl9.sell.length-1]===n-1)ex9='★ 法人線快訊:今日收盤跌破短窗大戶線(快訊,非引擎訊號)';",
 "else if(wl9.sell.length&&wl9.sell[wl9.sell.length-1]===n-1)ex9='★ 法人線快訊:今日收盤跌破支撐基準→翻面為壓力層(非引擎訊號)';"),
(''' if($('wx')&&$('wx').checked&&cur.wei)tip.innerHTML+='<br><span style="color:#3ef94a">法人壓 '+xh9(cur.wei.P[xi])+'</span> <span style="color:#ffd700">法人支 '+xh9(cur.wei.S[xi])+'</span>';''',
 ''' if($('wx')&&$('wx').checked&&cur.wei)tip.innerHTML+='<br><span style="color:#3ef94a">法人壓1 '+xh9(cur.wei.R1[xi])+'</span> <span style="color:#2a8f3a">壓2 '+xh9(cur.wei.R2[xi])+'</span> <span style="color:#ffd700">支1 '+xh9(cur.wei.S1[xi])+'</span> <span style="color:#b89b3a">支2 '+xh9(cur.wei.S2[xi])+'</span>';'''),
(''' if($('wx')&&$('wx').checked&&cur.wei){var wp9=cur.wei.P[xi],ws9=cur.wei.S[xi];ro9+='|法人壓 '+((wp9==null||isNaN(wp9))?'—':wp9.toFixed(2))+' 支 '+((ws9==null||isNaN(ws9))?'—':ws9.toFixed(2));}''',
 ''' if($('wx')&&$('wx').checked&&cur.wei){var xr9=function(v){return (v==null||isNaN(v))?'—':v.toFixed(2)};ro9+='|法人 壓1 '+xr9(cur.wei.R1[xi])+' 壓2 '+xr9(cur.wei.R2[xi])+' 支1 '+xr9(cur.wei.S1[xi])+' 支2 '+xr9(cur.wei.S2[xi]);}'''),
('title="近2個法人賣超(買超)日的量加權成本棘輪(原名韋式快訊線);價格在線下(上)連續≥4根後,收盤站上壓線/跌破支線=快訊。以CPO族群2026-07-22五檔校準:4/5正中、1檔晚一日。僅顯示參考,不進回測、不影響引擎訊號"',
 'title="v2 翻面階梯(2026-08-21 以韋氏 13 檔錨點校準):支2=基準、支1=基準×級距;收盤跌破基準→翻面為壓力層(×1.002267,壓1近/壓2遠)並保留下層;反彈日重錨、間距壓縮;收盤站上壓力層=收復快訊。壓力恆在支撐之上。級距個股對照(聯亞/國巨/華新科1.8685%、台積/樺漢等2.8845%、預設4.0009%)。僅顯示參考,不進回測、不影響引擎訊號"'),
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
