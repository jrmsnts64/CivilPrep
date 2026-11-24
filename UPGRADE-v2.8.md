# CivilPrep v2.8 — Smart Examination Edition

## Updating from v2.7.1 on GitHub
Finish your current review first. Back up the repository, and check that questions.js and difficulty.js match the package before doing a full replacement. If the live bank has changed, retain the live bank and use the quick patch instead. Keep the existing updates/status.json and any updates/candidates.json, and do not delete .github or .nojekyll.

For the GitHub browser upload, extract the quick patch and upload its four root files together: index.html, sw.js, smart-exam.js, smart-exam.css. The existing v2.7.1 seasonal workflow already copies all root JS/CSS files. No workflow edit is needed for this feature update. Commit once. Check Actions for successful Build and Deploy, then reopen CivilPrep and install the app update if offered. Keep all original questions, user browser storage and monitoring data.

For the optional new CI logic tests, upload scripts/test_smart_exam.cjs into scripts first, then edit the existing .github/workflows/civilprep-seasonal.yml to match the packaged workflow. The complete package also includes an optional Windows updater for a cloned repo; it refuses to copy if the bank differs and preserves status and candidates. Do not upload UPDATE-CIVILPREP.cmd to the live repository.

## Features
- Practice: answer selection stays editable until Next question. Feedback appears after confirmation. Optional smart practice uses recent performance to adjust the difficulty mix (after 10 attempts), favors weaker categories and reduces recent repeats. Default editorial distributions remain unchanged; actual counts depend on available questions.
- Mock: selectable time limit, up to 150 or 165 mixed items, previous/next, skip, jump to item, flag, answer changes until final submission. Time limit defaults to one minute per actual item. Counts and timing are custom practice settings, not official CSC specifications.
- Mock answers are stored locally until submission. No correctness feedback until submission. Unanswered items are scored incorrect. The timer continues based on a stored deadline, including while the page is closed. When reopened after expiration, the app submits automatically. No background operation while the browser is closed. Local system clock changes may affect timing. No proctoring.
- Existing draft version 2/3 remains compatible; legacy mock drafts finish using the old sequential behavior. New drafts use version 4. Per-question timing for revisitable mock exams is not recorded, so speed KPIs show unavailable for those sessions. Existing practice timing is unchanged.

## Tests
Run `python scripts/test_reliability.py` and `node scripts/test_smart_exam.cjs`. Simulated Chromium tests cover reselection and scoring, practice reload, mock flags and navigation, draft recovery, timeout and unanswered scoring, adaptive sampling and mobile width. Live deployment and device tests remain required.

## Next phases
v2.9 advanced analytics, v3.0 Tabby and gamification/accessibility, v3.1 personalized learning and reminders, v3.2 optional cloud and secure admin, v3.3 mobile release. Cloud services require a separate secure backend and provider setup. No paid service is required for v2.8.
