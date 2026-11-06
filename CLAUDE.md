# 單字學習卡（PWA）— 專案說明（給 Claude Code）

背誦大考中心「高中英文參考詞彙表（111 學年度）」的單頁網頁 App，部署在 GitHub Pages，iPhone 用 Safari「加入主畫面」當 App 用。使用者：Vincent（繁體中文溝通，偏好簡短回覆）。

## 檔案結構
- `index.html`：整個 App（HTML／CSS／JS 全部 inline），**6,011 字詞庫以 JSON 字串內嵌在 `const DEFAULT_CSV = "...";`**，所以檔案約 1.5 MB。
- `manifest.webmanifest`、`icons/`：PWA 設定與圖示（180／192／512）。
- `sw.js`：Service Worker。App shell 走 network-first 加離線備援；外部卡片照片快取最多約 300 張。**改完 index.html 後要把 `VERSION` 加一**，手機才會拿到新版。
- `data/vocab.csv`：詞庫，三欄「單字, 背面內容（多行）, Level N」，沒有標題列，UTF-8 BOM。
- `data/cards_src/c_00..c_40.txt`：詞庫原始資料，每行 `front|pos.意思|衍生字@…|搭配詞@…|英文例句|中文翻譯`，`-` 代表沒有衍生字；每檔 150 字，順序對應 `data/words.json`（從 PDF 解析出的 6,012 筆：word／pos／level）。medium 的兩筆在 CSV 裡已經合併，所以總數是 6,011。
- `tools/build_csv.py`：把 cards_src 轉成 CSV（路徑是原本 session 的，用之前要改）。
- `tools/embed_into_html.py`：把 CSV 嵌進原始 HTML 並加上章節功能的 patch 腳本（以 `tools/flashcards_original.html` 為底）。

## App 行為
- 卡片背面格式：`word (pos.) 意思` → 【詞性變化】→【搭配詞】→【例句】`English.(中文。)`
- 章節：先依 Level 1–6 分大章，每級用 FNV hash 依單字做固定亂序，再每 50 字切一節（`SEC_SIZE`）。
- 複習：Again／Hard／Good／Easy（鍵盤 1–4）、Space 翻面、Enter 朗讀（Web Speech API, en-US）。
- 進度：localStorage key `fc-v2:<deckId>:<level>:<section>`，另有 `fc-v2:last`。使用者匯入的 CSV 存在 IndexedDB（`flashcards`／`kv`／`deck:<id>`）。
- 卡片照片：LoremFlickr，失敗時退回 Wikimedia Commons。

## 尚未做／可做
- 每個字再補 1–2 句例句（使用者問過，暫緩）。
- 進度跨裝置同步（目前只存在各自的瀏覽器）。

## 部署
推上 `main` 分支後，GitHub Pages（Settings → Pages → Deploy from branch → main / root）會自動更新，網址是 `https://<帳號>.github.io/<repo>/`。
