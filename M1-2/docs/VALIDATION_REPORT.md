# Validation Report

## Local code checks — 2026-10-26

| Check | Result |
|---|---|
| Backend tests | 14 passed; one existing Starlette deprecation warning |
| Frontend tests | 8 passed |
| JavaScript syntax | Passed |
| Frontend production build | Passed |
| Seed dry run | Generated 165 sample schedules; no database upload |
| FastAPI local smoke check | Health, API docs, and required routes responded successfully |
| Browser smoke check | CRUD, summary refresh, chat, conversation reload, error recovery, and mobile layout verified with a fake API |

The browser smoke check used a fake API and does not represent a production service check.

## Deployment status

| Target | Status |
|---|---|
| GitHub / Render source | Final code commit `b7c69a9` deployed successfully |
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
| Required API contracts | All 10 required method/path pairs present in deployed OpenAPI |
| Final frontend period | API analysis period displayed after reloading the deployed page |
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

## Final mission audit — 2026-10-26

Four concrete gaps were reproduced with failing tests and repaired without changing the required stack or architecture:

1. The summary card now displays the analysis period, including an empty-data state.
2. Invalid merged schedule updates return HTTP 422 rather than an unhandled validation error; the original row is preserved.
3. AI requests include `max_completion_tokens` (default 2048, configurable), and SDK errors become a readable 503 response without exposing provider details.
4. Conversation-load failure keeps existing messages and shows an error notice.

The entire backend suite, frontend suite, syntax checks, production build, and seed dry-run passed after these changes. The new token field and provider errors were tested with SDK MockTransport; the existing real AI conversation was reused rather than making another chargeable call. Runtime AI behavior under the new output cap was not separately exercised with a paid request.

Render deployed code commit `b7c69a9`; Vercel production deployment `dpl_4QqaoiHS2MeY72A16pAQdgcFsKua` reached READY and retained both approved production aliases. The final read-only checks confirmed health/docs/OpenAPI, 100+ saved schedules, Summary fields, correct API URL injection, and displayed analysis period. The README now maps the original mission to implementation and documents schema, calculations, context injection, setup, deployment, tests, demonstration steps, and limitations.

## Remaining manual checks and limits

- Complete the native schedule-delete confirmation in a normal browser using a disposable row. Do not delete existing demo rows just to test.
- Open the submission links once before entering them in the course submission form. Course submission itself has not been performed.
- The app is a shared demonstration without authentication/user isolation. Stored conversation history is restored in the UI but is not included in subsequent model context. Date-specific detail tools, Function Calling, and MCP/GPT Actions are outside the implemented optional scope.
