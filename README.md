# ad-copy-agency-skill: AI copywriting that works like an ad agency

**Language**: English | [한국어](README.ko.md) · **Site**: https://5hyuns.github.io/ad-copy-agency-skill/

An open-source [Claude Code](https://claude.com/claude-code) plugin for AI ad copywriting. It writes advertising headlines by running a real ad agency workflow with one AI agent per role: planner, creative director, three creative teams and the client. The skill is named `copy-masters`.

Ads are rarely one person writing one good sentence. A planner reframes the brief, a creative director reviews it, several teams write a lot of lines, the CD cuts them down more than once, and the client picks. The skill follows that order. Each role is a separate agent that sees only the files the previous step left behind, teams never pick their own lines, and the CD judges lines with team names hidden. At the end you get a final headline, two alternates, the path each line took, and a table checking that every step ran as the agency workflow expects.

> **There is no evidence that it beats a single well-written prompt.** Read [Limits](#limits) first. It writes English copy for the US market and Korean copy for the Korean market.

![CD review sheet from an English run: lines kept and killed](docs/og.png)

## Quick start

Install it as a plugin, inside a Claude Code session:

```
/plugin marketplace add 5hyuns/ad-copy-agency-skill
/plugin install copy-masters@ad-copy-agency-skill
```

Start a new session (or run `/reload-plugins`) and the skill is `/copy-masters:copy-masters`. Update with `/plugin marketplace update ad-copy-agency-skill`.

If you would rather have the files in a skills folder, clone it instead. Keep the folder name `copy-masters`; then the skill is `/copy-masters` and you update with `git pull`.

```bash
# all projects (macOS, Linux, Git Bash)
git clone https://github.com/5hyuns/ad-copy-agency-skill.git ~/.claude/skills/copy-masters

# all projects (Windows PowerShell)
git clone https://github.com/5hyuns/ad-copy-agency-skill.git "$HOME\.claude\skills\copy-masters"

# one project only
git clone https://github.com/5hyuns/ad-copy-agency-skill.git .claude/skills/copy-masters
```

Call it like this. Set `Copy language: en` for English copy, because the default is Korean. The market then defaults to `us`, so the client checks against US channel specs and FTC rules.

```
/copy-masters:copy-masters
Subject: SlowBowl, a smart dog bowl that releases kibble in small portions when it notices a dog gulping
Business goal: more first orders from Instagram ads
Target: US dog owners, 25 to 45, whose dog eats too fast
Mode: performance
Channel: social feed
Brand: Tumbleweed Pets
Must-haves: not a veterinary medical device; no health claims
Your material: ./material.md
Copy language: en
```

You can also just ask for ad copy or headlines in plain words. If a required input is missing, it asks before starting.

Requirements: Claude Code and Python 3 (the helper scripts use only the standard library). Raw material collection uses a web search tool when available and falls back to the material you provide.

## Inputs

| Input | Required | Value |
|---|---|---|
| Subject | yes | What is being advertised |
| Business goal | yes | One short line, such as "more trial orders" |
| Target | yes | Who the ad speaks to |
| Mode | yes | `performance` (clicks, conversions) or `brand` (memory, attitude) |
| Channel | yes | `social feed`, `search ads`, `landing page` or `video script` |
| Brand | yes | Names the output folder and the learning log |
| Product truth | no | What the company itself says is the core of the product |
| Must-haves | no | What must or must not appear, tone rules |
| Industry | no | Adds industry-specific regulation checks |
| Your material | no | Decks, reviews, interviews. Approved customer quotes reach the shortlist verbatim |
| Copy language | no | `en` for English copy. Korean if not set |
| Market | no | `us` or `kr`: which country's channel specs and ad law the client checks against. Follows the copy language if not set |

It never guesses the mode, channel or target. Product numbers, conditions, reviews and certifications come only from the raw material or your files; anything unverified is flagged `[client to confirm: …]`.

## Workflow

| Step | Role | What happens | Output |
|---|---|---|---|
| 1 | Client brief | Inputs written down as given | `01-client-brief.md` |
| 2 | Raw material | Product facts, what people wrote, competitor copy, verbatim with sources | `02-raw.md` |
| 3 | Planner | Reframes the task as "what this ad must say" and writes the creative brief | `03-creative-brief.md` |
| 4 | Creative surgery | CD reviews the brief; the planner may revise once | `04-surgery.md` |
| 5 | Three teams | Run in sequence, 3 to 5 routes and 33 lines each; later teams avoid routes already taken | `05-team-*.md` |
| 6 | CD round 1 | Criteria first, then keep or kill on every line; 3 to 5 routes survive | `06-cd-review-1.md` |
| 7 | Rework and defense | Teams rewrite surviving routes and may defend one killed line | `07-team-*.md` |
| 8 | CD round 2 | Rules on defenses, shortlists about five lines | `08-cd-review-2.md` |
| 9 | Client | Fact and advertising-law check, then one final line and two alternates | `09-client-review.md` |
| 10 | Handoff | The path each line took and a process check table | `10-final.md`, `10-process-check.md` |

Outputs go to `copy-runs/<brand>/<date>-<topic>/` in your working directory. Running the same brand again surfaces lessons from `copy-runs/<brand>/learning-log.md` first.

## Example run

One English run on a fictional US smart dog bowl, with the inputs shown above. The planner changed the kind of problem: owners already know to slow their dog down, and every bowl they know does it with an obstacle in a full bowl. The CD sent the first brief back once. Three teams wrote 99 lines, the CD kept 13, the round 2 pool had 58, the CD shortlisted 6, and the client picked:

> Two of you listening at dinner. Only one of you can hold the kibble back.

Alternates: "He can't inhale what isn't in the bowl yet." and "He doesn't have to change. The bowl does."

A full line-by-line record with every CD verdict and reason is published for a Korean run on a fictional smart pillow: [demo page (Korean)](https://5hyuns.github.io/ad-copy-agency-skill/demo/). That run used 13 sub-agents, about 20 minutes and about 1.04M sub-agent tokens.

## Limits

- Compared head to head with a single prompt given the same raw material, the skill's final lines won 0.37 of the time on average. Treat its output as about as good as, or worse than, one well-written prompt.
- The reason to use it is the process. You can follow each step, and the brief check and client review catch factual errors a single prompt repeated across runs, such as unsupported claims or edited customer quotes.
- The CD and the client are the same model. Re-running the same pool can change the final line.
- **English copy has been tested once.** On one fictional US product the English run worked end to end (all 46 process checks, every verdict parsed), but its three picks won 0.39 of blind comparisons against two single-prompt runs. The client's longest pick lost every pair while one of its alternates was the second strongest line. That number leans on one client pick: given the same shortlist nine more times, the client chose the 43-character alternate every time, and that line scored 0.67 against the single-prompt lines. Lines get longer at team rework (41.8 characters for round-1 survivors, 58.5 for rewrites), not at the CD's shortlist. The US regulation checklist did its job: the client dropped a customer quote under the FTC's typical-results rule (16 CFR 255.2).
- It writes headlines only. Visuals, subheads and body copy are out of scope.
- The full list of known limits is in [SKILL.md](SKILL.md), which is written in Korean. Paths under `reports/`, `research_notes/` and `skill-tests/` cited there are design evidence kept outside this repository and are not needed to run the skill.

## Repository layout

- `.claude-plugin/`: plugin and marketplace manifests
- `SKILL.md`: steps, principles and known limits
- `templates/common/`: collection, planner and creative surgery prompts, shared by both languages
- `templates/en/`, `templates/ko/`: team, CD and client prompts, written separately for each language rather than translated
- `scripts/`: `build_pool.py` moves and hides lines between roles, `assemble.py` builds the final report and process check
- `references/us/`, `references/kr/`: channel specs and the fact and regulation checklist for each market (US: FTC Act Section 5, deception and substantiation statements, 16 CFR 255 and 465, FDA general wellness)
- `docs/`: the project site and demo page (GitHub Pages)

## License

MIT. See [LICENSE](LICENSE).

## Background

The name copy-masters comes from versions 1 to 4, which imitated the methods of famous copywriters (David Ogilvy, Bill Bernbach, Taniyama Masakazu, Jung Chul). Version 5 dropped that design and follows the agency workflow instead. The design draws on production records of 25 well-known campaigns and on Turnbull & Wheeler's research on London advertising agencies, where only two of 24 steps produced ideas and the rest were about agreeing on the problem and checking the work.

Related keywords: AI copywriting, ad copy generator, headline generator, Claude Code plugin, Claude skills, multi-agent workflow, creative brief, advertising agency.
