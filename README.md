# 單字學習卡

大考中心高中英文參考詞彙 6,011 字的單字卡網頁 App，支援 iPhone「加入主畫面」與離線使用。

## 部署到 GitHub Pages
1. 在 GitHub 建一個 **public** repo（例如 `flashcards`），把這個資料夾的所有檔案推上 `main`。
2. 到 repo 的 **Settings → Pages**，Source 選 **Deploy from a branch**，Branch 選 **main / (root)**，按 Save。
3. 約 1 分鐘後，網址會是 `https://<你的帳號>.github.io/flashcards/`。

## 裝到 iPhone
用 **Safari** 打開上面的網址 → 點分享按鈕 → **加入主畫面**。之後從主畫面圖示打開就是全螢幕 App；開過一次後，沒有網路也能用。

## 開啟帳號同步（Firebase，免費）
1. 到 https://console.firebase.google.com 建立專案（Google Analytics 可關掉）。
2. **Build → Authentication → Get started → Sign-in method**，啟用 **Email/Password**。
3. 同一頁的 **Settings → Authorized domains**，新增 `<你的帳號>.github.io`。
4. **Build → Firestore Database → Create database**，位置選 `asia-east1 (Taiwan)`，模式選 production。建立後到 **Rules** 分頁，貼上 `firestore.rules` 的內容，按 Publish。
5. **專案設定（齒輪）→ 一般 → 你的應用程式 → Web（</>）**，註冊一個 Web App，把產生的 `firebaseConfig` 貼進 `firebase-config.js`，取代 `export default null;`。
6. 推上 GitHub。打開網頁按右上角帳號按鈕，註冊後就會開始同步；手機和電腦登入同一個帳號即可。

## 更新
改完 `index.html` 後，把 `sw.js` 裡的 `VERSION` 加一（例如 `v1` → `v2`）再推上去；手機重開 App 一兩次就會換成新版。
