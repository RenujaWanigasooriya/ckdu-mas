# How to start this project in Claude Code

## 0. Recommended approach
Use a short `CLAUDE.md` for permanent rules (already in this folder) and give Claude Code your task as a
prompt in plan mode. Do not paste the whole project plan as the prompt. Claude Code reads `CLAUDE.md`
automatically at the start of every session, so keep it short (under 200 lines) and put the long plan in
`docs/project_plan.md`, which Claude reads only when needed.

## 1. Install Claude Code (needs a Claude subscription or Anthropic Console account)
- macOS, Linux or WSL:   `curl -fsSL https://claude.ai/install.sh | bash`
- Windows PowerShell:    `irm https://claude.ai/install.ps1 | iex`
- Then open a NEW terminal and check: `claude --version`
- Alternatives: the Claude desktop app (Code tab) or the VS Code extension. Same engine, same CLAUDE.md.
- Windows tip: for SPADE, WSL (Ubuntu) avoids most asyncio and path problems.

## 2. Open the project
```
cd ckdu-mas
git init
claude
```
Inside Claude Code run `/context` to confirm it loaded `CLAUDE.md`.

## 3. Prompt 1: plan first (press Shift+Tab until the bar shows "plan mode on")
```
Read CLAUDE.md, docs/project_plan.md and data/raw/README_data_sources.md.
Plan Phase 0 only: project scaffold plus a toy Contract Net demo.
Scope: virtual environment and requirements.txt, folder skeleton as in CLAUDE.md, a minimal
ontology.py, one ResourceCoordinatorAgent and three VillageAgents exchanging cfp, propose,
accept-proposal and reject-proposal over SPADE's built-in XMPP server, a message logger writing
logs/messages.csv, and a pytest for the bid function. Do not build the real risk model yet.
List the files you will create, the commands to run, and how we will verify it works.
```
Read the plan, edit it if needed, then approve.

## 4. Prompt 2: build it (after approving the plan, plan mode switches off)
```
Implement the Phase 0 plan. Install dependencies, pin versions in requirements.txt, run pytest,
start `spade run`, run the toy demo, and show me the logs/messages.csv output.
Update the Commands section of CLAUDE.md with the exact commands that worked.
Then commit with a clear message.
```

## 5. Later prompts (one phase per session, `/clear` between unrelated tasks)
1. Data loader and WQI function in src/core, tested against data/raw files. Ask me about any TO_FILL weight.
2. WellMonitorAgent and RiskScoringAgent reading data/processed/synthetic_wells.csv month by month.
3. VillageAgent bid function (need = risk x population / distance, my first draft) and tests.
4. Real Contract Net with scarce RO units and bowsers, plus equal-split and first-come baselines.
5. HotspotAgent using data/raw/ckdu_04 and ckdu_05 as sanity checks.
6. AlertAgent with tiered, non-alarmist messages.
7. Evaluation script: allocation efficiency vs baselines, message counts, negotiation rounds, alert latency.
8. Streamlit + Folium dashboard reading the logs.

## 6. Team tips
- Each person works on their own branch and their own Claude Code session. Commit CLAUDE.md so everyone shares the rules.
- Give Claude something to check against (pytest, the demo run). "Run the tests and fix failures" works much better than "make it work".
- If you correct Claude twice on the same thing, `/clear` and rewrite the prompt with what you learned.
- Use a fresh session to review code: "Review src/agents/ against CLAUDE.md rules. Report only real problems."
- Keep your own notes of real vs synthetic data for the report.

Docs: https://code.claude.com/docs/en/overview, https://code.claude.com/docs/en/best-practices
