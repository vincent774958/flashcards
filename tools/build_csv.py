import json,csv,re
w=json.load(open('words.json'))
P=r'(?:n|v|adj|adv|prep|conj|pron|art|aux|int)\.'
rows=[];issues=[]
for b in range(41):
    lines=[l for l in open(f'cards/c_{b:02d}.txt',encoding='utf-8').read().split('\n') if l.strip()]
    for i,l in enumerate(lines):
        front,head,der,col,ex,tr=[x.strip() for x in l.split('|')]
        h=re.sub(r'(^|；)\s*('+P+r'(?:/'+P+r')*)\s*',lambda m:f"{m.group(1)}({m.group(2)}) ",head)
        if not h.startswith('('): issues.append(front)
        back=[f"{front} {h}"]
        if der!='-':
            back.append('【詞性變化】')
            for d in der.split('@'):
                d=d.strip(); mm=re.match(r'^(.+?)\s+('+P+r'(?:/'+P+r')*)\s+(.*)$',d)
                back.append(f"{mm.group(1)} ({mm.group(2)}) {mm.group(3)}" if mm else d)
                if not mm: issues.append('der:'+d)
        back.append('【搭配詞】'); back+=[c.strip() for c in col.split('@')]
        back.append('【例句】'); back.append(f"{ex}({tr})")
        rows.append([front,'\n'.join(back),f"Level {w[b*150+i]['level']}"])
with open('英文單字學習卡.csv','w',newline='',encoding='utf-8-sig') as fh:
    cw=csv.writer(fh); cw.writerow(['正面','背面','級別']); cw.writerows(rows)
print(len(rows),issues[:20],len(issues))
import random;random.seed(3)
for r in [rows[144]]+random.sample(rows,3): print('====',r[0],r[2]);print(r[1])
