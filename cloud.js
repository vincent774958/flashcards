// Firebase 帳號登入 + 背誦進度雲端同步。
// 資料結構：users/{uid}            → { last: {deckId, level, sec, t} }
//           users/{uid}/progress/{localStorage key} → { queue, counts, t }
// 合併規則：同一節以 t（最後修改時間）較新的為準。
import config from './firebase-config.js';

const V = '10.12.2';
const $ = id => document.getElementById(id);
const PREFIX = 'fc-v2:';
const LAST = 'fc-v2:last';

const ui = {
  dot: s => { $('acctDot').className = 'dot' + (s ? ' ' + s : ''); },
  msg: (t, ok) => { $('acctMsg').textContent = t || ''; $('acctMsg').classList.toggle('ok', !!ok); },
  state: t => { $('syncState').textContent = t; },
};

if (!config) {
  $('acctLbl').textContent = '未設定';
  $('acctOut').innerHTML = '<p class="note">尚未設定 Firebase，所以還不能登入同步。請在 <b>firebase-config.js</b> 填入 firebaseConfig（見 README）。目前進度只存在這台裝置。</p>';
} else {
  start().catch(e => { console.error(e); ui.dot('err'); ui.msg('無法載入登入元件，請檢查網路後重新整理。'); });
}

async function start() {
  const [{ initializeApp }, A, F] = await Promise.all([
    import(`https://www.gstatic.com/firebasejs/${V}/firebase-app.js`),
    import(`https://www.gstatic.com/firebasejs/${V}/firebase-auth.js`),
    import(`https://www.gstatic.com/firebasejs/${V}/firebase-firestore.js`),
  ]);
  const app = initializeApp(config);
  const auth = A.getAuth(app);
  let db;
  try { db = F.initializeFirestore(app, { localCache: F.persistentLocalCache() }); }
  catch (e) { db = F.getFirestore(app); }

  let user = null;
  const timers = new Map();
  const progRef = k => F.doc(db, 'users', user.uid, 'progress', k);

  // ---- hooks called by the main app on every save ----
  window.cloud = {
    saveProgress(k, d) {
      if (!user) return;
      clearTimeout(timers.get(k));
      ui.dot('busy');
      timers.set(k, setTimeout(() => {
        timers.delete(k);
        F.setDoc(progRef(k), d).then(() => !timers.size && ui.dot('on')).catch(err);
      }, 1500));
    },
    saveLast(last) {
      if (!user) return;
      clearTimeout(timers.get(LAST));
      timers.set(LAST, setTimeout(() => {
        timers.delete(LAST);
        F.setDoc(F.doc(db, 'users', user.uid), { last }, { merge: true }).then(() => !timers.size && ui.dot('on')).catch(err);
      }, 1500));
    },
  };
  function err(e) { console.error(e); ui.dot('err'); ui.state('同步失敗：' + (e.code || e.message)); }

  const readLocal = k => { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } };

  async function syncAll() {
    if (!user) return;
    ui.dot('busy'); ui.state('同步中…');
    const snap = await F.getDocs(F.collection(db, 'users', user.uid, 'progress'));
    const remote = new Map(snap.docs.map(d => [d.id, d.data()]));
    let pulled = 0, pushed = 0;
    const batch = F.writeBatch(db);
    // remote → local
    for (const [k, r] of remote) {
      const l = readLocal(k);
      if (!l || (r.t || 0) > (l.t || 0)) { localStorage.setItem(k, JSON.stringify(r)); pulled++; }
    }
    // local → remote
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (!k || !k.startsWith(PREFIX) || k === LAST || k.includes('/')) continue;
      const l = readLocal(k), r = remote.get(k);
      if (l && Array.isArray(l.queue) && (!r || (l.t || 0) > (r.t || 0))) {
        if (!l.t) l.t = 1;
        batch.set(progRef(k), l); pushed++;
        if (pushed >= 450) break;
      }
    }
    // last position
    const uref = F.doc(db, 'users', user.uid);
    const us = await F.getDoc(uref);
    const rLast = us.exists() ? us.data().last : null, lLast = readLocal(LAST);
    let jump = null;
    if (rLast && (!lLast || (rLast.t || 0) > (lLast.t || 0))) { localStorage.setItem(LAST, JSON.stringify(rLast)); jump = rLast; }
    else if (lLast) batch.set(uref, { last: lLast }, { merge: true });
    await batch.commit();

    const cur = window.fcApp?.current();
    if (jump && cur && jump.deckId === cur.deckId) window.fcApp.goto(jump.level, jump.sec);
    else if (pulled) window.fcApp?.refresh();
    ui.dot('on');
    ui.state(`已同步 ${new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}（下載 ${pulled} 節、上傳 ${pushed} 節）`);
  }

  // ---- auth UI ----
  const MSG = {
    'auth/invalid-credential': 'Email 或密碼錯誤。',
    'auth/wrong-password': 'Email 或密碼錯誤。',
    'auth/user-not-found': '找不到這個帳號，請先註冊。',
    'auth/email-already-in-use': '這個 Email 已經註冊過了，請直接登入。',
    'auth/weak-password': '密碼至少要 6 個字元。',
    'auth/invalid-email': 'Email 格式不正確。',
    'auth/missing-password': '請輸入密碼。',
    'auth/too-many-requests': '嘗試次數太多，請稍後再試。',
    'auth/network-request-failed': '網路連線失敗。',
    'auth/operation-not-allowed': 'Firebase 尚未啟用 Email/Password 登入。',
  };
  const say = e => ui.msg(MSG[e.code] || ('發生錯誤：' + (e.code || e.message)));
  const creds = () => [$('acctEmail').value.trim(), $('acctPw').value];

  $('acctForm').addEventListener('submit', async e => {
    e.preventDefault(); ui.msg('登入中…', true);
    try { await A.signInWithEmailAndPassword(auth, ...creds()); ui.msg(''); } catch (x) { say(x); }
  });
  $('signupBtn').addEventListener('click', async () => {
    if (!$('acctForm').reportValidity()) return;
    ui.msg('建立帳號中…', true);
    try { await A.createUserWithEmailAndPassword(auth, ...creds()); ui.msg('帳號已建立，已自動登入。', true); } catch (x) { say(x); }
  });
  $('resetBtn').addEventListener('click', async () => {
    const email = $('acctEmail').value.trim();
    if (!email) return ui.msg('請先輸入 Email。');
    try { await A.sendPasswordResetEmail(auth, email); ui.msg('已寄出重設密碼信，請到信箱查看。', true); } catch (x) { say(x); }
  });
  $('logoutBtn').addEventListener('click', () => A.signOut(auth));
  $('syncBtn').addEventListener('click', () => syncAll().catch(err));

  A.onAuthStateChanged(auth, u => {
    user = u;
    $('acctOut').hidden = !!u; $('acctIn').hidden = !u;
    $('acctLbl').textContent = u ? (u.email || '已登入').split('@')[0] : '登入';
    if (u) { $('acctWho').textContent = u.email; ui.msg(''); syncAll().catch(err); }
    else { ui.dot(''); }
  });

  // sync again when the app comes back to the foreground (e.g. switched from phone to computer)
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && user) syncAll().catch(err); });
}
