export type Role = 'APPLICANT' | 'BANKER' | 'BANK_ADMIN' | 'CRED_SAATHI_ADMIN';
export type ApplicationStatus = 'DRAFT' | 'SUBMITTED' | 'UNDER_REVIEW' | 'ADDITIONAL_INFO_REQUIRED' | 'ACCEPTED' | 'REJECTED' | 'CLOSED';
export type DocumentStatus = 'UPLOADING' | 'PROCESSING' | 'VALID' | 'NEEDS_REVIEW' | 'FAILED';

export type NotificationCategory = 'ADDITIONAL_DOCUMENTS' | 'APPLICATION_TRANSMISSION' | 'DOCUMENT_UPLOAD_CONFIRMATION' | 'SCHEME_POLICY_INFO';

export interface NotificationItem {
  id: string;
  category: NotificationCategory;
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  actionUrl?: string;
  actionLabel?: string;
}

export interface ConsentArtifact {
  id: string;
  title: string;
  purpose: string;
  grantedAt: string;
  status: 'ACTIVE' | 'REVOKED' | 'EXPIRED';
  scope: string[];
}

export interface UserSettings {
  applicantName: string;
  entityName: string;
  udyamRegistrationNo: string;
  email: string;
  phone: string;
  verifiedCredentials: {
    identityVerified: boolean;
    businessVerified: boolean;
    financialsVerified: boolean;
  };
  consentLenderSharing: boolean;
  consentProductAnalytics: boolean;
  language: 'en' | 'hi';
  activeConsents: ConsentArtifact[];
}

export interface UserSession { 
  id: string; 
  name: string; 
  email: string; 
  role: Role; 
  organization?: string;
}

export interface Scheme { 
  id: string; 
  name: string; 
  purpose: string; 
  description: string; 
  matchLabel: string; 
  reasons: string[]; 
  documents: string[]; 
  source: string; 
  lastVerified: string; 
  status: string; 
}

export interface Application { 
  id: string; 
  customerName?: string;
  enterpriseName?: string;
  schemeName: string; 
  amountLabel: string; 
  submittedAt: string; 
  status: ApplicationStatus; 
  updatedAt: string; 
  documentsCount?: number;
  readinessScore?: string;
  authorizedOrganization?: string;
}

export interface BankerCustomer {
  id: string;
  name: string;
  enterpriseName: string;
  udyamNo: string;
  activeApplicationsCount: number;
  lastActivity: string;
  contactEmail: string;
  contactPhone: string;
  riskCategory: 'LOW' | 'MODERATE' | 'HIGH';
  verificationStatus: 'VERIFIED' | 'PENDING';
}

export interface BankerReportMetrics {
  totalSubmitted: number;
  underReview: number;
  additionalInfoRequired: number;
  closed: number;
  pipelineBreakdown: { label: string; percentage: string; count: number }[];
  authorizedOrganization: string;
  lastUpdated: string;
  disclaimer: string;
}

export interface DocumentItem { 
  id: string; 
  name: string; 
  type: string; 
  size: string; 
  status: DocumentStatus; 
  updatedAt: string; 
}

export interface FinancialSnapshot { 
  monthlyIncome: string; 
  monthlyExpenses: string; 
  existingDebt: string; 
  remainingCashFlow: string; 
  sourceNote: string;
  assets?: string;
  liabilities?: string;
  debtServiceCoverageRatio?: string;
  trendLabel?: string;
  verificationStatus?: 'VERIFIED' | 'UNVERIFIED' | 'SELF_DECLARED';
}

export interface LoanScenarioRequest {
  amount: number;
  tenureYears: number;
  interestRate?: number;
}

export interface AmortizationRow {
  year: number;
  principalPaid: string;
  interestPaid: string;
  balanceRemaining: string;
}

export interface LoanScenarioResponse {
  emiLabel: string;
  totalRepaymentLabel: string;
  totalInterestLabel: string;
  monthlyDebtObligationsLabel: string;
  remainingCashFlowPostEmiLabel: string;
  cashFlowImpactPercentage: string;
  interestRateApplied: string;
  amortizationBreakdown: AmortizationRow[];
  disclaimer: string;
}

export interface AssistantResponse {
  answer: string;
  sources?: string[];
  confidence?: string;
  humanReviewRequired?: boolean;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  sources?: string[];
  confidence?: string;
  humanReviewRequired?: boolean;
  error?: boolean;
}
