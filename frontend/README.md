# CredSaathi Frontend — Aarohi

Production-oriented React/TypeScript frontend foundation for CredSaathi. The UI follows the supplied CredSaathi Stitch design system and includes applicant and banker workspace routes, authentication UX, bilingual UI, scheme discovery, application tracking, document vault, financial views, loan scenario UI, AI assistant, notifications, settings/consent and API integration boundaries.

## Important integration rule

The frontend never owns authorization or official financial calculations. The backend is the source of truth. `src/services/api/client.ts` is the integration boundary; `src/services/mock/*` is clearly isolated demo data for UI development only.

## Run

From the `frontend` directory:

```bash
npm install
npm run dev
```

If Git Bash on Windows hangs on `npm`, use the Windows launcher:

```bash
"/c/Program Files/nodejs/npm.cmd" install
"/c/Program Files/nodejs/npm.cmd" run dev
```

## Build

```bash
npm run build
npm run lint
npm test
```

## Demo mode

Copy `.env.example` to `.env`. Keep `VITE_DEMO_MODE=true` while Kashvi/Uday APIs are not connected. When real endpoints are available, set `VITE_DEMO_MODE=false` and `VITE_API_BASE_URL` to the backend API.

Demo credentials are intentionally non-sensitive: any email/password combination works in demo mode. No real personal, financial or identity data should be entered.

## Route map

- `/` public landing
- `/login` login
- `/register` registration
- `/applicant/dashboard` applicant dashboard
- `/applicant/profile` profile
- `/applicant/loan-requirement` loan requirement
- `/applicant/financial-profile` financial profile
- `/applicant/schemes` scheme discovery
- `/applicant/schemes/:id` scheme details
- `/applicant/applications` applications
- `/applicant/applications/new` guided application
- `/applicant/applications/:id` application status
- `/applicant/documents` document vault
- `/applicant/financial` financial snapshot
- `/applicant/loan-scenario` loan scenario
- `/applicant/assistant` Saakshi assistant
- `/applicant/notifications` notifications
- `/applicant/settings` settings & consent
- `/banker/dashboard` banker dashboard
- `/banker/applications` banker applications
- `/banker/customers` customers
- `/banker/reports` reports

## Backend contract placeholders

The UI expects the eventual backend to expose versioned endpoints under `/api/v1`. No endpoint is silently invented as a production contract. The adapter currently documents the intended calls and falls back to isolated demo mode only when enabled.
