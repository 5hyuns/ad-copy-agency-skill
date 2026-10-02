# 마지막 단계. 최종 줄이 거쳐 온 길을 모으고(10-final.md), 단계가 업계 흐름대로 돌았는지 점검한다(10-process-check.md).
# 과정 점검은 산출물에 필요한 항목이 있는지만 본다. 그 단계가 잘 됐는지는 보지 않는다.
# 사용: python assemble.py <실행 폴더>
import re, sys, pathlib, statistics
from runfiles import TEAMS, read, write, section, section_pos, table, load_json, md_row, lang, canon

sys.stdout.reconfigure(encoding="utf-8")
run = pathlib.Path(sys.argv[1])
LANG = lang(run)


def M(ko, en):
    """사용자가 읽는 문구. 실행의 카피 언어를 따른다."""
    return en if LANG == "en" else ko


def exists(name):
    return (run / name).exists()


def txt(name):
    return read(run / name) if exists(name) else ""


checks = []


def check(stage, basis, what, ok, note=""):
    checks.append((stage, basis, what, M("통과", "pass") if ok else M("어긋남", "MISSING"), note))


# 1. OT (양식의 항목 이름은 두 언어 모두 한국어 정본을 앞에 둔다)
cb = txt("01-client-brief.md")
for field, field_en in [("주제", "Subject"), ("사업 목표", "Business goal"), ("타깃", "Target"), ("모드", "Mode"), ("채널", "Channel"), ("브랜드명", "Brand")]:
    check("1 OT", M("T&W 3단계 클라이언트 브리프", "T&W step 3 client brief"), M(f"'{field}' 항목", f"'{field_en}' field"), field in cb or field_en in cb)

# 2. 원자료
raw = txt("02-raw.md")
for g, name, name_en in [("F", "제품 사실", "Product facts"), ("V", "사람의 말", "What people said"), ("C", "광고 문구", "Ad copy")]:
    n = len(re.findall(rf"(?m)^- {g}\d+", raw))
    check(M("2 재료", "2 Material"), M("T&W 4단계 디브리프·데스크 리서치", "T&W step 4 debrief, desk research"), M(f"{name} 원문", f"{name_en}, verbatim"), n > 0, M(f"{n}개", f"{n}"))

# 3. 크리에이티브 브리프
br = txt("03-creative-brief.md")
for h in ["받은 과제", "다시 정의한 과제", "누구에게", "바라는 반응", "단일 제안", "믿을 이유", "경쟁이 이미 하는 말", "톤", "필수 사항", "택하지 않은 재정의"]:
    check(M("3 플래너", "3 Planner"), M("IPA 브리프 가이드, King T-Plan", "IPA brief guide, King T-Plan"), M(f"'{h}' 절", f"'{h}' section"), section(br, h) is not None)
redef = section(br, "다시 정의한 과제") or ""
method = re.search(r"(?:쓴 방법|Method):\s*(.+)", redef)
check(M("3 플래너", "3 Planner"), M("사례 25편 중 16편의 과제 재정의", "16 of 25 cases reframed the task"), M("재정의 방법이 세 가지 중 하나", "Reframe uses one of the three methods"),
      bool(method and re.search(r"(?i)말 상대|문제 종류|빈자리|audience|problem type|gap", method.group(1))), method.group(1).strip() if method else "")
scene = re.search(r"(?:근거가 된 한 장면·한마디|Evidence scene or quote):\s*(.+)", redef)
check(M("3 플래너", "3 Planner"), M("사례: 재정의의 재료는 한 장면·한마디", "Cases: a reframe rests on one scene or remark"), M("근거가 원자료 번호를 가리킴", "Evidence points to a raw material number"), bool(scene and re.search(r"\b[FVCXN]\d+", scene.group(1))))

# 4. 서저리
sg = txt("04-surgery.md")
v = (section(sg, "판정") or "").strip()
first = canon(re.split(r"[\s.,:]", v, 1)[0]) if v else ""
check(M("4 서저리", "4 Surgery"), M("T&W 9단계 크리에이티브 서저리", "T&W step 9 creative surgery"), M("판정이 있음", "Has a verdict"), first in ("통과", "돌려보냄"), v.splitlines()[0] if v else "")
if first == "돌려보냄":
    check(M("4 서저리", "4 Surgery"), M("T&W 9단계", "T&W step 9"), M("플래너가 고친 것을 적음", "Planner recorded the changes"), section(br, "고친 것") is not None)

# 5. 팀
total1, line_lens1 = 0, []
for t in TEAMS:
    tt = txt(f"05-team-{t}.md")
    routes = table(section(tt, "루트"))
    lines = [r for r in table(section(tt, "줄")) if len(r) >= 3 and r[2]]
    total1 += len(lines)
    line_lens1 += [len(r[2]) for r in lines]
    check(M("5 팀", "5 Teams"), M("T&W: 같은 브리프를 받는 팀은 대개 3팀 이하 / Sullivan: 서로 다른 문", "T&W: usually 3 teams or fewer per brief / Sullivan: different doors"),
          M(f"팀 {t} 루트 3개 이상", f"Team {t} has 3+ routes"), len(routes) >= 3, M(f"루트 {len(routes)}, 줄 {len(lines)}", f"routes {len(routes)}, lines {len(lines)}"))
check(M("5 팀", "5 Teams"), "Sullivan 'write 100'", M("1차 줄 합계 90~115", "Round 1 total 90-115 lines"), 90 <= total1 <= 115, M(f"{total1}줄", f"{total1} lines"))
for t in TEAMS[1:]:
    check(M("5 팀", "5 Teams"), M("CD가 다음 팀에 이미 나온 길을 알림 (스킬 시험: skill-tests/2026-10-02-divergence*)", "CD tells the next team which routes are taken (skill test: skill-tests/2026-10-02-divergence*)"),
          M(f"팀 {t}가 앞 팀의 루트를 받음", f"Team {t} received earlier routes"), exists(f"05-known-{t}.md"))

# 6. CD 1차
c1 = txt("06-cd-review-1.md")
key = load_json(run / "06-pool-key.json") if exists("06-pool-key.json") else {"lines": {}, "routes": {}}
pos = {h: section_pos(c1, h) for h in ["기준", "줄 판정"]}
check(M("6 CD 1차", "6 CD round 1"), M("橋口幸生: 기준을 먼저 세운다", "Hashiguchi Yukio: set criteria first"), M("기준이 판정보다 앞", "Criteria come before verdicts"), 0 <= pos["기준"] < pos["줄 판정"])
ver1 = {r[0]: r for r in table(section(c1, "줄 판정")) if r and r[0] in key["lines"]}
check(M("6 CD 1차", "6 CD round 1"), M("T&W 13단계 CD 리뷰", "T&W step 13 CD review"), M("모든 줄을 판정", "Every line judged"), len(ver1) == len(key["lines"]) > 0, f"{len(ver1)}/{len(key['lines'])}")
killed = [r for r in ver1.values() if len(r) > 1 and r[1] == "죽임"]
check(M("6 CD 1차", "6 CD round 1"), M("Dave Dye: 기각 이유를 짧게 남김", "Dave Dye: short kill reasons"), M("죽인 줄마다 이유", "Every kill has a reason"), all(len(r) > 2 and r[2] for r in killed), M(f"죽임 {len(killed)}", f"killed {len(killed)}"))
kept_routes = [r for r in table(section(c1, "살린 루트")) if r and r[0] in key["routes"]]
check(M("6 CD 1차", "6 CD round 1"), M("T&W 14단계 WIP: 발전시킬 루트 합의", "T&W step 14 WIP: agree routes to develop"), M("살린 루트마다 피드백", "Feedback for every kept route"),
      bool(kept_routes) and all(len(r) > 2 and r[2] for r in kept_routes), M(f"루트 {len(kept_routes)}", f"routes {len(kept_routes)}"))
check(M("6 CD 1차", "6 CD round 1"), M("宣伝会議賞 講評: 같은 관점을 묶어 거름", "Sendenkaigi Award reviews: group same viewpoints"), M("관점 묶음 절", "Viewpoint groups section"), section(c1, "관점 묶음") is not None)
check(M("6 CD 1차", "6 CD round 1"), M("설계안 6단계: 살릴 루트 3~5개", "Design step 6: keep 3-5 routes"), M("살린 루트 3~5개", "3-5 routes kept"), 3 <= len(kept_routes) <= 5, M(f"루트 {len(kept_routes)}", f"routes {len(kept_routes)}"))

# 7. 재작업
for t in TEAMS:
    check(M("7 재작업", "7 Rework"), M("T&W 17단계 수정·재제시", "T&W step 17 revise and re-present"), M(f"팀 {t} 재작업 파일", f"Team {t} rework file"), exists(f"07-team-{t}.md"))

# 8. CD 2차
c2 = txt("08-cd-review-2.md")
pkey = load_json(run / "08-pool-key.json") if exists("08-pool-key.json") else {}
pos2 = {h: section_pos(c2, h) for h in ["기준", "줄 판정"]}
check(M("8 CD 2차", "8 CD round 2"), M("橋口幸生", "Hashiguchi Yukio"), M("기준이 판정보다 앞", "Criteria come before verdicts"), 0 <= pos2["기준"] < pos2["줄 판정"])
ver2 = {r[0]: r for r in table(section(c2, "줄 판정")) if r and r[0] in pkey}
check(M("8 CD 2차", "8 CD round 2"), M("T&W 13단계(여러 라운드)", "T&W step 13 (several rounds)"), M("모든 줄을 판정", "Every line judged"), len(ver2) == len(pkey) > 0, f"{len(ver2)}/{len(pkey)}")
defended = [m for m, it in pkey.items() if it["src"] == "변론"]
dver = {r[0]: r for r in table(section(c2, "변론 판정")) if r and r[0] in pkey}
check(M("8 CD 2차", "8 CD round 2"), M("사례: 반대에 맞서 아이디어를 지킨 사람", "Cases: someone defended the idea against objections"), M("변론마다 판정", "Every defense ruled on"), all(m in dver for m in defended), M(f"변론 {len(defended)}건", f"defenses {len(defended)}"))
cands = [r for r in table(section(c2, "후보")) if len(r) >= 4 and r[1] in pkey]
check(M("8 CD 2차", "8 CD round 2"), M("AC재팬 40→10→3, Dye 15:1", "AC Japan 40→10→3, Dye 15:1"), M("후보 3~7줄", "3-7 shortlisted lines"), 3 <= len(cands) <= 7, M(f"{len(cands)}줄", f"{len(cands)} lines"))
check(M("8 CD 2차", "8 CD round 2"), "—", M("후보가 '남김' 판정 안에 있음", "Shortlist lines were marked HOLD"), all(ver2.get(r[1], ["", ""])[1] == "남김" for r in cands))

# 9. 광고주
cl = txt("09-client-review.md")
picks = [r for r in table(section(cl, "선택")) if len(r) >= 3]
cand_ids = {r[1] for r in cands}
check(M("9 광고주", "9 Client"), M("사례: 최종 선택에 광고주가 들어감", "Cases: the client takes part in the final pick"), M("최종 1줄", "Exactly one final line"), sum(1 for r in picks if r[0] == "최종") == 1)
check(M("9 광고주", "9 Client"), "—", M("고른 줄이 CD 후보 안에 있음", "Picked lines come from the shortlist"), all(r[1] in cand_ids for r in picks if r[1] in pkey))
check(M("9 광고주", "9 Client"), "regulation.md", M("사실·규제 검수 절", "Fact and regulation check section"), section(cl, "사실·규제 검수") is not None)

# 최종 파일
ver1_by_rid = {}
for r in kept_routes:
    ver1_by_rid[r[0]] = r[2]
SRC_EN = {"1차 생존": "survived round 1", "2차 재작업": "round 2 rework", "변론": "defense", "원자료 원문": "verbatim source"}
PICK_EN = {"최종": "Final", "대안": "Alternate"}
VERDICT_EN = {"받아들임": "accepted", "기각": "rejected"}
subject = re.search(r"(?:주제|Subject)[^:：\n]*[:：]\s*(.+)", cb)
out = [M("# 최종 — ", "# Final — ") + (subject.group(1).strip() if subject else run.name), ""]
out += [md_row(*(M("순서", "Rank"), M("헤드라인", "Headline"), M("팀·루트", "Team and route"), M("거쳐 온 길", "Path"), M("광고주가 고른 이유", "Client's reason"))), "|---|---|---|---|---|"]
cd2_reason = {r[1]: r[3] for r in cands}
for r in picks:
    rank = M(r[0], PICK_EN.get(r[0], r[0]))
    it = pkey.get(r[1])
    if not it:
        out.append(md_row(rank, r[2], "?", M("풀에 없는 줄", "not in the pool"), r[3] if len(r) > 3 else ""))
        continue
    src = M(it["src"], SRC_EN.get(it["src"], it["src"]))
    path = f"{src}" + (M(f" (변론: {dver[r[1]][1]})", f" (defense: {VERDICT_EN.get(dver[r[1]][1], dver[r[1]][1])})") if r[1] in dver else "")
    path += M(f" → CD 1차 루트 피드백: {ver1_by_rid.get(it['rid'], '-')} → CD 2차: {cd2_reason.get(r[1], '-')}",
              f" → CD round 1 route feedback: {ver1_by_rid.get(it['rid'], '-')} → CD round 2: {cd2_reason.get(r[1], '-')}")
    plain = key["routes"].get(it["rid"], {}).get("plain", "")
    team = it["team"] if LANG != "en" or it["team"] != "원자료" else "source"
    out.append(md_row(rank, it["text"], M(f"팀 {team} {it['route']}: {plain}", f"Team {team} {it['route']}: {plain}"), path, r[3] if len(r) > 3 else ""))


def mean(xs):
    return f"{statistics.mean(xs):.1f}" if xs else "-"


pool2_lens = [len(it["text"]) for it in pkey.values()]
cand_lens = [len(pkey[r[1]]["text"]) for r in cands]
pick_lens = [len(pkey[r[1]]["text"]) for r in picks if r[1] in pkey]
alive1 = sum(1 for r in ver1.values() if len(r) > 1 and r[1] == "살림")
rework = sum(1 for it in pkey.values() if it["src"] == "2차 재작업")
accepted = sum(1 for m in defended if dver.get(m, ["", ""])[1] == "받아들임")
out += ["", M("## 단계별 수", "## Counts by step"), "",
        M(f"- 1차 줄 {total1} → CD 1차 살림 {alive1} (루트 {len(kept_routes)}) → 재작업 {rework}줄, 변론 {len(defended)}건(받아들임 {accepted}) → 2차 풀 {len(pkey)} → CD 후보 {len(cands)} → 광고주 선택 {len(picks)}",
          f"- Round 1 lines {total1} → CD round 1 kept {alive1} (routes {len(kept_routes)}) → rework {rework} lines, defenses {len(defended)} (accepted {accepted}) → round 2 pool {len(pkey)} → CD shortlist {len(cands)} → client picks {len(picks)}"),
        "", M("## 길이 (CD의 길이 편향을 보는 기록. 판정에는 쓰지 않는다)", "## Length (a record for spotting CD length bias, not used in judging)"), "",
        M(f"- 평균 글자 수: 1차 전체 {mean(line_lens1)} / 2차 풀 {mean(pool2_lens)} / CD 후보 {mean(cand_lens)} / 광고주 선택 {mean(pick_lens)}",
          f"- Mean characters: round 1 {mean(line_lens1)} / round 2 pool {mean(pool2_lens)} / CD shortlist {mean(cand_lens)} / client picks {mean(pick_lens)}"), ""]
write(run / "10-final.md", "\n".join(out) + "\n")

bad = [c for c in checks if c[3] == M("어긋남", "MISSING")]
pc = [M("# 과정 점검", "# Process check"), "", M("> 단계마다 업계 흐름의 산출물이 있는지 본다. 그 단계가 잘 됐는지는 보지 않는다.", "> Checks that each step left the output the agency workflow expects. It does not judge whether the step was done well."), "",
      M(f"- 점검 {len(checks)}개, 어긋남 {len(bad)}개", f"- {len(checks)} checks, {len(bad)} missing"), "", md_row(M("단계", "Step"), M("업계 근거", "Industry basis"), M("점검", "Check"), M("결과", "Result"), M("메모", "Note")), "|---|---|---|---|---|"]
pc += [md_row(*c) for c in checks]
write(run / "10-process-check.md", "\n".join(pc) + "\n")
print(f"10-final.md, 10-process-check.md — 점검 {len(checks)}개 중 어긋남 {len(bad)}개")
for c in bad:
    print("  어긋남:", c[0], c[2], c[4])
