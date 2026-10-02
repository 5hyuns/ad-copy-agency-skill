# 실행 폴더의 마크다운 표를 읽고 쓰는 공통 함수. build_pool.py와 assemble.py가 쓴다.
import re, json, pathlib

TEAMS = ["A", "B", "C"]


def read(path):
    return pathlib.Path(path).read_text(encoding="utf-8")


def write(path, text):
    pathlib.Path(path).write_text(text, encoding="utf-8")


def section(text, title):
    """'## title'로 시작하는 절의 본문. 없으면 None."""
    m = re.search(rf"(?m)^## {re.escape(title)}\s*$", text)
    if not m:
        return None
    rest = text[m.end():]
    n = re.search(r"(?m)^## ", rest)
    return rest[:n.start()] if n else rest


def table(block):
    """마크다운 표의 데이터 행을 칸 목록으로. 머리줄과 구분줄은 뺀다."""
    if block is None:
        return []
    rows, seen_header = [], False
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if set(s) <= set("|-: "):
            continue
        if not seen_header:
            seen_header = True
            continue
        rows.append(cells)
    return rows


def load_json(path):
    return json.loads(read(path))


def save_json(path, obj):
    write(path, json.dumps(obj, ensure_ascii=False, indent=1))


def md_row(*cells):
    return "| " + " | ".join(str(c).replace("|", "/") for c in cells) + " |"
