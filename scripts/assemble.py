# 마지막 단계. 최종 줄이 거쳐 온 길을 모으고(10-final.md), 단계가 업계 흐름대로 돌았는지 점검한다(10-process-check.md).
# 과정 점검은 산출물에 필요한 항목이 있는지만 본다. 그 단계가 잘 됐는지는 보지 않는다.
# 사용: python assemble.py <실행 폴더>
import re, sys, pathlib, statistics
from runfiles import TEAMS, read, write, section, table, load_json, md_row

sys.stdout.reconfigure(encoding="utf-8")
run = pathlib.Path(sys.argv[1])


def exists(name):
    return (run / name).exists()


def txt(name):
    return read(run / name) if exists(name) else ""


checks = []


def check(stage, basis, what, ok, note=""):
    checks.append((stage, basis, what, "통과" if ok else "어긋남", note))


# 1. OT
cb = txt("01-client-brief.md")
for field in ["주제", "사업 목표", "타깃", "모드", "채널", "브랜드명"]:
    check("1 OT", "T&W 3단계 클라이언트 브리프", f"'{field}' 항목", field in cb)

# 2. 원자료
raw = txt("02-raw.md")
for g, name in [("F", "제품 사실"), ("V", "사람의 말"), ("C", "광고 문구")]:
    n = len(re.findall(rf"(?m)^- {g}\d+", raw))
    check("2 재료", "T&W 4단계 디브리프·데스크 리서치", f"{name} 원문", n > 0, f"{n}개")

# 3. 크리에이티브 브리프
br = txt("03-creative-brief.md")
for h in ["받은 과제", "다시 정의한 과제", "누구에게", "바라는 반응", "단일 제안", "믿을 이유", "경쟁이 이미 하는 말", "톤", "필수 사항", "택하지 않은 재정의"]:
    check("3 플래너", "IPA 브리프 가이드, King T-Plan", f"'{h}' 절", section(br, h) is not None)
redef = section(br, "다시 정의한 과제") or ""
method = re.search(r"쓴 방법:\s*(.+)", redef)
check("3 플래너", "사례 25편 중 16편의 과제 재정의", "재정의 방법이 세 가지 중 하나", bool(method and re.search(r"말 상대|문제 종류|빈자리", method.group(1))), method.group(1).strip() if method else "")
scene = re.search(r"근거가 된 한 장면·한마디:\s*(.+)", redef)
check("3 플래너", "사례: 재정의의 재료는 한 장면·한마디", "근거가 원자료 번호를 가리킴", bool(scene and re.search(r"\b[FVCXN]\d+", scene.group(1))))

# 4. 서저리
sg = txt("04-surgery.md")
v = (section(sg, "판정") or "").strip()
check("4 서저리", "T&W 9단계 크리에이티브 서저리", "판정이 있음", v.startswith("통과") or v.startswith("돌려보냄"), v.splitlines()[0] if v else "")
if v.startswith("돌려보냄"):
    check("4 서저리", "T&W 9단계", "플래너가 고친 것을 적음", section(br, "고친 것") is not None)

# 5. 팀
total1, line_lens1 = 0, []
for t in TEAMS:
    tt = txt(f"05-team-{t}.md")
    routes = table(section(tt, "루트"))
    lines = [r for r in table(section(tt, "줄")) if len(r) >= 3 and r[2]]
    total1 += len(lines)
    line_lens1 += [len(r[2]) for r in lines]
    check("5 팀", "T&W: 같은 브리프를 받는 팀은 대개 3팀 이하 / Sullivan: 서로 다른 문", f"팀 {t} 루트 3개 이상", len(routes) >= 3, f"루트 {len(routes)}, 줄 {len(lines)}")
check("5 팀", "Sullivan 'write 100'", "1차 줄 합계 90~115", 90 <= total1 <= 115, f"{total1}줄")
for t in TEAMS[1:]:
    check("5 팀", "CD가 다음 팀에 이미 나온 길을 알림 (스킬 시험: skill-tests/2026-10-02-divergence*)", f"팀 {t}가 앞 팀의 루트를 받음", exists(f"05-known-{t}.md"))

# 6. CD 1차
c1 = txt("06-cd-review-1.md")
key = load_json(run / "06-pool-key.json") if exists("06-pool-key.json") else {"lines": {}, "routes": {}}
pos = {h: c1.find(f"## {h}") for h in ["기준", "줄 판정"]}
check("6 CD 1차", "橋口幸生: 기준을 먼저 세운다", "기준이 판정보다 앞", 0 <= pos["기준"] < pos["줄 판정"])
ver1 = {r[0]: r for r in table(section(c1, "줄 판정")) if r and r[0] in key["lines"]}
check("6 CD 1차", "T&W 13단계 CD 리뷰", "모든 줄을 판정", len(ver1) == len(key["lines"]) > 0, f"{len(ver1)}/{len(key['lines'])}")
killed = [r for r in ver1.values() if len(r) > 1 and r[1] == "죽임"]
check("6 CD 1차", "Dave Dye: 기각 이유를 짧게 남김", "죽인 줄마다 이유", all(len(r) > 2 and r[2] for r in killed), f"죽임 {len(killed)}")
kept_routes = [r for r in table(section(c1, "살린 루트")) if r and r[0] in key["routes"]]
check("6 CD 1차", "T&W 14단계 WIP: 발전시킬 루트 합의", "살린 루트마다 피드백", bool(kept_routes) and all(len(r) > 2 and r[2] for r in kept_routes), f"루트 {len(kept_routes)}")
check("6 CD 1차", "宣伝会議賞 講評: 같은 관점을 묶어 거름", "관점 묶음 절", section(c1, "관점 묶음") is not None)
check("6 CD 1차", "설계안 6단계: 살릴 루트 3~5개", "살린 루트 3~5개", 3 <= len(kept_routes) <= 5, f"루트 {len(kept_routes)}")

# 7. 재작업
for t in TEAMS:
    check("7 재작업", "T&W 17단계 수정·재제시", f"팀 {t} 재작업 파일", exists(f"07-team-{t}.md"))

# 8. CD 2차
c2 = txt("08-cd-review-2.md")
pkey = load_json(run / "08-pool-key.json") if exists("08-pool-key.json") else {}
pos2 = {h: c2.find(f"## {h}") for h in ["기준", "줄 판정"]}
check("8 CD 2차", "橋口幸生", "기준이 판정보다 앞", 0 <= pos2["기준"] < pos2["줄 판정"])
ver2 = {r[0]: r for r in table(section(c2, "줄 판정")) if r and r[0] in pkey}
check("8 CD 2차", "T&W 13단계(여러 라운드)", "모든 줄을 판정", len(ver2) == len(pkey) > 0, f"{len(ver2)}/{len(pkey)}")
defended = [m for m, it in pkey.items() if it["src"] == "변론"]
dver = {r[0]: r for r in table(section(c2, "변론 판정")) if r and r[0] in pkey}
check("8 CD 2차", "사례: 반대에 맞서 아이디어를 지킨 사람", "변론마다 판정", all(m in dver for m in defended), f"변론 {len(defended)}건")
cands = [r for r in table(section(c2, "후보")) if len(r) >= 4 and r[1] in pkey]
check("8 CD 2차", "AC재팬 40→10→3, Dye 15:1", "후보 3~7줄", 3 <= len(cands) <= 7, f"{len(cands)}줄")
check("8 CD 2차", "—", "후보가 '남김' 판정 안에 있음", all(ver2.get(r[1], ["", ""])[1] == "남김" for r in cands))

# 9. 광고주
cl = txt("09-client-review.md")
picks = [r for r in table(section(cl, "선택")) if len(r) >= 3]
cand_ids = {r[1] for r in cands}
check("9 광고주", "사례: 최종 선택에 광고주가 들어감", "최종 1줄", sum(1 for r in picks if r[0] == "최종") == 1)
check("9 광고주", "—", "고른 줄이 CD 후보 안에 있음", all(r[1] in cand_ids for r in picks if r[1] in pkey))
check("9 광고주", "regulation.md", "사실·규제 검수 절", section(cl, "사실·규제 검수") is not None)

# 최종 파일
ver1_by_rid = {}
for r in kept_routes:
    ver1_by_rid[r[0]] = r[2]
rid_of = {(v["team"], v["route"]): r for r, v in key["routes"].items()}
out = ["# 최종 — " + (re.search(r"주제[^:：]*[:：]\s*(.+)", cb).group(1).strip() if re.search(r"주제[^:：]*[:：]\s*(.+)", cb) else run.name), ""]
out += [md_row("순서", "헤드라인", "팀·루트", "거쳐 온 길", "광고주가 고른 이유"), "|---|---|---|---|---|"]
cd2_reason = {r[1]: r[3] for r in cands}
for r in picks:
    it = pkey.get(r[1])
    if not it:
        out.append(md_row(r[0], r[2], "?", "풀에 없는 줄", r[3] if len(r) > 3 else ""))
        continue
    path = f"{it['src']}" + (f" (변론: {dver[r[1]][1]})" if r[1] in dver else "")
    path += f" → CD 1차 루트 피드백: {ver1_by_rid.get(it['rid'], '-')} → CD 2차: {cd2_reason.get(r[1], '-')}"
    plain = key["routes"].get(it["rid"], {}).get("plain", "")
    out.append(md_row(r[0], it["text"], f"팀 {it['team']} {it['route']}: {plain}", path, r[3] if len(r) > 3 else ""))


def mean(xs):
    return f"{statistics.mean(xs):.1f}" if xs else "-"


pool2_lens = [len(it["text"]) for it in pkey.values()]
cand_lens = [len(pkey[r[1]]["text"]) for r in cands]
pick_lens = [len(pkey[r[1]]["text"]) for r in picks if r[1] in pkey]
alive1 = sum(1 for r in ver1.values() if len(r) > 1 and r[1] == "살림")
rework = sum(1 for it in pkey.values() if it["src"] == "2차 재작업")
accepted = sum(1 for m in defended if dver.get(m, ["", ""])[1] == "받아들임")
out += ["", "## 단계별 수", "",
        f"- 1차 줄 {total1} → CD 1차 살림 {alive1} (루트 {len(kept_routes)}) → 재작업 {rework}줄, 변론 {len(defended)}건(받아들임 {accepted}) → 2차 풀 {len(pkey)} → CD 후보 {len(cands)} → 광고주 선택 {len(picks)}",
        "", "## 길이 (CD의 길이 편향을 보는 기록. 판정에는 쓰지 않는다)", "",
        f"- 평균 글자 수: 1차 전체 {mean(line_lens1)} / 2차 풀 {mean(pool2_lens)} / CD 후보 {mean(cand_lens)} / 광고주 선택 {mean(pick_lens)}", ""]
write(run / "10-final.md", "\n".join(out) + "\n")

bad = [c for c in checks if c[3] == "어긋남"]
pc = ["# 과정 점검", "", "> 단계마다 업계 흐름의 산출물이 있는지 본다. 그 단계가 잘 됐는지는 보지 않는다.", "",
      f"- 점검 {len(checks)}개, 어긋남 {len(bad)}개", "", md_row("단계", "업계 근거", "점검", "결과", "메모"), "|---|---|---|---|---|"]
pc += [md_row(*c) for c in checks]
write(run / "10-process-check.md", "\n".join(pc) + "\n")
print(f"10-final.md, 10-process-check.md — 점검 {len(checks)}개 중 어긋남 {len(bad)}개")
for c in bad:
    print("  어긋남:", c[0], c[2], c[4])
