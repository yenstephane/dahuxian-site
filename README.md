# 大戶線網站(dahuxian-site)

台股「統一 B v2 策略」操盤台+大盤儀表板。每晚收盤後由排程自動掃描、更新資料檔並部署。

## 架構
- 靜態前端:`index.html`(操盤台,`watch.html`/`watch/index.html` 為同步副本)、`market.html`(大盤儀表板)
- 資料檔(每晚夜掃覆蓋):`rotation_data.js`(族群訊號分數)、`dahu_filters.js`(濾網/觀察名單/SCANST/期交所大額交易人)
- `flask_app.py`:PythonAnywhere 入口——供應整站靜態檔+`/api/taiex` 盤中大盤代理(取代 Netlify `_redirects`)
- `_redirects`:Netlify 時代遺留,PythonAnywhere 不使用,留作歷史

## 部署(PythonAnywhere)
1. Web app 指向本 repo 目錄,WSGI 設定 import `flask_app.app`
2. 夜掃排程以 PythonAnywhere Files API 覆蓋兩個資料 js(靜態檔即時生效,免 reload)
3. 程式碼變更:push 本 repo 後,以 API 覆蓋對應檔案並 reload web app

## 注意
- 免費帳號對外連線有白名單:`mis.twse.com.tw` 若被擋,`/api/taiex` 回 502,前端自動退回盤後價
- 免費 web app 每 3 個月需在後台按一次「Run until…」續命
- 資料源:FinMind(token 由使用者瀏覽器 localStorage 提供)+ TWSE/TPEX 公開 API,皆為瀏覽器直連

僅供研究,非投資建議。
