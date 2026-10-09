# CredSaathi AI Layer API Contract Document

**Version**: `1.0.0`  
**Base URL**: `/api/v1/ai`  
**Contact / Owner**: CredSaathi AI Team (For Frontend Integration by Aarohi)

---

## 1. Overview & Authentication

The CredSaathi AI Gateway microservice exposes stateless endpoints for Scheme Matching, Document AI Extraction, Financial Summarization, RAG Assistant Queries, and Model Capabilities Inspection.

### Global Request Headers

| Header Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `X-API-Key` | String | Yes | API authentication key (or `Authorization: Bearer <token>`) |
| `X-Request-ID` | String | Optional | Correlation ID for end-to-end request tracing. If omitted, gateway generates a UUID v4. |
| `Content-Type` | String | Yes | `application/json` |

---

## 2. Unified Response Format (`ResponseEnvelope[T]`)

All API responses follow a standardized JSON envelope structure.

### Success Response Structure (`HTTP 200 OK`)
```json
{
  "success": true,
  "data": { ... },
  "model": {
    "provider": "mock-provider",
    "model": "mock-llm-v1",
    "version": "1.0.0"
  },
  "request_id": "req_8f93a10e7b",
  "errors": []
}
```

### Error Response Structure (`HTTP 400 / 401 / 403 / 429 / 502 / 504`)
```json
{
  "success": false,
  "data": null,
  "model": null,
  "request_id": "req_8f93a10e7b",
  "errors": [
    {
      "code": "UNAUTHORIZED",
      "message": "Unauthorized: Missing X-API-Key or Authorization header.",
      "field": null
    }
  ]
}
```

---

## 3. API Endpoints Specification

### 1. `POST /api/v1/ai/scheme-match`
Ranks and explains candidate financial/government schemes provided by backend.

**Request Payload Body (`SchemeMatchRequest`)**:
```json
{
  "applicant_context": {
    "applicant_id": "user_101",
    "category": "Women",
    "state": "Maharashtra",
    "income_annual": 350000.0,
    "purpose": "Micro business expansion"
  },
  "candidate_schemes": [
    {
      "scheme_id": "SCH_WOMEN_01",
      "scheme_name": "Stree Shakti Udyam Scheme",
      "category": "Women",
      "description": "Financial assistance for female business owners.",
      "eligibility_criteria": ["Female business owner", "Annual income < 5L"],
      "required_documents": ["Business Registration", "Income Certificate"]
    }
  ]
}
```

**Response Data Body (`SchemeMatchResponseData`)**:
```json
{
  "matches": [
    {
      "scheme_id": "SCH_WOMEN_01",
      "scheme_name": "Stree Shakti Udyam Scheme",
      "relevance_score": 0.95,
      "eligibility_status": "ELIGIBLE",
      "explanation": "High alignment for female entrepreneur with income under 5 Lakhs.",
      "match_reasons": ["Applicant category matches Women entrepreneur criteria."],
      "missing_fields": []
    }
  ]
}
```

---

### 2. `POST /api/v1/ai/extract-document`
Extracts, normalizes, and validates document fields from document text or raw OCR bytes.

**Request Payload Body (`DocumentExtractionRequest`)**:
```json
{
  "document_type": "PAN_CARD",
  "raw_text": "INCOME TAX DEPARTMENT GOVT OF INDIA PAN ABCDE1234F NAME RAMESH KUMAR"
}
```

**Response Data Body (`DocumentExtractionResponseData`)**:
```json
{
  "document_type": "PAN_CARD",
  "extracted_fields": {
    "pan_number": "ABCDE1234F",
    "name": "RAMESH KUMAR"
  },
  "confidence_score": 0.95,
  "validation_passed": true,
  "validation_messages": []
}
```

---

### 3. `POST /api/v1/ai/financial-explanation`
Generates grounded narrative summaries explaining applicant financial profile overview.

**Request Payload Body (`FinancialProfileInput`)**:
```json
{
  "applicant_id": "user_101",
  "annual_income": 600000.0,
  "monthly_liabilities": 15000.0
}
```

**Response Data Body (`FinancialSummaryResponseData`)**:
```json
{
  "summary": "Financial profile overview based on verified backend metrics.",
  "key_facts": ["Annual Income: 600000.0", "Monthly Liabilities: 15000.0"],
  "observations": ["Debt-to-income ratio is within healthy bounds."],
  "data_gaps": [],
  "preparation_guidance": ["Keep bank statement ready for submission."]
}
```

---

### 4. `POST /api/v1/ai/assistant/query`
Saakshi Applicant Assistant endpoint for grounded navigation, scheme FAQs, and status queries.

**Request Payload Body (`AssistantQueryRequest`)**:
```json
{
  "query": "What is the maximum loan limit under Mudra Tarun category?",
  "language": "en",
  "authenticated_user_id": "user_101"
}
```

**Response Data Body (`AssistantQueryResponseData`)**:
```json
{
  "answer": "Under PMMY Tarun category, loans from Rs 5 lakh up to Rs 10 lakh are sanctioned.",
  "citations": [
    {
      "citation_id": "[1]",
      "title": "Pradhan Mantri Mudra Yojana Guidelines",
      "source_url": "https://gov.in/mudra",
      "snippet": "Tarun category covers loans above 5 Lakhs up to 10 Lakhs."
    }
  ],
  "suggested_actions": ["View Mudra Scheme Details", "Apply Now"],
  "safety_flags": {
    "prompt_injection_detected": false,
    "unauthorized_access_attempt": false,
    "evidence_found": true
  },
  "disclaimer": "Saakshi is an informational assistant. Saakshi does not issue credit approvals, loan rejections, or credit scores."
}
```

---

### 5. `GET /api/v1/ai/models`
Returns list of registered foundation models and capabilities (zero secret credentials exposed).

---

### 6. `GET /api/v1/ai/health`
Returns AI microservice health status.

---

## 4. Error Code Summary Table

| HTTP Status | Error Code | Description |
| :--- | :--- | :--- |
| `400` | `INVALID_AI_INPUT` / `GUARDRAIL_VIOLATION` | Malformed request parameters or security guardrail violation |
| `401` | `UNAUTHORIZED` | Missing or invalid API key or bearer token |
| `403` | `AGENT_FIREWALL_VIOLATION` | Action blocked by Agent Firewall allowlist or scope checks |
| `429` | `RATE_LIMIT_EXCEEDED` | Exceeded 60 requests per minute limit |
| `502` | `MODEL_EXECUTION_ERROR` | Downstream AI provider connection failure |
| `504` | `OPERATION_TIMEOUT` | AI model or tool execution timeout |
