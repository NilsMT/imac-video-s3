#!/usr/bin/env python3
"""
audit_derush.py - audits Parent/Plan_X/Prise_Y/*.WAV|*.MP4
Usage:  python audit_derush.py "D:\Film\Parent"      (or put it in Parent and double-click)
        add --cross to check chronology/numbering across ALL plans (default: inside each Plan)
"""
import re, sys, os, argparse, traceback
from pathlib import Path

# ============================ CONFIG ============================
AUDIO = {'.wav'}
VIDEO = {'.mp4', '.mov'}
IGNORE_FILES = {'thumbs.db', 'desktop.ini', '.ds_store'}
IGNORE_DIRS = {'le reste', 'j1', 'j2', 'truc_a_ranger'}   # never audited as Plans
POOL = 'truc_a_ranger'                                    # where lost files are searched
MAX_SHOWN = 15
# HHMM or HHMMSS inside the WAV name (14-32-05, 14h32, 143205, 20240315_1432...). LAST match wins.
TIME_RE = re.compile(r'(?<!\d)([01]\d|2[0-3])[\s._:hH-]?([0-5]\d)(?:[\s._:mM-]?([0-5]\d))?(?!\d)')
# ================================================================

COL = {'ERROR': '\033[91m', 'WARN': '\033[93m', 'INFO': '\033[96m'}
ROOT = None
report, counts = [], {'ERROR': 0, 'WARN': 0, 'INFO': 0}
stats = {'Plans': 0, 'Prises': 0, 'WAV': 0, 'Video': 0}


def say(level, msg, details=()):
    print(f"{COL[level]}[{level}] {msg}\033[0m"); report.append(f"[{level}] {msg}")
    for d in details:
        print(f"\033[90m         {d}\033[0m"); report.append(f"         {d}")
    counts[level] += 1


def section(t):
    print(f"\n\033[1m=== {t} ===\033[0m"); report.extend(["", f"=== {t} ==="])


def rel(p): return str(Path(p).relative_to(ROOT))
def num(name): m = re.search(r'\d+', name); return int(m.group()) if m else 10**9
def skey(p): return (num(p.name), p.name.lower())


def mk(p, warn=True):
    """File -> item. val = seconds (WAV) or camera counter (video). val None if unreadable."""
    is_a = p.suffix.lower() in AUDIO
    val, pre, disp = None, '', p.stem
    if is_a:
        m = TIME_RE.findall(p.stem)
        if m:
            h, mi, s = m[-1]; val = int(h) * 3600 + int(mi) * 60 + int(s or 0)
            disp = f"{val // 3600:02d}:{val % 3600 // 60:02d}:{val % 60:02d}"
    else:
        m = re.match(r'^(.*?)(\d+)$', p.stem)          # 0D8A5111 -> prefix 0D8A, number 5111
        if m: pre, val = m[1], int(m[2])
    if val is None and warn:
        say('WARN', f"Can't read a {'time' if is_a else 'number'} in name: {rel(p)}")
    return dict(kind='A' if is_a else 'V', rel=rel(p), val=val, pre=pre, disp=disp, group=rel(p.parent))


def load(d):
    files = sorted(f for f in d.iterdir() if f.is_file() and f.name.lower() not in IGNORE_FILES)
    A = [mk(f) for f in files if f.suffix.lower() in AUDIO]
    V = [mk(f) for f in files if f.suffix.lower() in VIDEO]
    O = [rel(f) for f in files if f.suffix.lower() not in AUDIO | VIDEO]
    S = [rel(x) for x in d.iterdir() if x.is_dir()]
    return A, V, O, S


# ---------------- sequence checks (blame the outlier, not its neighbours) ----------------
def lnds(vals):
    n = len(vals); L = [1] * n; P = [-1] * n
    for i in range(n):
        for j in range(i):
            if vals[j] <= vals[i] and L[j] + 1 > L[i]: L[i], P[i] = L[j] + 1, j
    k = max(range(n), key=lambda i: (L[i], i)); kept = set()
    while k >= 0: kept.add(k); k = P[k]
    return kept


def check_seq(items, lo, hi, word):
    items = [i for i in items if i['val'] is not None]
    if len(items) < 2: return
    kept = lnds([i['val'] for i in items])
    good = [i for k, i in enumerate(items) if k in kept]
    for k, it in enumerate(items):
        if k in kept: continue
        pk = next((items[j] for j in range(k - 1, -1, -1) if j in kept), None)
        nk = next((items[j] for j in range(k + 1, len(items)) if j in kept), None)
        if pk and it['val'] < pk['val']:
            msg = f"{lo}  {it['rel']} ({it['disp']}) - but previous file {pk['rel']} is {pk['disp']}"
        elif nk and it['val'] > nk['val']:
            msg = f"{hi}  {it['rel']} ({it['disp']}) - but next file {nk['rel']} is {nk['disp']}"
        else:
            msg = f"OUT OF ORDER  {it['rel']} ({it['disp']})"
        b = [g for g in good if g['val'] <= it['val']]; a = [g for g in good if g['val'] > it['val']]
        if b and a: d = f"By its {word} it belongs between: {b[-1]['rel']}  and  {a[0]['rel']}"
        elif a:     d = f"By its {word} it belongs BEFORE: {a[0]['rel']}"
        elif b:     d = f"By its {word} it belongs AFTER: {b[-1]['rel']}"
        else:       d = ''
        say('ERROR', msg, [d] if d else [])


def check_video_seq(items, scope):
    items = [i for i in items if i['val'] is not None]
    pres = sorted({i['pre'] for i in items})
    if len(pres) > 1:
        say('INFO', f"Several video name prefixes in {scope}: {', '.join(repr(p) for p in pres)} (each checked separately)")
    for p in pres:
        check_seq([i for i in items if i['pre'] == p], 'NUMBER TOO LOW', 'NUMBER TOO HIGH', 'number')


# ---------------- neighbours + candidate search ----------------
def neigh(pr, idx, k):
    prev = nxt = None
    for q in range(idx - 1, -1, -1):
        L = [i for i in pr[q][k] if i['val'] is not None]
        if L: prev = L[-1]; break
    for q in range(idx + 1, len(pr)):
        L = [i for i in pr[q][k] if i['val'] is not None]
        if L: nxt = L[0]; break
    return prev, nxt


def fits(c, prev, nxt):
    if c['kind'] == 'A':
        return not ((prev and c['val'] < prev['val']) or (nxt and c['val'] > nxt['val']))
    ok = False
    for n, low in ((prev, True), (nxt, False)):
        if n and n['pre'] == c['pre']:
            ok = True
            if (low and c['val'] < n['val']) or (not low and c['val'] > n['val']): return False
    return ok


def find(pr, idx, kinds, loose, pool, quiet=False):
    """Looks for missing WAV/video in (1) loose files of the Plan, (2) TRUC_A_RANGER. Returns nb of candidates."""
    rec = pr[idx]; out = []; total = 0; groups = []
    for k in kinds:
        lab = 'WAV' if k == 'A' else 'VIDEO'
        prev, nxt = neigh(pr, idx, k)
        ref = []
        if prev: ref.append(f"Previous {lab}: {prev['rel']} ({prev['disp']})")
        if nxt:  ref.append(f"Next {lab}    : {nxt['rel']} ({nxt['disp']})")
        for src, items, is_pool in (('loose files of this Plan', loose, False), (POOL, pool, True)):
            c = [i for i in items if i['kind'] == k and i['val'] is not None]
            if prev or nxt:
                c = [i for i in c if fits(i, prev, nxt)]
            elif is_pool:
                out.append(('INFO', f"No neighbouring {lab} in this Plan: can't narrow the search in {POOL} for {rec['rel']}", []))
                continue
            if not c:
                if is_pool and pool: out.append(('WARN', f"Missing {lab} for {rec['rel']}: nothing fitting in {src}", ref))
                continue
            c.sort(key=lambda i: i['val'])
            lines = ref + [f"Candidates in {src}:"] + [f"  -> {i['rel']}  ({i['disp']})" for i in c[:MAX_SHOWN]]
            if len(c) > MAX_SHOWN: lines.append(f"  ... and {len(c) - MAX_SHOWN} more")
            out.append(('WARN', f"Missing {lab} for {rec['rel']}: {len(c)} possible file(s) in {src}", lines))
            total += len(c)
            if is_pool: groups.append({i['group'] for i in c})
    if len(groups) == 2:
        both = sorted(groups[0] & groups[1])
        if both:
            out.append(('INFO', f"Scene folder(s) in {POOL} with BOTH a WAV and a video candidate (likely the missing pair) for {rec['rel']}:",
                        [f"  -> {g}" for g in both]))
    if quiet and total == 0: return 0
    for l, m, d in out: say(l, m, d)
    return total


def place_loose(pr, loose):
    """Loose WAV/MP4 sitting directly in the Plan: where do they belong?"""
    for it in loose:
        if it['val'] is None: continue
        k = it['kind']; lab = 'WAV' if k == 'A' else 'video'
        L = sorted(((q, i) for q, r in enumerate(pr) for i in r[k] if i['val'] is not None and i['pre'] == it['pre']),
                   key=lambda t: t[1]['val'])
        head = f"LOOSE {lab}: {it['rel']} ({it['disp']})"
        if not L:
            say('WARN', f"{head} - no {lab} with the same name pattern in this Plan's Prises, can't place it"); continue
        b = [t for t in L if t[1]['val'] <= it['val']]; a = [t for t in L if t[1]['val'] > it['val']]
        bq, bi = b[-1] if b else (-1, None)
        aq, ai = a[0] if a else (len(pr), None)
        where = f"By its value it sits between: {bi['rel'] if bi else '(start)'}  and  {ai['rel'] if ai else '(end)'}"
        slots = [pr[q]['rel'] for q in range(bq + 1, aq) if not pr[q][k]]
        if slots:
            say('WARN', f"{head} - probably belongs in a Prise that has no {lab}:", [f"  -> {s}" for s in slots] + [where])
        elif bq == aq:
            say('WARN', f"{head} - falls between two {lab}s of the SAME Prise ({pr[bq]['rel']}): extra take? insert?", [where])
        else:
            say('WARN', f"{head} - every Prise around already has its {lab}: probably an INSERT (or extra take) there", [where])


# ---------------- spare pairs ----------------
def spare(r): return max(0, r['pairs'] - 1 - r['front'] - r['back'])


def take(r, side):
    if side == 'back': i = -1 - r['back']; r['back'] += 1
    else: i = r['front']; r['front'] += 1
    return [r['A'][i]['rel'], r['V'][i]['rel']]


# ---------------- one Plan ----------------
def audit_plan(plan, pool, allA, allV, cross):
    stats['Plans'] += 1
    section(rel(plan))
    if not re.match(r'^plan_\d+$', plan.name, re.I):
        say('WARN', f"Unexpected folder name in Parent: {rel(plan)}")

    loose = []
    for f in sorted(plan.iterdir()):
        if not f.is_file() or f.name.lower() in IGNORE_FILES: continue
        if f.suffix.lower() in AUDIO | VIDEO: loose.append(mk(f))
        else: say('WARN', f"Unexpected file in Plan: {rel(f)}")

    dirs = sorted((d for d in plan.iterdir() if d.is_dir()), key=skey)
    ins = [d for d in dirs if 'insert' in d.name.lower()]
    prs = [d for d in dirs if d not in ins]

    nums = [num(d.name) for d in prs if num(d.name) < 10**9]
    for k in range(1, (max(nums) if nums else 0) + 1):
        if k not in nums: say('WARN', f"Missing Prise folder: {rel(plan)}\\Prise_{k} (gap in numbering)")

    pr = []
    for d in prs:
        stats['Prises'] += 1
        A, V, O, S = load(d)
        stats['WAV'] += len(A); stats['Video'] += len(V)
        pr.append(dict(rel=rel(d), A=A, V=V, O=O, S=S, pairs=min(len(A), len(V)),
                       empty=not (A or V), front=0, back=0, claim=None))
    for d in ins:
        A, V, O, S = load(d)
        stats['WAV'] += len(A); stats['Video'] += len(V)
        say('INFO', f"Insert folder (not audited, ignored for chronology): {rel(d)} ({len(A)} WAV, {len(V)} video)")

    # pass 1a: empty Prise takes a spare pair from the PREVIOUS filled Prise (reverse order)
    for r in range(len(pr) - 1, -1, -1):
        if not pr[r]['empty'] or pr[r]['claim']: continue
        d = next((pr[q] for q in range(r - 1, -1, -1) if not pr[q]['empty']), None)
        if d and spare(d) > 0: pr[r]['claim'] = (d, 'previous', 'last', take(d, 'back'))
    # pass 1b: still empty -> NEXT filled Prise (forward order)
    for r in range(len(pr)):
        if not pr[r]['empty'] or pr[r]['claim']: continue
        d = next((pr[q] for q in range(r + 1, len(pr)) if not pr[q]['empty']), None)
        if d and spare(d) > 0: pr[r]['claim'] = (d, 'next', 'first', take(d, 'front'))

    # pass 2: report
    for r, rec in enumerate(pr):
        a, v = len(rec['A']), len(rec['V'])
        paths = [i['rel'] for i in rec['A'] + rec['V']]
        if rec['empty']:
            if rec['claim']:
                d, side, which, ps = rec['claim']
                say('WARN', f"EMPTY: {rec['rel']}  <-- {d['rel']} ({side} Prise) holds {d['pairs']} pairs, its {which} pair probably belongs here. Move:", ps)
            elif find(pr, r, ['A', 'V'], loose, pool, quiet=True) == 0:
                say('ERROR', f"WTF it's empty bro: {rec['rel']}  (no spare pair nearby, nothing fitting in loose files or {POOL})")
        elif a == 0:
            say('ERROR', f"VIDEO WITHOUT WAV: {rec['rel']} ({v} video, 0 WAV)", paths); find(pr, r, ['A'], loose, pool)
        elif v == 0:
            say('ERROR', f"WAV WITHOUT VIDEO: {rec['rel']} ({a} WAV, 0 video)", paths); find(pr, r, ['V'], loose, pool)
        else:
            if a > v: say('WARN', f"EXTRA WAV: {rec['rel']} ({a} WAV for {v} video) - {a - v} WAV should probably be deleted", paths)
            elif v > a: say('WARN', f"EXTRA VIDEO: {rec['rel']} ({v} video for {a} WAV) - {v - a} video should probably be deleted", paths)
            if rec['pairs'] >= 2 and spare(rec) > 0:
                say('WARN', f"EXTRA PAIR: {rec['rel']} holds {rec['pairs']} pairs, {spare(rec)} too many, no empty Prise nearby to take them. A pair doesn't belong here:", paths)
        if rec['O']: say('INFO', f"Unexpected file type(s) in {rec['rel']}", rec['O'])
        if rec['S']: say('INFO', f"Unexpected subfolder(s) in {rec['rel']}", rec['S'])

    place_loose(pr, loose)

    pa = [i for r in pr for i in r['A']]; pv = [i for r in pr for i in r['V']]
    allA += pa; allV += pv
    if not cross:
        check_seq(pa, 'TOO EARLY', 'TOO LATE', 'time')
        check_video_seq(pv, rel(plan))


# ---------------- main ----------------
def main():
    global ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?'); ap.add_argument('--cross', action='store_true')
    args = ap.parse_args()
    ROOT = Path(args.root or Path(__file__).resolve().parent).resolve()
    print(f"Auditing: {ROOT}\nIgnored folders: {', '.join(sorted(IGNORE_DIRS))}")
    print("Chronology: across ALL plans" if args.cross else "Chronology: inside each Plan (--cross for global)")

    pool = []
    pd = next((d for d in ROOT.iterdir() if d.is_dir() and d.name.lower() == POOL), None)
    if pd:
        pool = [mk(f, warn=False) for f in pd.rglob('*')
                if f.is_file() and f.suffix.lower() in AUDIO | VIDEO and f.name.lower() not in IGNORE_FILES]
        print(f"{POOL} loaded: {sum(i['kind'] == 'A' for i in pool)} WAV, {sum(i['kind'] == 'V' for i in pool)} video")
    else:
        print(f"No '{POOL}' folder found: missing files won't be searched there")

    for f in sorted(ROOT.iterdir()):
        if f.is_file() and f.suffix.lower() != '.py' and f.name != 'audit_report.txt' and f.name.lower() not in IGNORE_FILES:
            say('WARN', f"Loose file in Parent (not in a Plan): {rel(f)}")

    plans = sorted((d for d in ROOT.iterdir() if d.is_dir() and d.name.lower() not in IGNORE_DIRS), key=skey)
    pn = [num(d.name) for d in plans if num(d.name) < 10**9]
    for k in range(1, (max(pn) if pn else 0) + 1):
        if k not in pn: say('WARN', f"Missing Plan folder: Plan_{k} (gap in numbering)")

    allA, allV = [], []
    for p in plans: audit_plan(p, pool, allA, allV, args.cross)

    if args.cross:
        section("Chronology across all plans")
        check_seq(allA, 'TOO EARLY', 'TOO LATE', 'time')
        check_video_seq(allV, 'ALL plans')

    section("SUMMARY")
    s1 = " | ".join(f"{k}: {v}" for k, v in stats.items())
    s2 = " | ".join(f"{k}S: {v}" for k, v in counts.items())
    print(s1); report.append(s1)
    print(COL['ERROR' if counts['ERROR'] else 'WARN' if counts['WARN'] else 'INFO'] + s2 + "\033[0m"); report.append(s2)
    out = Path(__file__).resolve().parent / 'audit_report.txt'
    out.write_text("\n".join(report), encoding='utf-8')
    print(f"\033[90mReport saved to: {out}\033[0m")


if __name__ == '__main__':
    if sys.platform == 'win32': os.system('')      # enables ANSI colours in the Windows console
    try: main()
    except Exception: print("\033[91mSCRIPT ERROR\033[0m"); traceback.print_exc()
    input("\nPress Enter to close")