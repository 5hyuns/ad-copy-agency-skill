# ad-copy-agency-skill

**Language**: [한국어](README.md) | English · **Site**: https://5hyuns.github.io/ad-copy-agency-skill/

A Claude Code skill that writes ad headlines by following an ad agency's workflow with one agent per role. The skill is named `copy-masters`. Prompts and output are in Korean.

Ads are rarely one person writing one good sentence. A planner reframes the task, a creative director reviews the brief, several teams write many lines, the CD cuts them down more than once, and the client picks. The skill follows that order. Each role is a separate agent that sees only the files the previous step left behind. No human picks anything mid-run. At the end you get the chosen line, two alternates and a table checking that each step ran as the industry workflow expects.

> There is no evidence that it beats a single well-written prompt. Read [Limits](#limits) first.

## Quick start

```bash
# all projects (macOS, Linux, Git Bash)
git clone https://github.com/5hyuns/ad-copy-agency-skill.git ~/.claude/skills/copy-masters

# all projects (Windows PowerShell)
git clone https://github.com/5hyuns/ad-copy-agency-skill.git "$HOME\.claude\skills\copy-masters"

# one project only
git clone https://github.com/5hyuns/ad-copy-agency-skill.git .claude/skills/copy-masters
```

Open a new Claude Code session and call `/copy-masters` with the subject, business goal, target, mode (`퍼포먼스` performance or `브랜드` brand), channel (`SNS 피드`, `검색광고`, `상세·랜딩페이지` or `영상 스크립트`) and brand name. See the Korean README for a full example. It needs Python 3 (standard library only) and uses a web search tool when one is available.

## Steps

1. Client brief, written down as given
2. Raw material: product facts, what people actually wrote, competitor copy, verbatim with sources
3. Planner reframes the task and writes the creative brief
4. CD reviews the brief ("creative surgery"); the planner may revise once
5. Three creative teams, run in sequence; each later team is told which routes are already taken
6. CD round 1: criteria first, then a verdict on every line with team names hidden
7. Teams rework surviving routes; each team may defend one killed line
8. CD round 2: rules on defenses, picks about five candidates
9. Client: fact and regulation check, then one final line and two alternates
10. Final report and process check

Output goes to `copy-runs/<brand>/<date>-<topic>/` in your working directory.

## Demo

One run on a fictional smart pillow: [demo page](https://5hyuns.github.io/ad-copy-agency-skill/demo/) (Korean). It used 13 sub-agents, took about 20 minutes and about 1.04M sub-agent tokens.

## Limits

- Compared head to head with a single prompt given the same raw material, the skill's final lines won 0.37 of the time on average. Treat its output as no better than a single prompt.
- The reason to use it is the process: you can follow each step, and the brief check and client review catch factual errors a single prompt repeated, such as unsupported claims or edited customer quotes.
- The CD and the client are the same model. Re-running the same pool can change the final line.
- It produces headlines only, not visuals or body copy.
- Paths under `reports/`, `research_notes/` and `skill-tests/` cited in SKILL.md are not in this repository. They are design evidence and are not needed to run the skill.
