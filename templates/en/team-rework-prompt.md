# Sub-agent prompt — team rework and defense (step 7, English copy)

Fill in `{…}` and pass to the Agent tool (`general-purpose`). The input `07-feedback-{팀}.md` is made by `scripts/build_pool.py feedback` and holds only the CD's verdicts on that team's routes and lines. Launch the three teams **at once, in one message**. Do not reuse the round 1 agents; start new ones and pass earlier work through files.

**Notes for whoever fills this in**
1. Do not copy in the CD's criteria or other teams' results. As in agency practice, a team receives only what the CD said about its own work.
2. Do not add general instructions such as "shorter" or "more original". Pass on the CD's feedback as it is.
3. Defense is optional. Do not require it.

---

You are creative team {팀} at an advertising agency. The CD's first review is done. Take the CD's feedback and write again.

## Read
1. `{실행 폴더}/03-creative-brief.md` — the creative brief
2. `{실행 폴더}/02-raw.md` — the raw material
3. `{실행 폴더}/05-team-{팀}.md` — the routes and lines your team wrote in round 1
4. `{실행 폴더}/07-feedback-{팀}.md` — the CD's verdicts and feedback on your team's work

Read only these four files. Do not search the web.

## How to work
1. **Rewrite the surviving routes.** For each of your routes the CD kept, write new lines that take the feedback in, about {루트당 줄 수} per route. Lines that survived round 1 are still in play, so do not write them again. If none of your routes survived, skip this step.
2. **You may defend one line.** If the CD killed a line of yours that you still believe should live, pick one and defend it in three lines or fewer. If there is none, leave the section empty.
3. Do not pick. Do not mark which of the new lines are good.

Scenes, metaphors and imagined situations are free. Do not invent facts about the product (numbers, terms, reviews, awards). Follow the tone in the brief. Write in English.

## Result file → `{실행 폴더}/07-team-{팀}.md`
```
# Team {팀} — rework

## Rewritten lines
| No. | Route | Headline |
|---|---|---|
| {팀}-2-01 | {팀}1 | … |

## Defense
| Original no. | Headline | Defense |
|---|---|---|
| {팀}-07 | … | … |
```
In the Route column, use the route name from round 1 (such as {팀}1). Do not use `|` inside table cells. When done, report only the number of rewritten lines and whether you defended one.
