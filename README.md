# ad-copy-agency-skill

Claude Code skill that writes ad headlines by following an ad agency workflow.

광고 대행사의 작업 흐름을 역할별 에이전트로 따라가 헤드라인을 만드는 Claude Code 스킬입니다. 클라이언트 브리프, 원자료 수집, 플래너의 과제 재정의, CD 서저리, 세 팀의 아이데이션, CD 리뷰 두 번과 재작업·변론, 광고주 선택과 사실·규제 검수 순서로 돕니다.

## 설치

스킬 이름은 `copy-masters`입니다(대가의 방식을 옮기던 v1~v4 때 붙인 이름을 그대로 씁니다).

이 폴더를 `~/.claude/skills/copy-masters/`(모든 프로젝트) 또는 프로젝트의 `.claude/skills/copy-masters/`에 둡니다. Claude Code에서 "광고 카피 써줘", "헤드라인 만들어줘" 같은 요청이나 `/copy-masters`로 부릅니다.

## 구성

- `SKILL.md`: 단계와 원칙, 알려진 한계
- `templates/`: 역할별 에이전트 프롬프트
- `scripts/`: 역할 사이에서 줄을 모으고 가리는 스크립트(`build_pool.py`), 최종본과 과정 점검을 만드는 스크립트(`assemble.py`)
- `references/`: 채널별 글자 수, 사실·규제 검수표

## 참고

SKILL.md와 템플릿이 설계 근거로 가리키는 `reports/`, `research_notes/`, `skill-tests/` 경로는 이 저장소에 들어 있지 않습니다. 스킬 실행에는 필요하지 않습니다.
