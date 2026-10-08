# CredSaathi — Transparent Credit & Scheme Discovery Platform

CredSaathi is a fintech platform designed for micro-entrepreneurs and applicants across India to discover relevant government and bank loan schemes, understand eligibility criteria, manage structured document vaults, simulate financial scenarios, and track credit application status transparently.

---

## Workspace Structure

- `frontend/`: Verified React + TypeScript + Vite web application built strictly matching the Stitch UI/UX design specifications.
- `backend/`: FastAPI + SQLAlchemy + Alembic core backend identity, organization, and credit data models.

---

## Frontend Architecture

The frontend is located under `frontend/` and provides:
- **Core Technology**: React 18, TypeScript, Vite, React Router DOM, React Hook Form, Zod validation, and Lucide React icons.
- **Design Tokens**: Standardized Deep Trust Navy (`#0B192C`), Emerald Forest (`#059669`), Canvas (`#F8FAFC`), Structural Border (`#E2E8F0`), Action Border (`#CBD5E1`), Muted (`#64748B`), and 8px base rhythm.
- **Dual Workspace**:
  1. **Applicant Workspace**: Scheme discovery, profile readiness, application creation, document vault, EMI scenario simulator, Saakshi AI Assistant (**Saakshi / साक्षी**), notifications, and explicit data consent controls.
  2. **Banker Workspace**: Organization-scoped dashboard, application review directory, customer management, operational pipeline reports, and multi-tenant security guardrails.

---

## Getting Started (Frontend)

```bash
cd frontend

# Install dependencies
npm install

# Run Vite development server (Demo Mode default)
npm run dev
```

### Environment Configuration

For isolated UI development and offline demonstration, enable Demo Mode:

```env
VITE_DEMO_MODE=true
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

- When `VITE_DEMO_MODE=true`, the application uses an isolated mock service layer (`src/services/mock/`).
- When `VITE_DEMO_MODE=false`, the application routes requests to live backend HTTP endpoints (`src/services/api/client.ts`).

---

## Quality & Build Verification

Run the following commands inside `frontend/` to verify compilation, linting, and tests:

```bash
# Production Build
npm run build

# ESLint Verification
npm run lint

# Vitest Test Suite
npm test -- --run
```