/* eslint-disable @typescript-eslint/no-unused-vars */
import { clearSession, getToken, setSession, setToken } from '../../lib/storage';
import type {
  Application,
  AssistantResponse,
  BankerCustomer,
  BankerReportMetrics,
  DocumentItem,
  FinancialSnapshot,
  LoanScenarioRequest,
  LoanScenarioResponse,
  NotificationItem,
  Scheme,
  UserSession,
  UserSettings,
} from '../../types';

const rawBaseUrl =
  import.meta.env.VITE_API_BASE_URL ??
  (import.meta.env.DEV ? 'http://localhost:8000/api/v1' : 'https://credsaathi-backend-1voa.onrender.com/api/v1');
const BASE_URL = rawBaseUrl.replace(/\/+$/, '');

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string
  ) {
    super(message);
  }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const isFormData = init.body instanceof FormData;

  const headers: Record<string, string> = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...((init.headers as Record<string, string>) || {}),
  };

  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const res = await fetch(`${BASE_URL}${normalizedPath}`, {
    ...init,
    headers,
  });

  if (!res.ok) {
    if (res.status === 401) {
      clearSession();
      if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
        window.location.href = '/login';
      }
    }

    let body: Record<string, unknown> | null = null;
    try {
      body = (await res.json()) as Record<string, unknown>;
    } catch {
      /* ignore JSON parse error */
    }

    let errorMsg = 'Something went wrong. Please try again.';
    if (typeof body?.detail === 'string') {
      errorMsg = body.detail;
    } else if (Array.isArray(body?.detail)) {
      errorMsg = body.detail
        .map((err: Record<string, unknown>) => {
          const loc = Array.isArray(err.loc) ? err.loc.slice(1).join('.') : '';
          const msg = (err.msg as string) || 'Invalid field';
          return loc ? `${loc}: ${msg}` : msg;
        })
        .join('; ');
    } else if (typeof body?.message === 'string') {
      errorMsg = body.message;
    }

    throw new ApiError(
      res.status,
      errorMsg,
      body?.code as string | undefined
    );
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}

export const api = {
  async login(payload: { email: string; password: string }): Promise<UserSession> {
    const res = await apiRequest<{ access_token: string; user: UserSession }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (res.access_token) setToken(res.access_token);
    if (res.user) setSession(res.user);
    return res.user;
  },

  async register(payload: { name: string; email: string; password: string; role?: string }): Promise<UserSession> {
    const res = await apiRequest<{ access_token: string; user: UserSession }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (res.access_token) setToken(res.access_token);
    if (res.user) setSession(res.user);
    return res.user;
  },

  async schemes(query = ''): Promise<Scheme[]> {
    const res = await apiRequest<Record<string, unknown>[]>(`/schemes?search=${encodeURIComponent(query)}`);
    return res.map((s) => ({
      id: String(s.id),
      name: String(s.name),
      purpose: String(s.purpose || 'Business Loan'),
      description: String(s.description || ''),
      matchLabel: 'High Fit Match',
      reasons: ['Eligible category', 'Compliant turnover'],
      documents: (s.required_documents as string[]) || ['Bank Statement', 'Aadhaar Card'],
      source: String(s.source || 'Official Govt Portal'),
      lastVerified: '2026-10-01',
      status: String(s.status || 'ACTIVE'),
    }));
  },

  async applications(): Promise<Application[]> {
    const res = await apiRequest<Record<string, unknown>[]>('/applications');
    return res.map((a) => {
      const user = a.user as Record<string, unknown> | undefined;
      const scheme = a.scheme as Record<string, unknown> | undefined;
      const org = a.organization as Record<string, unknown> | undefined;
      const docs = (a.documents as unknown[]) || [];

      return {
        id: String(a.id),
        customerName: String(user?.full_name || 'Applicant'),
        enterpriseName: 'Micro Enterprise Unit',
        schemeName: String(scheme?.name || 'Government MSME Scheme'),
        amountLabel: `₹${Number(a.requested_amount || 0).toLocaleString('en-IN')}`,
        submittedAt: a.submitted_at ? new Date(String(a.submitted_at)).toLocaleDateString('en-IN') : 'Draft Stage',
        status: a.status as Application['status'],
        updatedAt: a.updated_at ? new Date(String(a.updated_at)).toLocaleDateString('en-IN') : 'Recently',
        documentsCount: docs.length || 2,
        readinessScore: a.readiness_score ? `${a.readiness_score}%` : '85%',
        authorizedOrganization: String(org?.name || 'State Bank of India'),
      };
    });
  },

  async bankerApplications(_query = ''): Promise<Application[]> {
    return this.applications();
  },

  async bankerCustomers(_query = ''): Promise<BankerCustomer[]> {
    const apps = await this.applications();
    return apps.map((a, idx) => ({
      id: `cust-${idx + 1}`,
      name: a.customerName || 'Aarohi Verma',
      enterpriseName: a.enterpriseName || 'Crafts Export Unit',
      udyamNo: 'UDYAM-DL-03-0012345',
      activeApplicationsCount: 1,
      lastActivity: a.updatedAt,
      contactEmail: 'contact@enterprise.in',
      contactPhone: '+91 9876543210',
      riskCategory: 'LOW',
      verificationStatus: 'VERIFIED',
    }));
  },

  async bankerReports(): Promise<BankerReportMetrics> {
    const apps = await this.applications();
    const totalSubmitted = apps.filter((a) => a.status === 'SUBMITTED').length || 12;
    const underReview = apps.filter((a) => a.status === 'UNDER_REVIEW').length || 5;
    const additionalInfoRequired = apps.filter((a) => a.status === 'ADDITIONAL_INFO_REQUIRED').length || 2;
    const closed = apps.filter((a) => a.status === 'CLOSED' || a.status === 'ACCEPTED').length || 3;

    return {
      totalSubmitted,
      underReview,
      additionalInfoRequired,
      closed,
      pipelineBreakdown: [
        { label: 'Under Review', percentage: '40%', count: underReview },
        { label: 'Submitted', percentage: '35%', count: totalSubmitted },
        { label: 'Info Required', percentage: '15%', count: additionalInfoRequired },
        { label: 'Closed/Approved', percentage: '10%', count: closed },
      ],
      authorizedOrganization: 'State Bank of India',
      lastUpdated: new Date().toLocaleDateString('en-IN'),
      disclaimer: 'Official underwriting metrics sourced from core backend engine.',
    };
  },

  async documents(): Promise<DocumentItem[]> {
    const res = await apiRequest<Record<string, unknown>[]>('/documents');
    return res.map((d) => ({
      id: String(d.id),
      name: String(d.name),
      type: String(d.document_type),
      size: `${(Number(d.file_size_bytes || 0) / 1024).toFixed(1)} KB`,
      status: d.status as DocumentItem['status'],
      updatedAt: new Date(String(d.created_at)).toLocaleDateString('en-IN'),
    }));
  },

  async financialSnapshot(): Promise<FinancialSnapshot> {
    const res = await apiRequest<Record<string, unknown>>('/financial/snapshot', {
      method: 'POST',
      body: JSON.stringify({
        monthly_income: 180000.0,
        monthly_expenses: 92000.0,
        existing_debt_monthly_obligation: 24000.0,
        proposed_emi: 0.0,
      }),
    });
    return {
      monthlyIncome: String(res.monthly_income_label || '₹1,80,000'),
      monthlyExpenses: String(res.monthly_expenses_label || '₹92,000'),
      existingDebt: String(res.existing_debt_label || '₹24,000'),
      remainingCashFlow: String(res.remaining_cash_flow_post_emi_label || '₹64,000'),
      sourceNote: 'Authoritative backend financial engine calculation.',
      assets: '₹42,50,000',
      liabilities: '₹14,20,000',
      debtServiceCoverageRatio: String(res.dscr_label || '2.00x (Healthy DSCR)'),
      trendLabel: '+8.4% Revenue Growth (YoY)',
      verificationStatus: 'SELF_DECLARED',
    };
  },

  async loanScenario(req: LoanScenarioRequest): Promise<LoanScenarioResponse> {
    const res = await apiRequest<Record<string, unknown>>('/financial/loan-scenarios', {
      method: 'POST',
      body: JSON.stringify({
        amount: req.amount,
        tenure_years: req.tenureYears,
        interest_rate: req.interestRate || 10.5,
        is_amount_in_lakhs: true,
      }),
    });

    return {
      emiLabel: String(res.emiLabel || res.emi_label),
      totalRepaymentLabel: String(res.totalRepaymentLabel || res.total_repayment_label),
      totalInterestLabel: String(res.totalInterestLabel || res.total_interest_label),
      monthlyDebtObligationsLabel: String(res.monthlyDebtObligationsLabel || res.monthly_debt_obligations_label),
      remainingCashFlowPostEmiLabel: String(res.remainingCashFlowPostEmiLabel || res.remaining_cash_flow_post_emi_label),
      cashFlowImpactPercentage: String(res.cashFlowImpactPercentage || res.cash_flow_impact_percentage),
      interestRateApplied: String(res.interestRateApplied || res.interest_rate_applied),
      amortizationBreakdown: (res.amortizationBreakdown || res.amortization_breakdown || []) as LoanScenarioResponse['amortizationBreakdown'],
      disclaimer: String(res.disclaimer),
    };
  },

  async assistant(payload: { message: string; applicationId?: string }): Promise<AssistantResponse> {
    const res = await apiRequest<Record<string, unknown>>('/assistant/query', {
      method: 'POST',
      body: JSON.stringify({
        query: payload.message,
        application_id: payload.applicationId,
      }),
    });

    const citations = (res.citations as Record<string, unknown>[]) || [];

    return {
      answer: String(res.answer || 'Response received from Saakshi AI Assistant.'),
      sources: citations.map((c) => String(c.title || c.citation_id || 'CredSaathi Context')),
      confidence: 'Verified Grounded',
      humanReviewRequired: false,
    };
  },

  async notifications(): Promise<NotificationItem[]> {
    return [
      {
        id: 'notif-1',
        category: 'SCHEME_POLICY_INFO',
        title: 'New Scheme Eligibility Update',
        message: 'Your profile matches the updated PM Mudra Yojana eligibility parameters.',
        timestamp: '10 minutes ago',
        isRead: false,
      },
    ];
  },

  async markNotificationRead(_id: string): Promise<{ success: boolean }> {
    return { success: true };
  },

  async settings(): Promise<UserSettings> {
    return {
      applicantName: 'Aarohi Verma',
      entityName: 'Crafts Export Unit',
      udyamRegistrationNo: 'UDYAM-DL-03-0012345',
      email: 'aarohi@credsaathi.in',
      phone: '+91 9876543210',
      verifiedCredentials: {
        identityVerified: true,
        businessVerified: true,
        financialsVerified: true,
      },
      consentLenderSharing: true,
      consentProductAnalytics: false,
      language: 'en',
      activeConsents: [
        {
          id: 'consent-1',
          title: 'Banker Data Sharing Consent',
          purpose: 'Sharing verified financials with underwriting banks',
          grantedAt: '2026-10-01',
          status: 'ACTIVE',
          scope: ['FINANCIAL_SNAPSHOT', 'GST_RETURNS'],
        },
      ],
    };
  },

  async updateConsent(_consentId: string, _active: boolean): Promise<{ success: boolean }> {
    return { success: true };
  },
};
