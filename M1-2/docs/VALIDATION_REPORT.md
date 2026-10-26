# Validation Report

## Local code checks — 2026-10-26

| Check | Result |
|---|---|
| Backend tests | 10 passed; one existing Starlette warning |
| Frontend tests | 6 passed |
| JavaScript syntax | Passed |
| Frontend production build | Passed |
| Seed dry run | Generated more than 100 sample schedules; no database upload |
| FastAPI local smoke check | Health, API docs, and required routes responded successfully |
| Browser smoke check | CRUD, summary refresh, chat, conversation reload, error recovery, and mobile layout verified with a fake API |

The browser smoke check used a fake API and does not represent a production service check.

## Deployment status

| Target | Status |
|---|---|
| GitHub | Render deployed source commit `684551e` |
| Backend deployment | Succeeded: https://myschedule-ai-api.onrender.com |
| Frontend deployment | READY: https://myschedule-ai.vercel.app |
| Swagger | HTTP 200: https://myschedule-ai-api.onrender.com/docs |
| Submission screenshots | Three production screenshots linked from README |

## Production read-only checks — 2026-10-26

| Check | Result |
|---|---|
| Render `/health`, `/docs`, `/openapi.json` | HTTP 200 |
| Vercel `/`, `/config.js`, `/app.js`, `/styles.css` | HTTP 200 without sign-in |
| Build-time API URL | Points to the deployed Render origin |
| Render instance | Free, Singapore; `/health` health check |
| CORS allowlist update | Approved by the user and applied through a Render redeploy |
| Both production Vercel origins | Preflight HTTP 200 with the matching allow-origin header |
| Unlisted origin | Preflight HTTP 400 without an allow-origin header |
| Production data workflow | UI create and reload; API update HTTP 200 and delete HTTP 204; temporary row absent afterward |
| Production AI | One real request to deployed `/api/chat`, HTTP 200; nonempty answer with numeric comparison |
| Conversation persistence | Detail endpoint HTTP 200, user/assistant messages and timestamps preserved |
| Conversation UI | Selected saved conversation and restored both messages after a page reload |
| Final verification tab console | No error entries |

## Evidence and verification scope

- [Summary and AI conversation](screenshots/chat-summary.jpg)
- [Schedule create/update result](screenshots/schedule-crud.jpg)
- [Conversation history selection](screenshots/conversation-history.jpg)

These screenshots were captured from the production site using generated demonstration data. The temporary schedule was removed; existing schedules and conversations were not edited or deleted. The newly created demonstration conversation remains available for reload.

The in-app browser stalled when automating the native schedule-deletion confirmation. The disposable schedule was deleted through the API, and the result was checked in a fresh browser page. The real AI request was made through the deployed API once, then its saved messages were restored through the production UI. A second real AI request was not sent solely to retest the browser submit button.
