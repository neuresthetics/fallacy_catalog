"""Round 3 scoring: reviewers E (strict) and F (practical) vs tests/round3/answer_key.csv (multi-row). Run from the repository root: python3 tests/round3/score.py. Judgments hard-coded below."""
import csv,re,collections
import json
def load_key(path, as_keyed=True):
    """Read answer_key.csv. With as_keyed=True, restore the original (pre-adjudication) key
    values from the original_key column, so the score reproduces the 'as keyed' numbers;
    adjudication is applied by the judgments hard-coded in this script, as in the original run."""
    out = {}
    for r in csv.DictReader(open(path)):
        if as_keyed and r.get('original_key'):
            r.update(json.loads(r['original_key']))
        out[r['id']] = r
    return out
K=load_key('tests/round3/answer_key.csv')
def load(f):
    d=collections.defaultdict(list)
    for r in csv.DictReader(open(f)): d[r['id']].append(r)
    return d
E=load('tests/round3/verdicts_E.csv'); F=load('tests/round3/verdicts_F.csv')
RANK={'flag':2,'possible issue':1,'no issue':0}
def worst(rows): 
    rs=[r for r in rows if r['verdict']!='no issue']
    return max(rs,key=lambda r:RANK[r['verdict']]) if rs else {'verdict':'no issue','entry_ids':rows[0]['entry_ids'] if rows else ''}
ent=lambda r:r['entry_ids'].split(';')[0].strip()
# ---- judgments
# fallacy passages: label wrong (entry -> not acceptable for that passage)
WRONG={('R031','false-analogy'),('R081','disregarding-known-science')}
# adjudication (key overruled): passage -> set of verdicts counted correct
ADJ={'R021':{'no issue','possible issue'},   # excerpt boundary: refutation follows; motive clause is after two replies
     'R040':{'no issue','possible issue'},   # insult not offered as a reason; rhetoric note, not a fallacy
     'R063':{'possible issue','flag'},       # excerpt cut + direct rebuttal (S3) in text: contested
     'R041':{'possible issue','flag'}}       # scholarly-disputed: PI acceptable as well as flag
# mixed: error units per key (passage, unit, matching rule on reviewer rows)
UNITS=[('R006','ad hoc rescue S2-S3',lambda r:'ad-hoc' in r['entry_ids']),
       ('R006','burden / ignorance S4-S5',lambda r:'burden' in r['entry_ids'] or 'ignorance' in r['entry_ids']),
       ('R013','McNamara S3-S4',lambda r:'mcnamara' in r['entry_ids']),
       ('R021','motive attribution / loaded language (S3 end)',lambda r:'jesuitically' in r['error_sentence'] or 'bulverism' in r['entry_ids'] or 'motive' in r['entry_ids']),
       ('R030','sunk cost S2',lambda r:'sunk' in r['entry_ids']),
       ('R036','etymological S3',lambda r:'etymolog' in r['entry_ids']),
       ('R036','false dilemma S4',lambda r:'dilemma' in r['entry_ids']),
       ('R040','loaded language / ad hominem S4',lambda r:'lapdogs' in r['error_sentence']),
       ('R053','straw man S3-S4',lambda r:'straw' in r['entry_ids']),
       ('R060','regression S2',lambda r:'regression' in r['entry_ids']),
       ('R070','base rate S4',lambda r:'base-rate' in r['entry_ids']),
       ('R072','motive / loaded S4',lambda r:'motive' in r['entry_ids'] or 'hominem' in r['entry_ids']),
       ('R072','slippery slope S5',lambda r:'slippery' in r['entry_ids']),
       ('R090','Texas sharpshooter S3',lambda r:'texas' in r['entry_ids'])]
NOT_ERRORS={('R021','motive attribution / loaded language (S3 end)'),('R040','loaded language / ad hominem S4')}  # key overruled
REAL=[i for i in K if K[i]['category']=='real-excerpt']
def agreed_rows(i):
    # row-level agreed: pair each E step with a matching F step (same entry or sentence overlap); flag only if both flag; else PI
    out=[]; usedF=set()
    for r in E[i]:
        if r['verdict']=='no issue': continue
        m=[(j,o) for j,o in enumerate(F[i]) if j not in usedF and o['verdict']!='no issue' and (ent(o)==ent(r) or ov(o['error_sentence'],r['error_sentence'])>=0.5)]
        if m: usedF.add(m[0][0]); o_=m[0][1]
        v='flag' if m and r['verdict']=='flag' and o_['verdict']=='flag' else 'possible issue'
        lab=ent(r) if not m or ent(o_)==ent(r) else ent(r)+'|'+ent(o_)
        out.append({'verdict':v,'entry_ids':lab,'error_sentence':r['error_sentence']})
    for j,o in enumerate(F[i]):
        if o['verdict']!='no issue' and j not in usedF:
            out.append({'verdict':'possible issue','entry_ids':ent(o),'error_sentence':o['error_sentence']})
    return out or [{'verdict':'no issue','entry_ids':'','error_sentence':''}]
tok=lambda s:set(re.findall(r"[a-z0-9']+",s.lower()))
def ov(a,b):
    ta,tb=tok(a),tok(b); return len(ta&tb)/max(1,min(len(ta),len(tb))) if ta and tb else 0
AG={i:agreed_rows(i) for i in K}
REV={'E (strict)':E,'F (practical)':F,'Agreed':AG}
def label_ok(i,rows):
    labs=set()
    for r in rows:
        if r['verdict']=='flag':
            for l in r['entry_ids'].split('|'): labs.add(l.strip())
    ok=[(i,l) not in WRONG for l in labs]
    return 'ok' if ok and all(ok) else ('split' if any(ok) else 'wrong')
def passage_scores(rv,ids,adj=False):
    s=collections.Counter()
    for i in ids:
        k=K[i]; w=worst(rv[i]); v=w['verdict']; t=k['truth']
        if t in('legit','no-argument'):
            s[t+'_hard']+=v=='flag'; s[t+'_soft']+=v=='possible issue'; s[t+'_n']+=1
        elif t=='fallacy':
            s['f_n']+=1
            if adj and i in ADJ:
                s['f_adj_ok']+= v in ADJ[i]
                if v in ADJ[i] and v=='flag': s['f_ok']+= label_ok(i,rv[i])=='ok'
                if v in ADJ[i] and v!='flag': s['f_adjPI']+=1
                if v not in ADJ[i]: s['f_hard' if v=='no issue' else 'f_soft']+=1
                continue
            if v=='flag':
                lo=label_ok(i,rv[i]); s['f_'+lo]+=1
            elif v=='possible issue': s['f_soft']+=1
            else: s['f_hard']+=1
        else:
            s['m_n']+=1; s['m_worst_'+v]+=1
    return s
def unit_scores(rv,adj=False):
    s=collections.Counter()
    for (i,u,fn) in UNITS:
        rows=[r for r in rv[i] if r['verdict']!='no issue' and fn(r)]
        best=max((RANK[r['verdict']] for r in rows),default=0)
        if adj and (i,u) in NOT_ERRORS:
            s['overcall']+= best==2; s['overcall_pi']+=best==1; continue
        s['n']+=1; s[{2:'found',1:'soft',0:'missed'}[best]]+=1
    return s
def es_match(rv):
    n=m=0
    for i,k in K.items():
        if k['truth'] not in ('fallacy','mixed') or not k['error_sentences']: continue
        ks=[re.sub(r'^S\d+[^:]*:\s*','',x.strip()) for x in k['error_sentences'].split(' | ')]
        for r in rv[i]:
            if r['verdict']=='no issue': continue
            n+=1; m+= any(ov(x,r['error_sentence'])>=0.6 for x in ks)
    return m,n
ALL=list(K)
o=["# Round 3 scores: reviewers E (strict) and F (practical) vs held-out key 3\n",
"Catalog: fallacy_catalog @ 46e8036 (v0.5.0). 100 passages: 43 legit, 11 no-argument, 35 fallacy, 11 mixed (14 keyed error units). 20 are real public-domain excerpts. E wrote 114 rows and F wrote 108 (one per step). 'Agreed' = METHOD (h) at row level: a step is flagged only if both reviewers flag it; any other non-clear row becomes possible issue. Passage level uses the worst row. 'As keyed' scores against the key unchanged. 'Adjudicated' applies the key overrules in errors.csv: R021 and R040 are not errors; for R041 and R063 both possible issue and flag count as correct. Generated by `score.py`.\n"]
o.append("## Row and passage totals\n\n| | rows | flag rows | possible-issue rows | no-issue rows | passages flagged | passages possible issue only | passages clear |\n|---|---|---|---|---|---|---|---|")
for nm,rv in REV.items():
    rows=[r for i in K for r in rv[i] if not (nm=='Agreed' and r['verdict']=='no issue')]; ws=[worst(rv[i])['verdict'] for i in K]
    o.append(f"| {nm} | {len(rows)} | {sum(r['verdict']=='flag' for r in rows)} | {sum(r['verdict']=='possible issue' for r in rows)} | {sum(r['verdict']=='no issue' for r in rows)} | {ws.count('flag')} | {ws.count('possible issue')} | {ws.count('no issue')} |")
o.append("\n## False positives (passage level, worst row)\n\n| | legit (43): hard FP | legit: soft FP | no-argument (11): hard FP | no-argument: soft FP |\n|---|---|---|---|---|")
for nm,rv in REV.items():
    s=passage_scores(rv,ALL); o.append(f"| {nm} | {s['legit_hard']} | {s['legit_soft']} | {s['no-argument_hard']} | {s['no-argument_soft']} |")
o.append("\n## Fallacy passages (35), passage level\n\n| | hit, acceptable label | hit, wrong label | hit, labels split | soft miss | hard miss |\n|---|---|---|---|---|---|")
for nm,rv in REV.items():
    s=passage_scores(rv,ALL); o.append(f"| {nm}, as keyed | {s['f_ok']} | {s['f_wrong']} | {s['f_split']} | {s['f_soft']} | {s['f_hard']} |")
o.append("\nAdjudicated: R041 and R063 count as correct when the verdict is possible issue or flag.\n\n| | hit, acceptable label | correct possible issue (contested) | hit, wrong label | hit, split | soft miss | hard miss |\n|---|---|---|---|---|---|---|")
for nm,rv in REV.items():
    s=passage_scores(rv,ALL,adj=True); o.append(f"| {nm}, adjudicated | {s['f_ok']} | {s['f_adjPI']} | {s['f_wrong']} | {s['f_split']} | {s['f_soft']} | {s['f_hard']} |")
o.append("\nWrong labels: R031 false-analogy (both reviewers; key: converse accident, which fits exactly, but the catalog has no tie-break between generalization and comparison) and R081 disregarding-known-science (E; the catalog's inflation-of-conflict entry fits exactly, but it has no family or aliases, so it is hard to find).")
o.append("\n## Mixed passages (11 passages, 14 keyed error units)\n\n| | units found (flag) | soft (possible issue) | missed | rows flagged beyond the key |\n|---|---|---|---|---|")
for nm,rv in REV.items():
    s=unit_scores(rv); o.append(f"| {nm}, as keyed | {s['found']}/{s['n']} | {s['soft']} | {s['missed']} | 0 in mixed passages |")
for nm,rv in REV.items():
    s=unit_scores(rv,adj=True); o.append(f"| {nm}, adjudicated (12 real units) | {s['found']}/{s['n']} | {s['soft']} | {s['missed']} | overcalls on the 2 overruled units: {s['overcall']} flag, {s['overcall_pi']} possible issue |")
o.append("\nPer unit:\n\n| passage | unit | E | F | real error? |\n|---|---|---|---|---|")
for (i,u,fn) in UNITS:
    def b(rv): 
        rows=[r for r in rv[i] if r['verdict']!='no issue' and fn(r)]
        return max(rows,key=lambda r:RANK[r['verdict']])['verdict']+' '+ent(max(rows,key=lambda r:RANK[r['verdict']])) if rows else 'no issue'
    o.append(f"| {i} | {u} | {b(E)} | {b(F)} | {'NO (key overruled)' if (i,u) in NOT_ERRORS else 'yes'} |")
o.append("""
**Extra flags beyond the key's error sentences, all passages:**
- R092, both reviewers: possible issue, unrepresentative-sample on S1 ("counted the people in one corner ... multiplied by the area"). **This is a real error the key missed.** One corner, counted for ten seconds, can't be assumed representative of the whole square, and the method is garbled: a count is multiplied by an area, not a density. Possible issue is right.
- R082, both reviewers: a second flag, ad-hoc-rescue, on S3 ("the fidgeting and tears must be about something going on at home"). The key includes S3 in its single psychologist's-fallacy error. Explaining away contrary evidence to protect the claim is a separate move, so two labels are legitimate under METHOD (c). It is real, not a false positive.
- R021, E: flag, bulverism. This is an overcall once the key is overruled (excerpt boundary).
- No false positives on any legit or no-argument passage.""")
o.append("\n## Error-sentence location\n\n| | flag/possible-issue rows on fallacy or mixed passages that overlap a key error sentence (≥60% of tokens) |\n|---|---|")
for nm,rv in (('E (strict)',E),('F (practical)',F)):
    m,n=es_match(rv); o.append(f"| {nm} | {m}/{n} |")
o.append("\nHand check of the non-overlapping rows. R092 S1 (both) is the extra real error above. For R021 (E), R041 (E), R063 (E) and R084 (F), the real-excerpt key describes the location in a parenthetical, and the reviewer quoted inside it. For R100 (both), the reviewer quoted the premise and a truncated conclusion. **Every flagged or possible-issue row is at the keyed location, or at a real error the key missed.**")
# real excerpts
o.append("\n## Real public-domain excerpts (20)\n\n| id | truth (key) | adjudicated | E worst | F worst |\n|---|---|---|---|---|")
ADJTXT={'R021':'no issue / possible issue (excerpt boundary)','R041':'flag or possible issue (contested)','R063':'possible issue or flag (excerpt + direct rebuttal)','R084':'fallacy (flag); possible issue defensible','R099':'fallacy at speaker level'}
for i in REAL:
    we,wf=worst(E[i]),worst(F[i])
    o.append(f"| {i} | {K[i]['truth']} | {ADJTXT.get(i,'= key')} | {we['verdict']} {ent(we) if we['verdict']!='no issue' else ''} | {wf['verdict']} {ent(wf) if wf['verdict']!='no issue' else ''} |")
o.append("""
| real excerpts | E | F |
|---|---|---|
| FP on the 14 legit/no-argument excerpts | 0 | 0 |
| keyed fallacy/mixed excerpts (6): flagged, as keyed | 4 (R021, R041, R067, R084) | 2 (R067, R099) |
| matches adjudicated answer (6) | 4 (R041, R063, R067, R084) | 5 (R021, R041, R063, R067, R099; R084 possible issue is defensible) |

4 of the 5 passage-level E/F disagreements this round are real excerpts (R021, R041, R084, R099). Constructed items gave near-perfect agreement, and real texts are where the method is still under-specified: excerpt boundaries, dialogue speakers, and contested scholarly readings.""")
# agreement
ws=lambda rv:[worst(rv[i])['verdict'] for i in K]
we,wf=ws(E),ws(F); agree=sum(a==b for a,b in zip(we,wf)); n=100
vs=['flag','possible issue','no issue']
pe=sum((we.count(v)/n)*(wf.count(v)/n) for v in vs); kappa=(agree/n-pe)/(1-pe)
dis=[i for i in K if worst(E[i])['verdict']!=worst(F[i])['verdict']]
# step-level label agreement
steps=both=same=0; lab_dis=[]
for i in K:
    for r in E[i]:
        if r['verdict']=='no issue': continue
        m=[o for o in F[i] if o['verdict']!='no issue' and (ent(o)==ent(r) or ov(o['error_sentence'],r['error_sentence'])>=0.5)]
        steps+=1
        if m:
            both+=1; same+= ent(m[0])==ent(r)
            if ent(m[0])!=ent(r) or m[0]['verdict']!=r['verdict']: lab_dis.append(f"{i} E {r['verdict']} {ent(r)} / F {m[0]['verdict']} {ent(m[0])}")
o.append(f"""
## E–F agreement

| measure | value |
|---|---|
| passage worst-verdict agreement | {agree}/100 (kappa {kappa:.3f}); differ on {', '.join(dis)} |
| E non-clear steps matched by an F non-clear step | {both}/{steps} |
| same entry on matched steps | {same}/{both} |
| matched steps with a different verdict or entry | {'; '.join(lab_dis)} |
| unmatched E steps | R021 bulverism (F no issue), R099 (E no issue, F flag; counted from F's side) |
""")
f=open('tests/round3/FIXES.md').read(); o.append('\n'+f[f.index('## Cumulative results'):])
open('tests/round3/scores.md','w').write("\n".join(o)); print("\n".join(o))
