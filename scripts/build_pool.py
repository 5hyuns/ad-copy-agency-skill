# 역할 사이에 파일을 넘긴다. 팀 이름을 가리고 섞어서 CD에게, CD 판정을 팀별로 나눠 팀에게, CD 후보를 광고주에게.
# 사용: python build_pool.py <round1|feedback|round2|candidates> <실행 폴더>
#       python build_pool.py known <실행 폴더> <팀>   (앞 팀들의 루트 평문 → 05-known-<팀>.md)
import re, sys, random, pathlib
from runfiles import TEAMS, read, write, section, table, load_json, save_json, md_row

sys.stdout.reconfigure(encoding="utf-8")
cmd, run = sys.argv[1], pathlib.Path(sys.argv[2])
rnd = random.Random(f"{run.name}-{cmd}")


def team_round1(t):
    text = read(run / f"05-team-{t}.md")
    routes = {r[0]: r[1] for r in table(section(text, "루트")) if len(r) >= 2}
    lines = [(r[0], r[1], r[2]) for r in table(section(text, "줄")) if len(r) >= 3 and r[2]]
    return routes, lines


def round1():
    routes, lines = [], []
    for t in TEAMS:
        rs, ls = team_round1(t)
        routes += [(t, k, v) for k, v in rs.items()]
        lines += [(t, no, route, h) for no, route, h in ls]
    rnd.shuffle(routes)
    rid = {(t, k): f"R{i:02d}" for i, (t, k, _) in enumerate(routes, 1)}
    key = {"routes": {rid[(t, k)]: {"team": t, "route": k, "plain": v} for t, k, v in routes}, "lines": {}}
    out = ["# CD 1차 리뷰용 — 팀 이름을 가렸다", "", "## 루트", "", md_row("루트", "평문 한 줄"), "|---|---|"]
    out += [md_row(rid[(t, k)], v) for t, k, v in routes]
    out += ["", "## 줄", "", md_row("줄", "루트", "헤드라인"), "|---|---|---|"]
    n = 0
    missing_route = []
    for t, k, _ in routes:
        group = [x for x in lines if x[0] == t and x[2] == k]
        for _, no, route, h in group:
            n += 1
            lid = f"L{n:03d}"
            key["lines"][lid] = {"team": t, "no": no, "route": route, "rid": rid[(t, k)], "text": h}
            out.append(md_row(lid, rid[(t, k)], h))
    for t, no, route, h in lines:
        if (t, route) not in rid:
            missing_route.append(f"{t} {no} ({route})")
    write(run / "06-pool-1.md", "\n".join(out) + "\n")
    save_json(run / "06-pool-key.json", key)
    print(f"루트 {len(routes)}개, 줄 {n}개" + (f" / 루트 표에 없는 루트를 단 줄: {', '.join(missing_route)}" if missing_route else ""))


def cd1():
    key = load_json(run / "06-pool-key.json")
    text = read(run / "06-cd-review-1.md")
    kept_routes = {r[0]: (r[1], r[2] if len(r) > 2 else "") for r in table(section(text, "살린 루트")) if r and r[0] in key["routes"]}
    verdict = {r[0]: (r[1], r[2] if len(r) > 2 else "") for r in table(section(text, "줄 판정")) if r and r[0] in key["lines"]}
    # 살린 루트 밖의 줄을 CD가 '살림'으로 둔 경우(루트 상한을 줄 때 나왔다) 죽임으로 본다.
    for l, (v, why) in list(verdict.items()):
        if v == "살림" and key["lines"][l]["rid"] not in kept_routes:
            verdict[l] = ("죽임", "루트가 살아남지 않음")
    return key, kept_routes, verdict


def local_ids(text, key, t):
    """CD가 쓴 가림 번호(L001, R01)를 팀이 아는 번호로 바꾼다. 다른 팀의 것은 가린 채로 둔다."""
    def line(m):
        v = key["lines"].get(m.group(0))
        return m.group(0) if not v else (v["no"] if v["team"] == t else "다른 팀의 줄")

    def route(m):
        v = key["routes"].get(m.group(0))
        return m.group(0) if not v else (v["route"] if v["team"] == t else "다른 팀의 루트")
    return re.sub(r"(?<![A-Za-z0-9])R\d{2}(?!\d)", route, re.sub(r"(?<![A-Za-z0-9])L\d{3}(?!\d)", line, text))


def feedback():
    key, kept_routes, verdict = cd1()
    missing = [l for l in key["lines"] if l not in verdict]
    for t in TEAMS:
        kept_routes_t = {r: (local_ids(a, key, t), local_ids(b, key, t)) for r, (a, b) in kept_routes.items()}
        verdict_t = {l: (a, local_ids(b, key, t)) for l, (a, b) in verdict.items()}
        out = [f"# 팀 {t}에게 — CD 1차 리뷰 결과", "", "## 살아남은 루트와 CD 피드백", "",
               md_row("루트", "평문 한 줄", "CD 피드백"), "|---|---|---|"]
        mine = [(r, v) for r, v in key["routes"].items() if v["team"] == t]
        alive = [(r, v) for r, v in mine if r in kept_routes]
        out += [md_row(v["route"], v["plain"], kept_routes_t[r][1]) for r, v in alive] or ["| (없음) | | |"]
        out += ["", "## 살아남은 줄", "", md_row("번호", "루트", "헤드라인"), "|---|---|---|"]
        out += [md_row(v["no"], v["route"], v["text"]) for l, v in key["lines"].items() if v["team"] == t and verdict.get(l, ("",))[0] == "살림"] or ["| (없음) | | |"]
        out += ["", "## 죽은 줄과 CD의 이유", "", md_row("번호", "루트", "헤드라인", "이유"), "|---|---|---|---|"]
        out += [md_row(v["no"], v["route"], v["text"], verdict_t[l][1]) for l, v in key["lines"].items() if v["team"] == t and verdict.get(l, ("",))[0] == "죽임"] or ["| (없음) | | | |"]
        write(run / f"07-feedback-{t}.md", "\n".join(out) + "\n")
    alive_n = sum(1 for v in verdict.values() if v[0] == "살림")
    print(f"살린 루트 {len(kept_routes)}개, 살린 줄 {alive_n}개, 판정 빠진 줄 {len(missing)}개" + (f": {', '.join(missing)}" if missing else ""))


def round2():
    key, kept_routes, verdict = cd1()
    rid = {(v["team"], v["route"]): r for r, v in key["routes"].items()}
    items = []
    for l, v in key["lines"].items():
        if verdict.get(l, ("",))[0] == "살림":
            items.append({"src": "1차 생존", "team": v["team"], "no": v["no"], "route": v["route"], "rid": v["rid"], "text": v["text"], "defense": ""})
    notes = []
    for t in TEAMS:
        p = run / f"07-team-{t}.md"
        if not p.exists():
            notes.append(f"{p.name} 없음")
            continue
        text = read(p)
        for r in table(section(text, "다시 쓴 줄")):
            if len(r) < 3 or not r[2]:
                continue
            r_id = rid.get((t, r[1]))
            if r_id not in kept_routes:
                notes.append(f"{t} {r[0]}: 살아남지 않은 루트 {r[1]}")
            items.append({"src": "2차 재작업", "team": t, "no": r[0], "route": r[1], "rid": r_id or "?", "text": r[2], "defense": ""})
        defended = [r for r in table(section(text, "변론")) if len(r) >= 3 and r[0] and r[0] != "(없음)"]
        if len(defended) > 1:
            notes.append(f"팀 {t} 변론 {len(defended)}건 — 첫 건만 받는다")
        for r in defended[:1]:
            hit = [(l, v) for l, v in key["lines"].items() if v["team"] == t and v["no"] == r[0]]
            if not hit or verdict.get(hit[0][0], ("",))[0] != "죽임":
                notes.append(f"팀 {t} 변론 {r[0]}: 1차에서 죽은 줄이 아님 — 받지 않음")
                continue
            v = hit[0][1]
            items.append({"src": "변론", "team": t, "no": v["no"], "route": v["route"], "rid": v["rid"], "text": v["text"], "defense": r[2]})
    # 사용 승인을 받은 고객의 말은 팀이 원문 그대로 쓰지 않는다. 오케스트레이터가 08-quotes.md에 옮긴 원문을 R00 줄로 더한다.
    quotes = [r for r in table(section(read(run / "08-quotes.md"), "고객의 말")) if len(r) >= 2 and r[0]] if (run / "08-quotes.md").exists() else []
    for q in quotes:
        items.append({"src": "원자료 원문", "team": "원자료", "no": "-", "route": "R00", "rid": "R00", "text": q[0], "defense": "", "source": q[1]})
    rnd.shuffle(items)
    pkey = {}
    out = ["# CD 2차 리뷰용 — 팀과 판(1차/2차)을 가렸다", "", "## 루트", "", md_row("루트", "평문 한 줄"), "|---|---|"]
    if quotes:
        out.append(md_row("R00", "원자료 원문: 사용 승인을 받은 고객의 말을 고치지 않고 옮긴 줄"))
    out += [md_row(r, key["routes"][r]["plain"]) for r in sorted({i["rid"] for i in items if i["rid"] in key["routes"]})]
    out += ["", "## 줄", "", md_row("줄", "루트", "헤드라인", "변론"), "|---|---|---|---|"]
    for i, it in enumerate(items, 1):
        mid = f"M{i:03d}"
        pkey[mid] = it
        out.append(md_row(mid, it["rid"], it["text"], it["defense"]))
    write(run / "08-pool-2.md", "\n".join(out) + "\n")
    save_json(run / "08-pool-key.json", pkey)
    c = {s: sum(1 for x in items if x["src"] == s) for s in ["1차 생존", "2차 재작업", "변론", "원자료 원문"]}
    print(f"줄 {len(items)}개 {c}" + (" / " + "; ".join(notes) if notes else ""))


def candidates():
    pkey = load_json(run / "08-pool-key.json")
    text = read(run / "08-cd-review-2.md")
    rows = [r for r in table(section(text, "후보")) if len(r) >= 4 and r[1] in pkey]
    notes = [f"{r[1]} 헤드라인이 풀과 다름" for r in rows if r[2] != pkey[r[1]]["text"]]
    out = ["# CD가 고른 후보", "", md_row("줄", "헤드라인", "CD 설명: 받는 사람에게 주는 것"), "|---|---|---|"]
    # 원문 줄은 광고주가 승인된 후기인지 확인할 수 있게 출처를 붙인다
    out += [md_row(r[1], pkey[r[1]]["text"], r[3] + (f" [사용 승인을 받은 고객의 말, 출처: {pkey[r[1]]['source']}]" if pkey[r[1]].get("source") else "")) for r in rows]
    write(run / "09-candidates.md", "\n".join(out) + "\n")
    print(f"후보 {len(rows)}개" + (" / " + "; ".join(notes) if notes else ""))


def known():
    """5단계를 차례로 돌 때, 앞 팀들이 연 루트의 평문만 다음 팀에게 넘긴다. 줄은 넘기지 않는다."""
    t = sys.argv[3]
    before = TEAMS[:TEAMS.index(t)]
    items = [v for b in before for v in team_round1(b)[0].values()]
    body = "\n".join(f"- {v}" for v in items)
    write(run / f"05-known-{t}.md", body + "\n")
    print(f"팀 {t}에게 넘길 이미 나온 길 {len(items)}개 (앞 팀: {', '.join(before)})")
    print(body)


{"round1": round1, "feedback": feedback, "round2": round2, "candidates": candidates, "known": known}[cmd]()
