# 실행 폴더의 마크다운 표를 읽고 쓰는 공통 함수. build_pool.py와 assemble.py가 쓴다.
# 스크립트 안쪽은 한국어 정본 이름만 다룬다. 영어 템플릿이 쓴 절 제목과 판정어는 읽을 때 정본으로 맞춘다.
import re, json, pathlib

TEAMS = ["A", "B", "C"]

# 정본(한국어) 절 제목 → 영어 템플릿이 쓰는 이름
SECTION_EN = {
    # 05 팀, 07 재작업
    "루트": "Routes", "줄": "Lines", "다시 쓴 줄": "Rewritten lines", "변론": "Defense",
    # 06·08 CD
    "기준": "Criteria", "관점 묶음": "Viewpoint groups", "살린 루트": "Kept routes", "줄 판정": "Line verdicts",
    "변론 판정": "Defense verdicts", "후보": "Shortlist",
    # 08 고객의 말, 09 광고주
    "고객의 말": "Customer quotes", "사실·규제 검수": "Fact and regulation check", "선택": "Selection",
    # 03 브리프, 04 서저리
    "받은 과제": "Task as given", "다시 정의한 과제": "Reframed task", "누구에게": "Who",
    "바라는 반응": "Desired response", "단일 제안": "Single-minded proposition",
    "날것 그대로의 재료": "Raw material", "믿을 이유": "Reasons to believe",
    "경쟁이 이미 하는 말": "What competitors already say", "톤": "Tone", "필수 사항": "Mandatories",
    "택하지 않은 재정의": "Reframe not taken", "새로 찾은 것": "New findings", "고친 것": "Changes",
    "판정": "Verdict", "이유": "Reasons", "플래너에게": "To the planner",
}

# 정본(한국어) 판정어 → 영어. 표의 칸이 통째로 이 말이면 읽을 때 정본으로 바꾼다.
WORD_EN = {
    "살림": "KEEP", "죽임": "KILL", "남김": "HOLD", "뺌": "DROP", "받아들임": "ACCEPT", "기각": "REJECT",
    "최종": "FINAL", "대안": "ALTERNATE", "통과": "PASS", "돌려보냄": "RETURN", "(없음)": "(none)",
}
_WORD_KO = {v.lower(): k for k, v in WORD_EN.items()}


def read(path):
    return pathlib.Path(path).read_text(encoding="utf-8")


def write(path, text):
    pathlib.Path(path).write_text(text, encoding="utf-8")


def canon(word):
    """영어 판정어를 정본으로. 다른 말은 그대로."""
    return _WORD_KO.get(word.strip().lower(), word)


def section_pos(text, title):
    """'## title' 줄의 위치(정본 이름이나 영어 이름, 뒤에 괄호 설명이 붙어도 된다). 없으면 -1."""
    names = [title] + ([SECTION_EN[title]] if title in SECTION_EN else [])
    for name in names:
        m = re.search(rf"(?mi)^## {re.escape(name)}(\s*\(.*\))?\s*$", text)
        if m:
            return m.start()
    return -1


def section(text, title):
    """'## title'로 시작하는 절의 본문. 없으면 None."""
    pos = section_pos(text, title)
    if pos < 0:
        return None
    rest = text[pos:].split("\n", 1)[1] if "\n" in text[pos:] else ""
    n = re.search(r"(?m)^## ", rest)
    return rest[:n.start()] if n else rest


def table(block):
    """마크다운 표의 데이터 행을 칸 목록으로. 머리줄과 구분줄은 뺀다. 영어 판정어는 정본으로 바꾼다."""
    if block is None:
        return []
    rows, seen_header = [], False
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [canon(c.strip()) for c in s.strip("|").split("|")]
        if set(s) <= set("|-: "):
            continue
        if not seen_header:
            seen_header = True
            continue
        rows.append(cells)
    return rows


def lang(run):
    """01-client-brief.md의 카피 언어. 적혀 있지 않으면 한국어."""
    p = pathlib.Path(run) / "01-client-brief.md"
    if p.exists():
        m = re.search(r"(?m)^- *(카피 언어|Copy language)[^:：\n]*[:：]\s*(\S+)", read(p))
        if m and re.match(r"(?i)en|영어|english", m.group(2)):
            return "en"
    return "ko"


def load_json(path):
    return json.loads(read(path))


def save_json(path, obj):
    write(path, json.dumps(obj, ensure_ascii=False, indent=1))


def md_row(*cells):
    return "| " + " | ".join(str(c).replace("|", "/") for c in cells) + " |"
