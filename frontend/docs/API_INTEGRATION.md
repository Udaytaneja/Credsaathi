# API integration notes

Frontend integration boundary is `src/services/api/client.ts`.

Expected versioned areas: `/auth`, `/users`, `/applicants`, `/organizations`, `/banks`, `/schemes`, `/applications`, `/documents`, `/financial`, `/consents`, `/audit`, `/notifications`, `/ai`.

The frontend does not invent application state transitions or perform official financial calculations. Replace demo adapters only after Kashvi/Uday provide the final request/response schemas.

AI assistant target: `POST /api/v1/ai/assistant/query`. Scheme matching target: `POST /api/v1/ai/scheme-match`. Document extraction target: `POST /api/v1/ai/extract-document`. Financial explanation target: `POST /api/v1/ai/financial-explanation`.
