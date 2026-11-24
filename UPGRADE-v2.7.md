# CivilPrep v2.7 — Reliability Edition

This patch builds on the v2.6 Seasonal Update Edition. It leaves the question bank and its bank-version ID unchanged so existing history remains comparable. It adds quality checks, a public question-report draft, monitoring diagnostics, additional environmental-law references, an owner alert for unavailable CSC references, and a deployment validation gate. It does not claim that all 590 records have passed an editorial review. No paid API or account is needed to run these checks.

## Install on your existing GitHub repository

1. Complete and close any ongoing examination. Back up your repository (GitHub Code > Download ZIP) before replacing files. Keep the existing `.nojekyll`, `updates/status.json`, `questions.js`, `difficulty.js`, assets and other files. Do not clear browser storage.
2. Extract this patch. Upload the six files at its root (`index.html`, `seasonal.js`, `reliability.js`, `reliability.css`, `sw.js`, and `UPGRADE-v2.7.md`) to the root of the existing CivilPrep repository, preferably on a test branch. Upload the contents of `scripts/` to the existing `scripts/` folder. Upload `quality.json` inside `updates/` to that same folder. Do not accidentally put a second CivilPrep directory inside the repository.
3. Commit the application and scripts together before changing the workflow. The existing workflow may run on a main-branch commit; the new quality panel will remain unavailable until the updated workflow deploys its JSON feed. To avoid interim deployment, use a test branch and merge the complete change as one commit if comfortable with branches.
4. On GitHub, open `.github/workflows/civilprep-seasonal.yml`, click Edit, and replace all content with the provided `civilprep-seasonal.yml.txt` (the text file is a convenience copy, not a new repository file). Commit to main after all files are present. Keep Pages source set to GitHub Actions. Do not create a second deployment workflow.
5. On Actions, inspect the newest run. If needed, click Run workflow, select main, leave approve_cycle blank and acknowledgement unchecked. Check Validate question bank before update, Validate updated bank and write audit report, build and deploy. The monitor can report unavailable CSC sources even if deployment succeeds. If so, inspect updates/status.json for HTTP status and error type. No claim is made that CSC access has been restored until a live run confirms it.
6. Open https://jrmsnts64.github.io/CivilPrep/ and accept an available update or reload. Under Announcements, confirm Question quality checks. Answer a practice question and check Report a question. The report opens a public GitHub issue draft; the user submits it themselves. Enable GitHub Issues if necessary. Do not include personal details. Existing local browser storage is not intentionally changed by this patch, but browser data can be lost if storage is cleared.

## Verification completed locally

- 500 base questions, 100 per category, plus 90 Professional variants.
- 590 records checked for structural integrity and exact stem/choice duplicates, with symbols preserved during normalization.
- 130/130 current Numerical Skills records independently recalculated with exact rational arithmetic. Five fixed word-problem cases independently recomputed. This does not validate every explanation or every non-math answer.
- 31 repeated numerical-template groups flagged by a heuristic; other repetitive wording and topic gaps still need editorial review.
- Six distinct factual reference URLs present in all General Information records; link presence is not factual verification.
- Five local Python tests passed, covering structural checks, wrong answer rejection, duplicate rejection, simulated seasonal candidate generation, and failed source checks preserving previous status.
- JavaScript syntax checked. Isolated Chromium document with mocked status and browser storage displayed the audit panel and a question-report link at 390px, without page errors or horizontal overflow. Live network access and live GitHub deployment have not been tested with this patch.

## Next approved phases (not implemented in v2.7)

v2.8: Timed exam simulation, skip and revisit, flag questions, auto-submit, anti-repetition and adaptive selection.
v2.9: Topic/difficulty analytics, study heatmap, speed versus accuracy, readiness estimates and reports.
v3.0: Tabby animation states, achievements, optional gamification, accessibility and onboarding.
v3.1: Topic practice, spaced repetition, flashcards, formulas, personalized goals, regional alerts and calendar/reminders.
v3.2: Optional secure accounts, cloud sync, data export/deletion, authenticated admin dashboard, backups and audit logs. Guest mode remains supported. Verify service free-tier limits before provisioning; no secrets in the public repo.
v3.3: Android/PWA device tests, notification backend, release and security acceptance checks.
Commercial monetization is not part of this approved release. Review hosting terms and privacy requirements before adding payments or ads.
