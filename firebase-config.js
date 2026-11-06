// Firebase 主控台「專案設定 → 你的應用程式 → SDK 設定」裡的 firebaseConfig。
// 這些值本來就會出現在前端，不是密碼；資料安全靠 firestore.rules 把關。
// 改成 null 時，網頁照常運作，只是沒有登入／同步功能。
export default {
  apiKey: "AIzaSyAUvUu584JP-VU-oYbhtYMb-XHtSRdGIbc",
  authDomain: "flashcard-da54d.firebaseapp.com",
  projectId: "flashcard-da54d",
  storageBucket: "flashcard-da54d.firebasestorage.app",
  messagingSenderId: "994618200407",
  appId: "1:994618200407:web:f2a563398a72284aceae12"
};
