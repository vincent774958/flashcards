import json,re
s=open('flashcards.html',encoding='utf-8').read()
csvtxt=open('/home/claude/英文單字學習卡.csv',encoding='utf-8-sig').read()
emb=json.dumps(csvtxt,ensure_ascii=False).replace('</','<\\/')
# A. default csv
a=s.index('const DEFAULT_CSV = `'); b=s.index('`;',a)+2
s=s[:a]+'const DEFAULT_CSV = '+emb+';'+s[b:]
# B. parser keeps level
s=s.replace("return rows.map(r=>({word:(r[0]||'').trim(),back:(r[1]||'').trim()})).filter(r=>r.word);",
 "return rows.map(r=>({word:(r[0]||'').trim(),back:(r[1]||'').trim(),level:(r[2]||'').trim()})).filter(r=>r.word&&r.back);")
# C. CSS + HTML
css="""  .secbar{display:flex;gap:8px;align-items:center}
  .sel{display:flex;align-items:center;gap:6px;background:#fff;border:1px solid var(--line);border-radius:999px;padding:0 12px;height:38px;color:var(--navy);min-width:0}
  .sel:hover{border-color:var(--navy)}
  .sel.grow{flex:1}
  .sel select{border:none;background:transparent;font:inherit;font-size:14px;font-weight:500;color:var(--navy);outline:none;width:100%;cursor:pointer;min-width:0}
  .sel svg{width:16px;height:16px;flex:none}
  .secbar .btn.icon{width:38px;height:38px;padding:0;flex:none}
  .done .row{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
  .sheet .btn{margin-top:6px}
"""
s=s.replace("  .toast{",css+"  .toast{",1)
bar="""  <section class="secbar" aria-label="章節">
    <label class="sel"><i data-lucide="layers"></i><select id="levelSel" title="級別"></select></label>
    <label class="sel grow"><i data-lucide="book-open"></i><select id="secSel" title="小節"></select></label>
    <button class="btn icon" id="prevSec" title="上一節"><i data-lucide="chevron-left"></i></button>
    <button class="btn icon" id="nextSec" title="下一節"><i data-lucide="chevron-right"></i></button>
  </section>

  <section class="infobar\""""
s=s.replace('  <section class="infobar"',bar,1)
s=s.replace('<button class="btn primary" id="restart"><i data-lucide="refresh-cw"></i>重新開始</button>',
 '<div class="row"><button class="btn" id="restart"><i data-lucide="refresh-cw"></i>重練本節</button><button class="btn primary" id="nextSecDone">下一節<i data-lucide="chevron-right"></i></button></div>')
s=s.replace('<div class="krow"><span class="k"><kbd>4</kbd></span><span><span class="tag c-easy">Easy</span>：從本次練習中移除</span></div>',
 '''<div class="krow"><span class="k"><kbd>4</kbd></span><span><span class="tag c-easy">Easy</span>：從本次練習中移除</span></div>
    <h4>章節</h4>
    <div class="krow">依 Level 1–6 分大章，每級打亂後每 50 字一節；每節進度分開記錄（✓ 已完成、● 練習中）。匯入自己的 CSV 時，第三欄可填級別。</div>
    <button class="btn" id="useBuiltin"><i data-lucide="refresh-cw"></i>改回內建 6,011 字詞庫</button>''')
# icons
s=s.replace('const ICONS={','const ICONS={"chevron-left": "<path d=\\"m15 18-6-6 6-6\\" />", "chevron-right": "<path d=\\"m9 18 6-6-6-6\\" />", "book-open": "<path d=\\"M12 7v14\\" /> <path d=\\"M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z\\" />", ',1)
# D. state
s=s.replace("let cards=parseCSV(DEFAULT_CSV), queue=[], counts={}, flipped=false, examples=[];",
"""let deck=parseCSV(DEFAULT_CSV), deckId='builtin', cards=[], queue=[], counts={}, flipped=false, examples=[];
let curLevel=null, curSec=0, secCache={};
const SEC_SIZE=50;""")
# save/restore block
a=s.index('/* ---------- Save / resume progress (localStorage) ---------- */'); b=s.index('function showCurrent(){')
s=s[:a]+r"""/* ---------- Sections & progress ---------- */
function hashStr(t){let h=2166136261;for(const c of t){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}return h>>>0;}
const lvOf=c=>c.level||'全部';
function levels(){return [...new Set(deck.map(lvOf))].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));}
function sections(lv){
  if(!secCache[lv]){
    const l=deck.filter(c=>lvOf(c)===lv).sort((a,b)=>hashStr(a.word)-hashStr(b.word)||a.word.localeCompare(b.word));
    const out=[]; for(let i=0;i<l.length;i+=SEC_SIZE) out.push(l.slice(i,i+SEC_SIZE));
    secCache[lv]=out;
  }
  return secCache[lv];
}
const pkey=(lv,i)=>`fc-v2:${deckId}:${lv}:${i}`;
function readProg(lv,i,n){
  try{
    const d=JSON.parse(localStorage.getItem(pkey(lv,i))||'null');
    if(!d||!Array.isArray(d.queue)||!d.queue.every(x=>Number.isInteger(x)&&x>=0&&x<n)) return null;
    if(!d.counts||!['again','hard','good','easy'].every(x=>Number.isFinite(d.counts[x]))) return null;
    return d;
  }catch(e){return null;}
}
function status(lv,i){
  const n=sections(lv)[i].length, d=readProg(lv,i,n);
  if(!d) return '';
  if(!d.queue.length) return ' ✓';
  return (d.queue.length<n||Object.values(d.counts).some(v=>v>0))?' ●':'';
}
function save(){
  try{
    localStorage.setItem(pkey(curLevel,curSec),JSON.stringify({queue,counts}));
    localStorage.setItem('fc-v2:last',JSON.stringify({deckId,level:curLevel,sec:curSec}));
  }catch(e){}
  fillSelectors();
}
function fillSelectors(){
  const ls=levels();
  $('levelSel').innerHTML=ls.map(lv=>{
    const ss=sections(lv), doneN=ss.filter((_,i)=>status(lv,i)===' ✓').length;
    const name=/^\d+$/.test(lv)?`Level ${lv}`:lv;
    return `<option value="${esc(lv)}">${esc(name)}（${doneN}/${ss.length} 節）</option>`;
  }).join('');
  $('levelSel').value=curLevel;
  const ss=sections(curLevel);
  $('secSel').innerHTML=ss.map((c,i)=>`<option value="${i}">第 ${i+1} 節（${c.length} 字）${status(curLevel,i)}</option>`).join('');
  $('secSel').value=String(curSec);
  const last=isLast();
  $('prevSec').disabled=curSec===0&&ls.indexOf(curLevel)===0;
  $('nextSec').disabled=last; $('nextSecDone').style.display=last?'none':'';
}
function isLast(){const ls=levels();return ls.indexOf(curLevel)===ls.length-1&&curSec===sections(curLevel).length-1;}
function loadSection(lv,i){
  const ls=levels(); if(!ls.includes(lv)) lv=ls[0];
  const ss=sections(lv); i=Math.max(0,Math.min(i|0,ss.length-1));
  curLevel=lv; curSec=i; cards=ss[i];
  const d=readProg(lv,i,cards.length);
  if(d){ queue=d.queue; counts=d.counts; showCurrent(); }
  else startSession();
}
function stepSection(dir){
  const ls=levels(); let li=ls.indexOf(curLevel), si=curSec+dir;
  if(si<0){ if(li===0) return; li--; si=sections(ls[li]).length-1; }
  else if(si>=sections(ls[li]).length){ if(li===ls.length-1) return; li++; si=0; }
  loadSection(ls[li],si);
}

/* ---------- Imported deck storage (IndexedDB; decks are too big for localStorage) ---------- */
function idb(){return new Promise((res,rej)=>{const r=indexedDB.open('flashcards',1);r.onupgradeneeded=()=>r.result.createObjectStore('kv');r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error);});}
async function idbSet(k,v){const db=await idb();return new Promise((res,rej)=>{const t=db.transaction('kv','readwrite');t.objectStore('kv').put(v,k);t.oncomplete=()=>res();t.onerror=()=>rej(t.error);});}
async function idbGet(k){const db=await idb();return new Promise((res,rej)=>{const q=db.transaction('kv').objectStore('kv').get(k);q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error);});}
function setDeck(d,id){ deck=d; deckId=id; secCache={}; imgCache.clear(); }

"""+s[b:]
# startSession unchanged; restart button stays. Import handler
s=s.replace("if(parsed.length){ cards=parsed; imgCache.clear(); $('toast').textContent=`已匯入 ${f.name}（${parsed.length} 張卡片）`; startSession(); }",
"if(parsed.length){ const id='imp-'+hashStr(f.name+'|'+parsed.length+'|'+parsed[0].word); setDeck(parsed,id); idbSet('deck:'+id,parsed).catch(()=>{}); $('toast').textContent=`已匯入 ${f.name}（${parsed.length} 張卡片）`; loadSection(levels()[0],0); }")
# init
s=s.replace("if(restore()) showCurrent(); else startSession();",r"""$('levelSel').addEventListener('change',e=>{loadSection(e.target.value,0);e.target.blur();});
$('secSel').addEventListener('change',e=>{loadSection(curLevel,+e.target.value);e.target.blur();});
$('prevSec').addEventListener('click',()=>stepSection(-1));
$('nextSec').addEventListener('click',()=>stepSection(1));
$('nextSecDone').addEventListener('click',()=>stepSection(1));
$('useBuiltin').addEventListener('click',()=>{setDeck(parseCSV(DEFAULT_CSV),'builtin');setInfo(false);$('toast').textContent='已改回內建詞庫';loadSection(levels()[0],0);});
(async()=>{
  let last=null; try{last=JSON.parse(localStorage.getItem('fc-v2:last')||'null');}catch(e){}
  if(last&&last.deckId&&last.deckId!=='builtin'){
    try{const d=await idbGet('deck:'+last.deckId); if(Array.isArray(d)&&d.length) setDeck(d,last.deckId);}catch(e){}
  }
  if(last&&last.deckId===deckId) loadSection(last.level,last.sec); else loadSection(levels()[0],0);
})();""")
open('flashcards.html','w',encoding='utf-8').write(s)
print(len(s))
